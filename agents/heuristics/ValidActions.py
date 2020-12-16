from typing import List
from agents.heuristics.Distance import Distance

from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Occupant import Occupant


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
    def multi_level_valid_actions(board: BoardState,
                                  possible_actions: List[Direction],
                                  snakes: List[Snake],
                                  my_snake: Snake,
                                  grid_map: GridMap[Occupant],
                                  depth: int) -> List[Direction]:

        my_valid_actions = ValidActions.get_valid_actions(board, possible_actions, snakes, my_snake, grid_map)

        # only relevant snakes
        enemy_valid_actions = [ValidActions.get_valid_actions(board, possible_actions, snakes, enemy_snake, grid_map)
                               for enemy_snake in snakes
                               if Distance.manhattan_dist(my_snake, enemy_snake) < 4]

        for action in my_valid_actions:
            for enemy_action in enemy_valid_actions:
                if action == enemy_action:
                    my_valid_actions.remove(action)

        return my_valid_actions
