from typing import List
import numpy as np
import math
from agents.heuristics.Distance import Distance

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
    def get_square(head: Position, valid_board, width, height, step):
        x_low = head.x - step if head.x - step > 0 else 0
        x_high = head.x + step + 1 if head.x + step + 1 < width else width
        y_low = head.y - step if head.y - step > 0 else 0
        y_high = head.y + step + 1 if head.y + step + 1 < height else height

        return valid_board[x_low: x_high, y_low: y_high]

    @staticmethod
    def get_valid_neighbours_values(x: int, y: int, square):
        neighbour_fields = []
        neighbour_fields.append(square[x + 1][y]) if x + 1 < square.shape[0] else 0
        neighbour_fields.append(square[x - 1][y]) if x - 1 >= 0 else 0
        neighbour_fields.append(square[x][y + 1]) if y + 1 < square.shape[1] else 0
        neighbour_fields.append(square[x][y - 1]) if y - 1 >= 0 else 0
        return neighbour_fields

    @staticmethod
    def calculate_board(board: BoardState, enemy_snakes: List[Snake], depth: int):
        valid_board = np.zeros((board.width, board.height))

        # add enemy snakes to board -> ( better with all snakes? )
        for snake in board.snakes:
            for index, position in enumerate(snake.body[::-1]):
                valid_board[position.x][position.y] = -(index + 1)

        for enemy in enemy_snakes:
            head = enemy.get_head()
            # choose for each step an in bound square around every snake head
            # calculate manhattan Dist and choose points that equal step
            # check if points are valid_points -> point > 0 and min 1 neigbour is step-1
            for step in range(1, depth+1):

                square = ValidActions.get_square(head, valid_board, board.width, board.height, step)
                square_head = np.where(square == valid_board[head.x][head.y])

                for x in range(0, square.shape[0]):
                    for y in range(0, square.shape[1]):

                        if Distance.manhattan_dist(Position(square_head[0], square_head[1]), Position(x, y)) == step \
                                and square[x][y] + step >= 0:

                            neighbour_fields = ValidActions.get_valid_neighbours_values(x, y, square)

                            for field in neighbour_fields:
                                if step-1 == field:
                                    square[x][y] = step

            # fix empty snake_body fields
            for body_part in enemy.body[::-1]:
                body_neighbours = ValidActions.get_valid_neighbours_values(body_part.x, body_part.y, valid_board)

                field_value = min([i for i in body_neighbours if i > 0])

                if field_value + valid_board[body_part.x][body_part.y] >= 0:
                    valid_board[body_part.x][body_part.y] = field_value + 1
                else:
                    valid_board[body_part.x][body_part.y] = field_value + 2

        return valid_board

    @staticmethod
    def find_invalid_actions(board: BoardState, valid_board, my_snake: Snake, depth: int):

        head = my_snake.get_head()

        for step in range(1, depth + 1):

            square = ValidActions.get_square(head, valid_board, board.width, board.height, step)
            square_head = np.where(square == valid_board[head.x][head.y])

            for x in range(0, square.shape[0]):
                for y in range(0, square.shape[1]):

                    if Distance.manhattan_dist(Position(square_head[0], square_head[1]), Position(x, y)) == step and square[x][y] + step >= 0:

                        neighbour_fields = ValidActions.get_valid_neighbours_values(x, y, square)

                        for field in neighbour_fields:
                            if step - 1 == field:
                                square[x][y] = step

        return None
        # make n steps of possible enemy actions
        # Actions need a neighbor of previous step
        # check valid actions for my_snake on board

    @staticmethod
    def multi_level_valid_actions(board: BoardState,
                                  possible_actions: List[Direction],
                                  snakes: List[Snake],
                                  my_snake: Snake,
                                  grid_map: GridMap[Occupant],
                                  depth: int) -> List[Direction]:

        my_valid_actions = ValidActions.get_valid_actions(board, possible_actions, snakes, my_snake, grid_map)

        enemy_snakes = [snake for snake in snakes if snake.snake_id != my_snake.snake_id
                        and Distance.manhattan_dist(snake.get_head(), my_snake.get_head()) < 20]

        valid_board = ValidActions.calculate_board(board, enemy_snakes, depth)

        invalid_actions = ValidActions.find_invalid_actions(board, valid_board, my_snake, depth)

        return my_valid_actions
