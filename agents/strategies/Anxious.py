import numpy as np
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position

from agents.Hyperparameters import Params_Anxious
from agents.heuristics.Distance import Distance
from agents.heuristics.ValidActions import ValidActions


class Anxious:

    @staticmethod
    def avoid_enemy(my_snake: Snake, board: BoardState, grid_map: GridMap) -> Direction:

        possible_actions = my_snake.possible_actions()
        print("Possible Actions:", possible_actions)
        valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, my_snake, grid_map)
        print("Valid Actions:", valid_actions)
        my_head = my_snake.get_head()
        enemy_heads = [snake.get_head() for snake in board.snakes if snake.snake_id != my_snake.snake_id]

        middle = Position(int(board.height/2), int(board.width/2))
        corners = [Position(0, 0), Position(0, board.width), Position(board.height, 0), Position(board.height,
                                                                                                 board.width)]

        alpha = Params_Anxious.ALPHA_DISTANCE_SNAKE
        beta = Params_Anxious.BETA_DISTANCE_CORNERS
        gamma = Params_Anxious.GAMMA_DISTANCE_FOOD
        theta = Params_Anxious.THETA_DISTANCE_MID

        cost = []

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
