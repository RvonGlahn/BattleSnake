from typing import List
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position
from agents.heuristics.Distance import Distance
from agents.heuristics.ValidActions import ValidActions

class Anxious:

    @staticmethod
    def _get_relevant_corner(my_head, snakes, board):
        bottom_left, bottom_right, top_left, top_right = (Position(3, 3)), \
                                                         (Position(3, board.height - 3)), \
                                                         (Position(board.width - 3, 3)), \
                                                         (Position(board.width - 3, board.height - 3))
        corners = []
        corners.extend((bottom_left, bottom_right, top_left, top_right))
        enemy_heads = [snake.get_head() for snake in snakes if snake.get_head() is not my_head]
        my_close_food = corners[0]
        my_dist_to_best_corner = Distance.manhattan_dist(my_close_food, my_head)
        for food in corners:
            enemy_dist_to_food = min([Distance.manhattan_dist(food, head) for head in enemy_heads])
            my_dist_to_food = Distance.manhattan_dist(food, my_head)
            if my_dist_to_food <= enemy_dist_to_food and my_dist_to_food <= my_dist_to_best_corner:
                my_close_food = food
                my_dist_to_best_corner = my_dist_to_food
        return my_close_food

    @staticmethod
    def hide_in_corner(board: BoardState, you: Snake, grid_map):

        head = you.get_head()
        tail = you.get_tail()

        # get the best corner
        corner = Anxious._get_relevant_corner(head, board.snakes, board)

        possible_actions = you.possible_actions()
        valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, you, grid_map)
        next_action = valid_actions[0]
        if not valid_actions:
            print("Keine validen ACtions!!!!!!!!!!!!")
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
    def avoid_enemy(valid_actions: List[Direction], my_snake: Snake, snakes: List[Snake]) -> Position:
        enemy_heads = [snake.get_head() for snake in snakes if snake.snake_id is not my_snake.snake_id]
        cost = 0
        my_head = my_snake.get_head()
        best_action = None
        corners = [Position(1, 1), Position(1, 13), Position(13, 1), Position(13, 13)]
        alpha = 1
        beta = 4

        for action in valid_actions:
            next_position = my_head.advanced(action)

            distance_snakes = sum([Distance.manhattan_dist(next_position, enemy_head) for enemy_head in enemy_heads])
            distance_corners = sum([Distance.manhattan_dist(next_position, corner) for corner in corners])
            distance = alpha * distance_snakes + beta * distance_corners
            if distance > cost:
                cost = distance
                best_action = action
        return best_action