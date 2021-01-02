from typing import List, Tuple
import numpy as np

from agents.heuristics.Distance import Distance
from agents.Hyperparameters import Params_ValidActions

from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Occupant import Occupant
from environment.Battlesnake.helper.DirectionUtil import DirectionUtil


class ValidActions:

    @staticmethod
    def get_valid_actions(board: BoardState,
                          possible_actions: List[Direction],
                          snakes: List[Snake],
                          my_snake: Snake,
                          grid_map: GridMap[Occupant]) -> List[Direction]:

        my_head = my_snake.get_head()
        snake_tails = []
        valid_actions = []

        for snake in snakes:
            if snake.health == 100:
                continue
            snake_tails.append(snake.get_tail())

        for direction in possible_actions:
            next_position = my_head.advanced(direction)

            # avoid eating
            if my_snake.health > 20:
                if grid_map.get_value_at_position(next_position) is Occupant.Food:
                    continue

            # outofbounds
            if board.is_out_of_bounds(next_position):
                continue

            # body crash -> ganze Gegner Schlange minus letzten Teil
            if grid_map.get_value_at_position(next_position) is Occupant.Snake and next_position not in snake_tails:
                continue

            # head crash -> Alle möglichen Richtungen des Heads der Gegner Schlange beachten
            cont = False
            for en_snake in snakes:
                if en_snake.snake_id != my_snake.snake_id:

                    if en_snake.get_length() >= my_snake.get_length():
                        enemy_head = en_snake.get_head()
                        positions_enemy = [enemy_head.advanced(action) for action in en_snake.possible_actions()]

                        if next_position in positions_enemy:
                            cont = True
            if cont:
                continue
            valid_actions.append(direction)

        if not valid_actions:
            for direction in possible_actions:
                next_position = my_head.advanced(direction)
                # avoid eating
                if grid_map.get_value_at_position(next_position) is Occupant.Food:
                    valid_actions.append(direction)

        return valid_actions

    @staticmethod
    def get_square(head: Position, valid_board: np.ndarray, width: int, height: int, step: int) -> Tuple[np.ndarray,
                                                                                                         Tuple[int,
                                                                                                               int]]:
        x_low = head.x - step if head.x - step > 0 else 0
        x_high = head.x + step + 1 if head.x + step + 1 < width else width
        y_low = head.y - step if head.y - step > 0 else 0
        y_high = head.y + step + 1 if head.y + step + 1 < height else height

        return valid_board[x_low: x_high, y_low: y_high], (x_low, y_low)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def calculate_board(board: BoardState, enemy_snakes: List[Snake], depth: int) -> Tuple[np.ndarray, np.ndarray]:

        #########################
        #
        # Idee: Für jede Schlange board einzeln berechnen und dann mit minimalen Werten überlagern
        #
        #########################

        valid_board = np.zeros((board.width, board.height))
        action_plan = np.zeros((board.width, board.height))

        # add enemy snakes to board -> ( better with all snakes? )
        for snake in board.snakes:
            for index, position in enumerate(snake.body[::-1]):
                valid_board[position.x][position.y] = -(index + 1)
                action_plan[position.x][position.y] = Params_ValidActions.BODY_VALUE
            action_plan[snake.get_head().x][snake.get_head().y] = Params_ValidActions.HEAD_VALUE

        # build movement area around all enemy snakes near us
        for enemy in enemy_snakes:

            enemy_depth = enemy.get_length() if depth > enemy.get_length() else depth
            head = enemy.get_head()

            # build new circle for each depth level
            for step in range(1, enemy_depth + 1):

                square, (_, _) = ValidActions.get_square(head, valid_board, board.width, board.height, step)
                action_square, (_, _) = ValidActions.get_square(head, action_plan, board.width, board.height, step)
                square_head = np.where(square == valid_board[head.x][head.y])

                # TODO adjust fields that get checked more efficient
                # fields = Mitte bzw. x Koordinate von square_head
                # pro step + und - step bis Koordinate von y == y-square-head
                # danach wieder minus 1 bis step/2
                # Distance.manhatttan durch step ersetzen
                # Extra Bedingung für Snake Body

                for x in range(0, square.shape[0]):
                    for y in range(0, square.shape[1]):

                        # check for each field in circle if it has the right distance
                        if Distance.manhattan_dist(Position(square_head[0][0], square_head[1][0]), Position(x, y)) \
                                == step and square[x][y] + step >= 0:

                            neighbour_field_values = ValidActions.get_valid_neighbour_values(x, y, square)

                            for field in neighbour_field_values:
                                if step - 1 == field:
                                    # nur der nächste Gegner zählt, nicht überlagern
                                    if square[x][y] == 0 or step <= square[x][y]:
                                        square[x][y] = step
                                    action_square[x][y] = Params_ValidActions.AREA_VALUE
            """
            # fix empty snake_body fields
            for body_part in enemy.body[::-1]:
                body_neighbours = ValidActions.get_valid_neighbour_values(body_part.x, body_part.y, valid_board)

                field_values = [i for i in body_neighbours if i > 0]
                if field_values:
                    field_value = min(field_values)
                else:
                    continue

                if field_value + valid_board[body_part.x][body_part.y] >= 0:
                    valid_board[body_part.x][body_part.y] = field_value + 1
                else:
                    valid_board[body_part.x][body_part.y] = field_value + 2
            """
        return valid_board, action_plan

    @staticmethod
    def backtrack(coord_list, valid_board: np.ndarray):
        for (x, y) in coord_list:
            all_neighbours_greater = True
            back_track_list = []
            while all_neighbours_greater:
                all_neighbours_greater = [value for value in ValidActions.get_valid_neighbour_values(x, y, valid_board)
                                          if value >= valid_board[x, y] and value != 99]

                if all_neighbours_greater:
                    backtrack_positions = [position for position in ValidActions.get_valid_neigbours(x, y, valid_board)
                                           if valid_board[position[0]][position[1]] == valid_board[x][y] + 1]

                    # TODO: 99er besser setzen
                    # wenn körper zwischem erreichbaren Feld und Schlange ist dann keine 99
                    # probleme wenn körper des Gegners voraus geht
                    # es fehlen noch Einbahnstraßen
                    # es werden zu viele falsche am Körper gesetzt (x)
                    if valid_board[x, y] < 10:
                        valid_board[x, y] = 99
                    back_track_list += backtrack_positions

                if back_track_list:
                    (x, y) = back_track_list.pop(0)

    @staticmethod
    def find_invalid_actions(board: BoardState, valid_board: np.ndarray, my_snake: Snake,
                             depth: int) -> List[Direction]:
        help_board = np.zeros((board.width, board.height))
        head = my_snake.get_head()
        backtrack_list = []
        invalid_actions = []
        snake_bodies = []
        for snake in board.snakes:
            if snake.snake_id != my_snake.snake_id:
                snake_bodies += snake.body
                for index, position in enumerate(snake.body[::-1]):
                    valid_board[position.x][position.y] = (index + 21)
                    help_board[position.x][position.y] = (index + 21)

        # mark my snake on board
        for index, position in enumerate(my_snake.body[::-1]):
            valid_board[position.x][position.y] = (index + 11)
            help_board[position.x][position.y] = (index + 11)

        # build new circle for each depth level
        for step in range(1, depth + 1):

            square, (x_delta, y_delta) = ValidActions.get_square(head, valid_board, board.width, board.height, step)
            square_head = np.where(square == help_board[head.x][head.y])

            # calculate elements in array
            for x in range(0, square.shape[0]):
                for y in range(0, square.shape[1]):

                    if Distance.manhattan_dist(Position(square_head[0][0], square_head[1][0]), Position(x, y)) == step:

                        neighbour_values = ValidActions.get_valid_neighbour_values(x, y, square)
                        border_field = True if x + x_delta == 0 or x + x_delta == board.width - 1 or y + y_delta == 0 or y + y_delta == board.height - 1 else False
                        snake_body_field = True if Position(x + x_delta, y + y_delta) in snake_bodies and square[x][
                            y] > depth else False

                        # kritische Felder markieren
                        if 0 < square[x][y] < 99 and square[x][y] - step <= 0:
                            square[x][y] = 99
                            continue

                        # aktionsradius der Schlange beschreiben
                        if square[x, y] == -step + 1 or step < square[x, y] or square[x, y] == 0:
                            if square[x, y] < 10:
                                square[x][y] = -step

                        # sackgassen erkennen am Rand
                        if border_field:
                            values = [value for value in neighbour_values if
                                      abs(value) <= abs(square[x][y])]
                            if not values:
                                backtrack_list.append((x + x_delta, y + y_delta))

                        # sackgassen erkennen an Snakebody
                        if snake_body_field:
                            values = [value for value in neighbour_values if value > square[x][y]]
                            if not values:
                                backtrack_list.append((x + x_delta, y + y_delta))

        if backtrack_list:
            ValidActions.backtrack(backtrack_list, valid_board)
            for x, y in ValidActions.get_valid_neigbours(head.x, head.y, valid_board):
                if valid_board[x][y] == 99:
                    direction = DirectionUtil.direction_to_reach_field(head, Position(x, y))
                    invalid_actions.append(direction)
        else:
            return []

        print(valid_board)

        return invalid_actions

    @staticmethod
    def multi_level_valid_actions(board: BoardState,
                                  snakes: List[Snake],
                                  my_snake: Snake,
                                  grid_map: GridMap[Occupant],
                                  depth: int) -> Tuple[List[Direction], np.ndarray]:

        possible_actions = my_snake.possible_actions()
        valid_actions = ValidActions.get_valid_actions(board, possible_actions, snakes, my_snake, grid_map)

        enemy_snakes = [snake for snake in snakes if snake.snake_id != my_snake.snake_id
                        and Distance.manhattan_dist(snake.get_head(), my_snake.get_head())
                        < Params_ValidActions.DIST_TO_ENEMY]

        # if len(board.snakes[0].body) == 4:
        #     print("Hallo")

        enemy_board, action_plan = ValidActions.calculate_board(board, enemy_snakes, depth)

        if enemy_snakes:
            invalid_actions = ValidActions.find_invalid_actions(board, enemy_board, my_snake, depth)

            valid_actions = [valid_action for valid_action in valid_actions if valid_action not in invalid_actions]

        print("Multi-Valid Actions:", valid_actions)
        if not valid_actions:
            valid_actions = ValidActions.get_valid_actions(board, possible_actions, snakes, my_snake, grid_map)

        print("Valid Actions:", valid_actions)

        return valid_actions, action_plan

# [Position(1,2),Position(1,3),Position(2,3),Position(2,4),Position(2,5),Position(2,6),Position(2,7),Position(2,8),Position(2,9),Position(3,9),Position(4,9),Position(5,9),Position(6,9)]
# [Position(0,0),Position(0,1),Position(0,2),Position(0,3)]

# board.snakes[0].body = [Position(1,2),Position(1,3),Position(2,3),Position(2,4),Position(2,5),Position(2,6),Position(2,7),Position(2,8),Position(2,9),Position(3,9),Position(4,9),Position(5,9),Position(6,9)]
# board.snakes[1].body = [Position(0,0),Position(0,1),Position(0,2),Position(0,3)]
