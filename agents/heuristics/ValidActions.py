from typing import List, Tuple, Dict
import numpy as np
import time

from agents.heuristics.Distance import Distance
from agents.Hyperparameters import Params_ValidActions, Params_Automat

from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Occupant import Occupant


# TODO:
#  besser food chasen -> valide Actions auf Food anpassen


def get_valid_neighbour_values(x: int, y: int, square: np.ndarray) -> List[int]:
    neighbour_fields = []

    if x + 1 < square.shape[0]:
        neighbour_fields.append(square[x + 1][y])
    if x - 1 >= 0:
        neighbour_fields.append(square[x - 1][y])
    if y + 1 < square.shape[1]:
        neighbour_fields.append(square[x][y + 1])
    if y - 1 >= 0:
        neighbour_fields.append(square[x][y - 1])

    return neighbour_fields


def get_valid_neigbours(x: int, y: int, square: np.ndarray) -> List[Tuple[int, int]]:
    neighbour_fields = []

    if x + 1 < square.shape[0]:
        neighbour_fields.append((x + 1, y))
    if x - 1 >= 0:
        neighbour_fields.append((x - 1, y))
    if y + 1 < square.shape[1]:
        neighbour_fields.append((x, y + 1))
    if y - 1 >= 0:
        neighbour_fields.append((x, y - 1))

    return neighbour_fields


class ValidActions:

    def __init__(self,
                 board: BoardState,
                 grid_map: GridMap,
                 me: Snake
                 ):

        self.depth = Params_ValidActions.DEPTH
        self.board = board
        self.snakes = board.snakes
        self.grid_map = grid_map
        self.my_snake = me
        self.valid_board = np.zeros((self.board.width, self.board.height))
        self.valid_actions = []
        self.direction_depth = {}
        self.hungry = False

    @staticmethod
    def get_valid_actions(board: BoardState,
                          possible_actions: List[Direction],
                          snakes: List[Snake],
                          my_snake: Snake,
                          grid_map: GridMap[Occupant],
                          avoid_food: bool) -> List[Direction]:

        my_head = my_snake.get_head()
        snake_tails = []
        val_actions = []
        forbidden_fields = []

        for snake in snakes:
            if snake.snake_id != my_snake.snake_id:
                for direc in snake.possible_actions():
                    enemy_head = snake.get_head()
                    forbidden_fields.append(enemy_head.advanced(direc))
            if snake.health == 100:
                continue
            snake_tails.append(snake.get_tail())

        for direction in possible_actions:
            next_position = my_head.advanced(direction)

            # avoid eating
            if my_snake.health > Params_ValidActions.FOOD_BOUNDARY and avoid_food:
                if grid_map.get_value_at_position(next_position) is Occupant.Food:
                    continue

            # outofbounds
            if board.is_out_of_bounds(next_position):
                continue

            # body crash -> ganze Gegner Schlange minus letzten Teil
            if grid_map.get_value_at_position(next_position) is Occupant.Snake and next_position not in snake_tails:
                continue

            # if next_position in forbidden_fields:
            #    continue

            val_actions.append(direction)

        if not val_actions:
            for direction in possible_actions:
                next_position = my_head.advanced(direction)
                # eat if its the only possible valid action
                if grid_map.get_value_at_position(next_position) is Occupant.Food:
                    val_actions.append(direction)

        return val_actions

    def _action_flood_fill(self, flood_queue: List, step: int, visited: List, action_plan: np.ndarray, enemy: bool):
        x_size, y_size = (self.board.width, self.board.height)
        new_queue = []
        for (x, y) in flood_queue:

            if (x, y) in visited:
                continue

            if enemy:
                if self.valid_board[x][y] + step < 0:
                    continue

                if self.valid_board[x][y] == 0 or step <= abs(self.valid_board[x][y]):
                    self.valid_board[x][y] = step
                action_plan[x][y] = Params_ValidActions.AREA_VALUE

            if not enemy:

                neighbour_values = get_valid_neighbour_values(x, y, self.valid_board)

                if step < self.valid_board[x][y] < 10 or self.valid_board[x][y] == 0:
                    self.valid_board[x][y] = -step
                
                # eigenenes Schwanzende berücksichtigen
                if 10 < self.valid_board[x, y] < 20 and self.valid_board[x, y] % 10 <= step:
                    # and -(step - 1) in neighbour_values:
                    self.valid_board[x][y] = -step

                # Schwanzanfang berücksichtigen
                if step == 1:
                    for snake in self.board.snakes:
                        tail = snake.get_tail()
                        if snake.health != 100 and (x, y) == (tail.x, tail.y):
                            self.valid_board[x][y] = -step

            visited.append((x, y))

            # add next steps to queue
            if x > 0 and (x - 1, y) not in visited:
                new_queue.append((x - 1, y))
            if x < (x_size - 1) and (x + 1, y) not in visited:
                new_queue.append((x + 1, y))
            if y > 0 and (x, y - 1) not in visited:
                new_queue.append((x, y - 1))
            if y < (y_size - 1) and (x, y + 1) not in visited:
                new_queue.append((x, y + 1))

        return new_queue, visited, action_plan

    def _mark_snakes(self, help_board: np.ndarray) -> None:
        # mark enemy snakes
        for snake in self.board.snakes:
            if snake.snake_id != self.my_snake.snake_id:
                for index, position in enumerate(snake.body[::-1]):
                    self.valid_board[position.x][position.y] = (index + 21)
                    help_board[position.x][position.y] = (index + 21)

        # mark my snake on board
        for index, position in enumerate(self.my_snake.body[::-1]):
            self.valid_board[position.x][position.y] = (index + 11)
            help_board[position.x][position.y] = (index + 11)

    def _expand(self, my_head: Position) -> Tuple[List[Direction], Dict]:
        invalid_actions = []
        longest_way = {}

        for direction in self.valid_actions:

            step_history = []
            dead_ends = {}
            searching = True
            value = -1
            dead = False
            longest_way[direction] = 0

            # get first field of Direction and check if valid
            next_position = my_head.advanced(direction)
            if self.valid_board[next_position.x][next_position.y] != value:
                continue
            step_history.append((next_position.x, next_position.y))
            x_coord, y_coord = next_position.x, next_position.y

            while searching:
                positions = get_valid_neigbours(x_coord, y_coord, self.valid_board)

                for x, y in positions:

                    # check if next value is valid and no dead end
                    if self.valid_board[x][y] == value-1 and (x, y) not in dead_ends.keys():
                        dead = False
                        step_history.append((x, y))
                        x_coord, y_coord = x, y
                        value -= 1
                        break
                    # mark dead ends
                    else:
                        dead = True

                    # break if food was found
                    if self.valid_board[x][y] == -99:
                        longest_way[direction] = -99
                        searching = False
                        dead = False
                        break

                    # break if a valid endnode was found
                    if self.valid_board[x][y] == 0:   # or self.valid_board[x][y] == -Params_ValidActions.DEPTH
                        searching = False
                        dead = False
                        break

                # check if dead end and no more possible nodes to explore
                if dead and not step_history:
                    searching = False

                # check if dead end but still valid nodes to explore
                if dead and step_history:
                    dead_ends[(x_coord, y_coord)] = value
                    step_history.pop(-1)
                    if step_history:
                        x_coord, y_coord = step_history[-1]
                    value += 1

                if longest_way[direction] >= value:
                    longest_way[direction] = value

        escape_direction_keys = []
        escape_path_value = []

        for k, v in longest_way.items():
            if v > -Params_ValidActions.DEPTH:
                invalid_actions.append(k)

            escape_direction_keys.append(k)
            escape_path_value.append(v)

        # sort dict
        order = np.argsort(escape_path_value)
        escape_direction_keys = [escape_direction_keys[i] for i in order]
        escape_path_value = [escape_path_value[i] for i in order]
        longest_way = dict(zip(escape_direction_keys,  escape_path_value))

        return invalid_actions, longest_way

    def _calculate_board(self, enemy_snakes: List[Snake]) -> np.ndarray:
        #########################
        #
        # Idee: Für jede Schlange board einzeln berechnen und dann mit minimalen Werten überlagern
        #
        #########################

        action_plan = np.zeros((self.board.width, self.board.height))

        # add enemy snakes to board -> ( better with all snakes? )
        for snake in self.board.snakes:
            for index, position in enumerate(snake.body[::-1]):
                self.valid_board[position.x][position.y] = -(index + 1)
                action_plan[position.x][position.y] = Params_ValidActions.BODY_VALUE
            action_plan[snake.get_head().x][snake.get_head().y] = Params_ValidActions.HEAD_VALUE

        # build movement area around all enemy snakes near us
        for enemy in enemy_snakes:

            head = enemy.get_head()

            flood_queue = get_valid_neigbours(head.x, head.y, self.valid_board)
            visited = [(head.x, head.y)]

            # build new flood for each depth level
            for step in range(1, self.depth + 1):
                flood_queue, visited, action_plan = self._action_flood_fill(flood_queue, step, visited, action_plan,
                                                                            enemy=True)

            if len(enemy.body) == 4:
                pass
        return action_plan

    def _find_invalid_actions(self) -> List[Direction]:
        help_board = np.zeros((self.board.width, self.board.height))
        head = self.my_snake.get_head()

        # mark snakes on the board
        self._mark_snakes(help_board)

        # calculate new wave for each depth level from queue
        flood_queue = get_valid_neigbours(head.x, head.y, self.valid_board)
        visited = [(head.x, head.y)]

        for step in range(1, self.depth + 1):
            flood_queue, visited, _ = self._action_flood_fill(flood_queue, step, visited, None, enemy=False)

        if not self.hungry:
            for food_pos in self.board.food:
                if Distance.manhattan_dist(head, food_pos) > 4:
                    self.valid_board[food_pos.x][food_pos.y] = 1

        invalid_actions, self.direction_depth = self._expand(head)

        print("Invalids: ", invalid_actions)
        return invalid_actions

    def _valid_check(self, enemy_snakes):

        # calculate range of my snake and find valid actions
        invalid_actions = self._find_invalid_actions()

        self.valid_actions = [valid_action for valid_action in self.valid_actions
                              if valid_action not in invalid_actions]

        print("Multi-Valid Actions:", self.valid_actions)

        # if less than 2 valid_actions decide to look deeper in direction_depth
        threshold = - self.depth + 1
        while self.direction_depth and len(self.valid_actions) < 2:
            self.valid_actions = [k for k, v in self.direction_depth.items() if v < threshold]
            threshold += 1
            if threshold == -2:
                break
            if len(self.board.snakes) > 2 and not self.hungry:
                if threshold < -5 and len(self.valid_actions) > 0:
                    break

        print("Valid Actions:", self.valid_actions)
        print("Direction Depth: ", self.direction_depth)
        print(self.valid_board)

    def multi_level_valid_actions(self) -> Tuple[List[Direction], np.ndarray]:

        start_time = time.time()
        action_plan = None
        possible_actions = self.my_snake.possible_actions()
        self.valid_actions = self.get_valid_actions(self.board, possible_actions, self.snakes,
                                                    self.my_snake, self.grid_map, True)

        if self.my_snake.health < Params_Automat.HUNGER_HEALTH_BOUNDARY:
            self.hungry = True
            self.depth = 7
        else:
            self.hungry = False
            self.depth = Params_ValidActions.DEPTH

        enemy_snakes = [snake for snake in self.snakes if snake.snake_id != self.my_snake.snake_id]

        # calculate enemy snakes board
        action_plan = self._calculate_board(enemy_snakes)

        # calculate valid actions
        self._valid_check(enemy_snakes)

        if not self.valid_actions and not self.hungry:
            # calculate valid_actions and allow snake to eat
            self.valid_actions = self.get_valid_actions(self.board, possible_actions, self.snakes,
                                                        self.my_snake, self.grid_map, False)
            self._valid_check(enemy_snakes)

        print("DAUER", time.time() - start_time)

        return self.valid_actions, action_plan


"""
self.board.snakes[0].body = [Position(2,3),Position(2,4),Position(2,5),Position(2,6),Position(2,7),Position(2,8), Position(2,9),Position(3,9),Position(4,9),Position(5,9),Position(6,9)]
self.board.snakes[2].body = [Position(0,6),Position(0,7),Position(0,8),Position(0,9),Position(0,10),Position(1,10), Position(2,10),Position(3,10),Position(4,10),Position(5,10)Position(6,10)Position(7,10)]
self.board.snakes[1].body = [Position(0,0),Position(0,1),Position(0,2),Position(0,3)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(1,6)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(0,5)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(0,5),Position(0,6),Position(0,7),Position(0,8)]
"""
