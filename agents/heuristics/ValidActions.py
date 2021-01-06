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
#  Felder im toten Winkel berücksichtigen
#  Gegner Square besser vorraussagen !!! Gibt probleme bei head to head und enemy head radius -> Fälle simulieren
#  Chase Tail für Gegner Body berücksichtigen
#  Teilweise Body-Collision
#  Auswahl von Food nicht optimal -> RelevantFood

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

    def _calculate_my_square(self, step: int, head: Position, help_board: np.ndarray) -> None:
        square, (_, _) = self._get_square(head, self.valid_board, step)  # (x_delta, y_delta)
        square_head = np.where(square == help_board[head.x][head.y])

        # calculate elements in array
        for x in range(0, square.shape[0]):
            for y in range(0, square.shape[1]):

                if Distance.manhattan_dist(Position(square_head[0][0], square_head[1][0]), Position(x, y)) == step:
                    neighbour_values = get_valid_neighbour_values(x, y, square)

                    # aktionsradius der Schlange beschreiben
                    if square[x, y] == -step + 1 or square[x, y] == 0 or step < square[x, y]:
                        if square[x, y] < 10 and step == 1 and square[x, y] != 1:
                            square[x][y] = -step
                        if square[x, y] < 10 and -(step - 1) in neighbour_values:
                            square[x][y] = -step
                    # eigenenes Schwanzende berücksichtigen
                    if 10 < square[x, y] < 20 and square[x, y] % 10 <= step and -(step - 1) in neighbour_values:
                        square[x][y] = -step
                    # feindliche Schwanzenden berücksichtigen
                    if 20 < square[x, y] < 30 and square[x, y] % 10 <= step and -(step - 1) in neighbour_values:
                        square[x][y] = -step

                    # kritische Felder markieren
                    if square[x][y] > 0 and square[x][y] - step <= 0:
                        pass
                        # square[x][y] = enemy_board[x + x_delta][y + y_delta]

    def _calculate_enemy_square(self, step: int, head: Position, action_plan: np.ndarray) -> None:
        square, (_, _) = self._get_square(head, self.valid_board, step)
        action_square, (_, _) = self._get_square(head, action_plan, step)
        square_head = np.where(square == self.valid_board[head.x][head.y])
        head_pos = Position(square_head[0][0], square_head[1][0])

        # TODO adjust fields that get checked more efficient
        # fields = Mitte bzw. x Koordinate von square_head
        # pro step + und - step bis Koordinate von y == y-square-head
        # danach wieder minus 1 bis step/2
        # Distance.manhatttan durch step ersetzen
        # Extra Bedingung für Snake Body

        for x in range(0, square.shape[0]):
            for y in range(0, square.shape[1]):

                # check for each field in circle if it has the right distance
                if Distance.manhattan_dist(head_pos, Position(x, y)) == step and square[x][y] + step >= 0:
                    neighbour_field_values = get_valid_neighbour_values(x, y, square)

                    for field in neighbour_field_values:
                        if step - 1 == field:
                            # nur der naheste Gegner zählt, nicht überlagern
                            if square[x][y] == 0 or step <= abs(square[x][y]):
                                square[x][y] = step
                            action_square[x][y] = Params_ValidActions.AREA_VALUE

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

                    # break if a valid endnode was found
                    if self.valid_board[x][y] == -Params_ValidActions.DEPTH or self.valid_board[x][y] == 0:
                        searching = False
                        dead = False
                        break

                # check if dead end and no more possible nodes to explore
                if dead and step_history == []:
                    searching = False

                # check if dead end but still valid nodes to explore
                if dead and step_history:
                    dead_ends[(x_coord, y_coord)] = value
                    step_history.pop(-1)
                    if step_history:
                        x_coord, y_coord = step_history[-1]
                    value += 1

                if longest_way[direction] > value:
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

        print("LongestWay:", longest_way)
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

            # build new circle for each depth level
            for step in range(1, enemy_depth + 1):
                self._calculate_enemy_square(step, head, action_plan)

        return action_plan

    def _find_invalid_actions(self) -> List[Direction]:
        help_board = np.zeros((self.board.width, self.board.height))
        head = self.my_snake.get_head()

        # mark snakes on the board
        self._mark_snakes(help_board)

        # calculate new square for each depth level
        for step in range(1, self.depth + 1):
            self._calculate_my_square(step, head, help_board)

        if self.hungry:
            invalid_actions, self.direction_depth = self._expand(head)
        else:
            old_board = self.valid_board.copy()
            for food_pos in self.board.food:
                self.valid_board[food_pos.x][food_pos.y] = 1

            invalid_actions, self.direction_depth = self._expand(head)

            if len(invalid_actions) == len(self.valid_actions):
                self.valid_board = old_board
                invalid_actions, self.direction_depth = self._expand(head)

        print(self.valid_board)
        print("Invalids: ", invalid_actions)
        return invalid_actions

    def multi_level_valid_actions(self) -> Tuple[List[Direction], np.ndarray]:
        possible_actions = self.my_snake.possible_actions()
        self.valid_actions = self.get_valid_actions(self.board, possible_actions, self.snakes,
                                                                    self.my_snake, self.grid_map)

        if self.my_snake.health < 20:
            self.hungry = True
            self.depth = 5
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

            if not self.valid_actions or self.my_snake.health < 25:
                break

            self.depth += 1

        print("Multi-Valid Actions:", self.valid_actions)

        if not self.valid_actions and self.direction_depth:
            longest_path = list(self.direction_depth.values())[0]
            for k, v in self.direction_depth.items():
                if v < longest_path+2:
                    self.valid_actions.append(k)

            print("Valid Actions:", self.valid_actions)

        return self.valid_actions, action_plan


"""
self.board.snakes[0].body = [Position(2,3),Position(2,4),Position(2,5),Position(2,6),Position(2,7),Position(2,8), Position(2,9),Position(3,9),Position(4,9),Position(5,9),Position(6,9)]
self.board.snakes[2].body = [Position(0,6),Position(0,7),Position(0,8),Position(0,9),Position(0,10),Position(1,10), Position(2,10),Position(3,10),Position(4,10),Position(5,10)Position(6,10)Position(7,10)]
self.board.snakes[1].body = [Position(0,0),Position(0,1),Position(0,2),Position(0,3)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(1,6)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(0,5)]
self.board.snakes[1].body = [Position(1,3),Position(1,4),Position(1,5),Position(0,5),Position(0,6),Position(0,7),Position(0,8)]
"""
