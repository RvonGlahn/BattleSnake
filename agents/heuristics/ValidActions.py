from typing import List, Tuple, Dict
import numpy as np
import time

from agents.heuristics.Distance import Distance
from agents.Hyperparameters import Params_ValidActions, Params_Automat
from agents.States import States

from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Occupant import Occupant


# TODO:
#  Food essen auf weg verringert die tiefe
#  Ab todespunkt/zug x zukünftige tote gegner vom Board löschen


class ValidActions:

    def __init__(self,
                 board: BoardState,
                 grid_map: GridMap,
                 me: Snake,
                 my_state: States
                 ):

        self.depth = Params_ValidActions.DEPTH
        self.board = board
        self.snakes = board.snakes
        self.grid_map = grid_map
        self.my_snake = me
        self.valid_board = np.zeros((self.board.width, self.board.height))
        self.valid_actions = []
        self.kill_board = np.zeros((self.board.width, self.board.height))
        self.direction_depth = {}
        self.state = my_state

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
            if my_snake.health > Params_ValidActions.FOOD_BOUNDARY and avoid_food and my_snake.get_length() > 5:
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

                if step < 4:
                    action_plan[x][y] = Params_ValidActions.AREA_VALUE * (4 - step)

            if not enemy:
                if step < self.valid_board[x][y] < 20 or self.valid_board[x][y] == 0:
                    self.valid_board[x][y] = -step
                
                # eigenenes Schwanzende berücksichtigen
                if 20 < self.valid_board[x, y] < 40 and self.valid_board[x, y] % 20 <= step:
                    self.valid_board[x][y] = -step

                # Schwanzanfang berücksichtigen
                if step == 1:
                    for snake in self.board.snakes:
                        tail = snake.get_tail()
                        if snake.health != 100 and (x, y) == (tail.x, tail.y) and self.valid_board[x, y] != 1:
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
        # TODO: add info of enemy step to snake body -> List ?
        # mark enemy snakes
        for snake in self.board.snakes:
            if snake.snake_id != self.my_snake.snake_id:
                for index, position in enumerate(snake.body[::-1]):
                    self.valid_board[position.x][position.y] = (index + 41)
                    help_board[position.x][position.y] = (index + 41)

        # mark my snake on board
        for index, position in enumerate(self.my_snake.body[::-1]):
            self.valid_board[position.x][position.y] = (index + 21)
            help_board[position.x][position.y] = (index + 21)

    def expand(self, next_position: Position) -> int:

        step_history = []
        dead_ends = {}
        searching = True
        value = -1
        dead = False
        longest_way = 0

        # get first field of Direction and check if valid
        if self.valid_board[next_position.x][next_position.y] != value:
            return 0
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

                # break if a valid endnode was found
                if self.valid_board[x][y] == 0:   # or self.valid_board[x][y] == -Params_ValidActions.DEPTH
                    searching = False
                    dead = False
                    break

            # check if dead end and no more possible nodes to explore
            if dead and not step_history:
                searching = False

            # update range for each direction
            if longest_way >= value:
                longest_way = value

            # check if dead end but still valid nodes to explore
            if dead and step_history:
                dead_ends[(x_coord, y_coord)] = value
                step_history.pop(-1)
                if step_history:
                    x_coord, y_coord = step_history[-1]
                value += 1

        return longest_way

    def _calculate_board(self) -> np.ndarray:
        #########################
        #
        # Idee: Für jede Schlange board einzeln berechnen und dann mit minimalen Werten überlagern
        #
        #########################
        enemy_snakes = [snake for snake in self.snakes if snake.snake_id != self.my_snake.snake_id]
        action_plan = np.zeros((self.board.width, self.board.height))

        # add enemy snakes to board -> ( better with all snakes? )
        for snake in self.board.snakes:
            for index, position in enumerate(snake.body[::-1]):
                self.valid_board[position.x][position.y] = -(index + 1)
                action_plan[position.x][position.y] = Params_ValidActions.BODY_VALUE
            action_plan[snake.get_head().x][snake.get_head().y] = Params_ValidActions.HEAD_VALUE

        # build movement area around all enemy snakes near us
        for enemy in enemy_snakes:
            start_value = 1
            if enemy.get_length() < self.my_snake.get_length():
                start_value = 2
            head = enemy.get_head()

            flood_queue = get_valid_neigbours(head.x, head.y, self.valid_board)
            visited = [(head.x, head.y)]

            # build new flood for each depth level
            for step in range(start_value, self.depth + 1):
                flood_queue, visited, action_plan = self._action_flood_fill(flood_queue, step, visited, action_plan,
                                                                            enemy=True)

            if len(enemy.body) == 4:
                pass
        return action_plan

    def _order_directions(self):
        invalid_actions = []
        escape_direction_keys = []
        escape_path_value = []

        for k, v in self.direction_depth.items():
            if v > -Params_ValidActions.DEPTH:
                invalid_actions.append(k)

            escape_direction_keys.append(k)
            escape_path_value.append(v)

        # sort dict
        order = np.argsort(escape_path_value)
        escape_direction_keys = [escape_direction_keys[i] for i in order]
        escape_path_value = [escape_path_value[i] for i in order]
        self.direction_depth = dict(zip(escape_direction_keys, escape_path_value))

        return invalid_actions

    def _find_invalid_actions(self) -> List[Direction]:
        help_board = np.zeros((self.board.width, self.board.height))
        head = self.my_snake.get_head()

        # mark snakes on the board
        self._mark_snakes(help_board)
        old_board = self.valid_board.copy()
        # print(self.valid_board)

        # calculate new wave for each depth level from queue
        for direction in self.valid_actions:
            next_position = head.advanced(direction)
            flood_queue = [(next_position.x, next_position.y)]
            visited = [(head.x, head.y)]

            for step in range(1, self.depth + 1):
                flood_queue, visited, _ = self._action_flood_fill(flood_queue, step, visited, None, enemy=False)

            if self.state != States.HUNGRY and self.my_snake.get_length() > 5:
                for food_pos in self.board.food:
                    if Distance.manhattan_dist(head, food_pos) > 3:
                        self.valid_board[food_pos.x][food_pos.y] = 1

            # expand for each direction
            depth = self.expand(next_position)
            print(self.valid_board)

            self.direction_depth[direction] = depth
            self.kill_board = np.add(self.kill_board, self.valid_board)
            self.valid_board = old_board.copy()

        self.kill_board = np.subtract(self.kill_board, old_board*(len(self.valid_actions)-1))

        invalid_actions = self._order_directions()

        return invalid_actions

    def _valid_check(self):

        # calculate range of my snake and find valid actions
        invalid_actions = self._find_invalid_actions()

        self.valid_actions = [valid_action for valid_action in self.valid_actions
                              if valid_action not in invalid_actions]

        print("Multi-Valid Actions:", self.valid_actions)

        # if less than 2 valid_actions decide to look deeper in direction_depth
        borderfields = count_border_fields(self.my_snake.get_head(), self.valid_board)
        threshold = - self.depth + 1
        while self.direction_depth and len(self.valid_actions) - borderfields < 2:
            self.valid_actions = [k for k, v in self.direction_depth.items() if v <= threshold]
            if threshold < -3 and len(self.valid_actions) >= 1:
                break
            if len(self.board.snakes) > 2 and self.state != States.HUNGRY:
                if threshold <= -5 and len(self.valid_actions) >= 1:
                    break
            if threshold == -1:
                break
            threshold += 1
        print("Direction Depth: ", self.direction_depth)
        print("Valid Actions:", self.valid_actions)

    def multi_level_valid_actions(self) -> Tuple[List[Direction], np.ndarray, Dict,  np.ndarray]:

        start_time = time.time()
        deepest = 0

        possible_actions = self.my_snake.possible_actions()
        self.valid_actions = self.get_valid_actions(self.board, possible_actions, self.snakes,
                                                    self.my_snake, self.grid_map, avoid_food=True)

        if self.my_snake.health < Params_Automat.HUNGER_HEALTH_BOUNDARY:
            self.depth = 8
        if self.my_snake.health < 10:
            self.depth = 4
        else:
            self.depth = Params_ValidActions.DEPTH
        if self.my_snake.health > 60:
            self.depth = Params_ValidActions.DEPTH

        # calculate enemy snakes board
        action_plan = self._calculate_board()

        # calculate valid actions
        self._valid_check()

        if self.direction_depth:
            deepest = min(list(self.direction_depth.values()))

        if (len(self.valid_actions) < 2 or deepest < -4) and self.state != States.HUNGRY:
            # calculate valid_actions and allow snake to eat
            self.valid_actions = self.get_valid_actions(self.board, possible_actions, self.snakes,
                                                        self.my_snake, self.grid_map, avoid_food=False)
            if self.valid_actions:
                self._valid_check()

        print("ValidAction-DAUER: ", time.time() - start_time)

        return self.valid_actions, action_plan, self.direction_depth, self.kill_board


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


def count_border_fields(my_head: Position, board: np.ndarray) -> int:
    count = 0
    width, height = board.shape
    valid_neigbours = get_valid_neigbours(my_head.x, my_head.y, board)

    for (x, y) in valid_neigbours:
        if x == 0 or y == 0 or x == width - 1 or y == height - 1:
            count = 1

    return count


"""
self.board.snakes[0].body = [Position(2,3),Position(2,4),Position(2,5),Position(2,6),Position(2,7),Position(2,8), 
Position(2,9),Position(3,9),Position(4,9),Position(5,9),Position(6,9)]
self.board.snakes[2].body = [Position(0,6),Position(0,7),Position(0,8),Position(0,9),Position(0,10),Position(1,10), 
Position(2,10),Position(3,10),Position(4,10),Position(5,10)Position(6,10)Position(7,10)]
self.board.snakes[1].body = [Position(0,0),Position(0,1),Position(0,2),Position(0,3)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(1,6)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(0,5)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(0,5),Position(0,6),
Position(0,7),Position(0,8)]
"""