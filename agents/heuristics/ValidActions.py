from typing import List, Tuple, Dict
import numpy as np
import time

from agents.heuristics.Distance import Distance
from agents.Hyperparameters import Params_ValidActions

from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Occupant import Occupant


# TODO:
#  Felder im toten Winkel berücksichtigen -> Flood Fill bei my square und überschreiben von enemy actions
#  Chase Tail für Gegner Body berücksichtigen
#  Food ausschluss in anxious mit ermöglichen. In valid actions Food mit einbeziehen als option
#  Wenn keine validen Actions dann head to head
#  A-Star korrigieren für Hindernisse
#  besser food chasen -> Anzahl des foods auf boards berücksichitgen -> früher essen?
#  invalids_werden nicht richtig gesetzt -> expand falsch?
#


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
                          grid_map: GridMap[Occupant]) -> List[Direction]:

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
            if my_snake.health > Params_ValidActions.FOOD_BOUNDARY:
                if grid_map.get_value_at_position(next_position) is Occupant.Food:
                    continue

            # outofbounds
            if board.is_out_of_bounds(next_position):
                continue

            # body crash -> ganze Gegner Schlange minus letzten Teil
            if grid_map.get_value_at_position(next_position) is Occupant.Snake and next_position not in snake_tails:
                continue

            if next_position in forbidden_fields:
                continue

            val_actions.append(direction)

        if not val_actions:
            for direction in possible_actions:
                next_position = my_head.advanced(direction)
                # eat if its the only possible valid action
                if grid_map.get_value_at_position(next_position) is Occupant.Food:
                    val_actions.append(direction)

        return val_actions

    def _get_square(self, head: Position, valid_board: np.ndarray, step: int) -> Tuple[np.ndarray, Tuple[int, int]]:
        width = self.board.width
        height = self.board.height

        x_low = head.x - step if head.x - step > 0 else 0
        x_high = head.x + step + 1 if head.x + step + 1 < width else width
        y_low = head.y - step if head.y - step > 0 else 0
        y_high = head.y + step + 1 if head.y + step + 1 < height else height

        return valid_board[x_low: x_high, y_low: y_high], (x_low, y_low)

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

                # aktionsradius der Schlange beschreiben
                if self.valid_board[x, y] == -step + 1 or self.valid_board[x, y] == 0 or step < self.valid_board[x, y]:
                    if self.valid_board[x, y] < 10 and step == 1 and self.valid_board[x, y] != 1:
                        self.valid_board[x][y] = -step
                    if self.valid_board[x, y] < 10 and -(step - 1) in neighbour_values:
                        self.valid_board[x][y] = -step

                # eigenenes Schwanzende berücksichtigen
                if 10 < self.valid_board[x, y] < 20 and self.valid_board[x, y] % 10 <= step \
                        and -(step - 1) in neighbour_values:
                    self.valid_board[x][y] = -step

                # feindliche Schwanzenden berücksichtigen
                if 20 < self.valid_board[x, y] < 30 and self.valid_board[x, y] % 10 <= step \
                        and -(step - 1) in neighbour_values:
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
                    # TODO teilweise noch kein korrektes backtracking bzw ausbreiten bis zum letzten node -> 0 als Ziel?
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

            enemy_depth = enemy.get_length() if self.depth > enemy.get_length() else self.depth
            head = enemy.get_head()

            flood_queue = get_valid_neigbours(head.x, head.y, self.valid_board)
            visited = [(head.x, head.y)]

            # build new flood for each depth level
            for step in range(1, self.depth + 1):
                flood_queue, visited, action_plan = self._action_flood_fill(flood_queue, step, visited, action_plan,
                                                                            enemy=True)

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
                self.valid_board[food_pos.x][food_pos.y] = 1
            # old_board = self.valid_board.copy()

        invalid_actions, self.direction_depth = self._expand(head)

        """
        if len(invalid_actions) == len(self.valid_actions):
            self.valid_board = old_board
            invalid_actions, self.direction_depth = self._expand(head)
        """

        print("Invalids: ", invalid_actions)
        return invalid_actions

    def multi_level_valid_actions(self) -> Tuple[List[Direction], np.ndarray]:

        action_plan = None
        possible_actions = self.my_snake.possible_actions()
        self.valid_actions = self.get_valid_actions(self.board, possible_actions, self.snakes,
                                                    self.my_snake, self.grid_map)

        if self.my_snake.health < 30:
            self.hungry = True
            self.depth = 4
        else:
            self.hungry = False
            self.depth = Params_ValidActions.DEPTH

        # if len(self.snakes[0].body) == 4:
        #    print("Hallo")

        enemy_snakes = [snake for snake in self.snakes if snake.snake_id != self.my_snake.snake_id]

        start_time = time.time()

        # calculate enemy snakes board
        while time.time() - start_time < 0.06:
            action_plan = self._calculate_board(enemy_snakes)

            if enemy_snakes:
                # calculate range of my snake and find valid actions
                invalid_actions = self._find_invalid_actions()

                if not invalid_actions:
                    invalid_actions = self._find_invalid_actions()

                self.valid_actions = [valid_action for valid_action in self.valid_actions
                                      if valid_action not in invalid_actions]

            if not self.valid_actions or self.my_snake.health < 20:
                break

            self.depth += 1

        # print("Multi-Valid Actions:", self.valid_actions)

        if not self.valid_actions and self.direction_depth:
            longest_path = list(self.direction_depth.values())[0]
            for k, v in self.direction_depth.items():
                if v < longest_path+2:
                    self.valid_actions.append(k)

        print("Valid Actions:", self.valid_actions)
        print(self.valid_board)

        return self.valid_actions, action_plan


"""
self.board.snakes[0].body = [Position(2,3),Position(2,4),Position(2,5),Position(2,6),Position(2,7),Position(2,8), Position(2,9),Position(3,9),Position(4,9),Position(5,9),Position(6,9)]
self.board.snakes[2].body = [Position(0,6),Position(0,7),Position(0,8),Position(0,9),Position(0,10),Position(1,10), Position(2,10),Position(3,10),Position(4,10),Position(5,10)Position(6,10)Position(7,10)]
self.board.snakes[1].body = [Position(0,0),Position(0,1),Position(0,2),Position(0,3)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(1,6)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(0,5)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(0,5),Position(0,6),Position(0,7),Position(0,8)]
"""
