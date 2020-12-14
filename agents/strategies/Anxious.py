from typing import List

import numpy as np
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position
from agents.heuristics.Distance import Distance
from agents.heuristics.ValidActions import ValidActions


class Anxious:

    @staticmethod
    def _get_relevant_corner(my_head, snakes, board) -> Position:
        bottom_left, bottom_right, top_left, top_right = (Position(3, 3)), \
                                                         (Position(3, board.height - 3)), \
                                                         (Position(board.width - 3, 3)), \
                                                         (Position(board.width - 3, board.height - 3))
        corners = []
        corners.extend((bottom_left, bottom_right, top_left, top_right))
        enemy_heads = [snake.get_head() for snake in snakes if snake.get_head() is not my_head]
        my_close_corner = corners[0]
        my_dist_to_best_corner = Distance.manhattan_dist(my_close_corner, my_head)
        for corner in corners:
            enemy_dist_to_corner = min([Distance.manhattan_dist(corner, head) for head in enemy_heads])
            my_dist_to_corner = Distance.manhattan_dist(corner, my_head)
            if my_dist_to_corner <= enemy_dist_to_corner and my_dist_to_corner <= my_dist_to_best_corner:
                my_close_corner = corner
                my_dist_to_best_corner = my_dist_to_corner
        return my_close_corner

    @staticmethod
    def hide_in_corner(board: BoardState, you: Snake, grid_map) -> Direction:

        head = you.get_head()
        tail = you.get_tail()

        # get the best corner
        corner = Anxious._get_relevant_corner(head, board.snakes, board)

        possible_actions = you.possible_actions()
        valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, you, grid_map)

        if valid_actions:
            next_action = valid_actions[0]

        # check if any part of the snake is in a corner, if so then chase tail, else go to the best corner
        if corner in you.body:
            # Chasing Tail
            distance_to_tail = Distance.manhattan_dist(tail, head.advanced(valid_actions[0]))

            for direction in valid_actions:
                distance_to_tail_next = Distance.manhattan_dist(tail, head.advanced(direction))
                if distance_to_tail_next <= distance_to_tail:
                    next_action = direction
                    distance_to_tail = distance_to_tail_next
        else:
            # Trying to reach Corner
            distance_to_tail = Distance.manhattan_dist(corner, head.advanced(valid_actions[0]))

            for direction in valid_actions:
                distance_to_tail_next = Distance.manhattan_dist(corner, head.advanced(direction))
                if distance_to_tail_next <= distance_to_tail:
                    next_action = direction
                    distance_to_tail = distance_to_tail_next

        return next_action

    @staticmethod
    def avoid_enemy(my_snake: Snake, board: BoardState, grid_map: GridMap) -> Direction:

        possible_actions = my_snake.possible_actions()
        valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, my_snake, grid_map)

        my_head = my_snake.get_head()
        enemy_heads = [snake.get_head() for snake in board.snakes if snake.snake_id is not my_snake.snake_id]

        middle = Position(int(board.height/2), int(board.width/2))
        corners = [Position(0, 0), Position(0, board.width), Position(board.height, 0), Position(board.height,
                                                                                                 board.width)]

        alpha = 2
        beta = 1
        gamma = 1
        theta = len(enemy_heads) * 5
        cost = []

        print(valid_actions)

        for action in valid_actions:
            next_position = my_head.advanced(action)

            distance_snakes = sum([Distance.manhattan_dist(next_position, enemy_head) for enemy_head in enemy_heads])
            distance_corners = sum([Distance.manhattan_dist(next_position, corner) for corner in corners])
            distance_mid = Distance.manhattan_dist(next_position, middle)
            distance_food = sum([Distance.manhattan_dist(next_position, food) for food in board.food
                                 if 3 < food.x < grid_map.width - 3 and 3 < food.y < grid_map.height - 3])

            distance = alpha * distance_snakes + beta * distance_corners - gamma * distance_food - theta * distance_mid

            cost.append(distance)

        if valid_actions:
            best_action = valid_actions[np.argmax(cost)]
        else:
            best_action = np.random.choice(possible_actions)

        return best_action
