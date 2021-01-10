import numpy as np
from typing import List
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position

from agents.Hyperparameters import Params_Anxious
from agents.heuristics.Distance import Distance
from agents.gametree.ActionPlan import ActionPlan
from agents.heuristics.ValidActions import ValidActions
from agents.heuristics.FloodFill import FloodFill

# TODO:
#  - im early game an hungrige Schlangen halten
#  - wenn gegnerische Schlange low health hat dann food blockieren
#  - Chase your Tail in Desperate State wenn eingeschlossen


class Anxious:

    @staticmethod
    def avoid_enemy(my_snake: Snake, board: BoardState, grid_map: GridMap, valid_actions: List[Direction],
                    action_plan: ActionPlan) -> Direction:

        if not valid_actions:
            possible_actions = my_snake.possible_actions()
            valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, my_snake,
                                                           grid_map, False)

        my_head = my_snake.get_head()
        enemy_heads = [snake.get_head() for snake in board.snakes if snake.snake_id != my_snake.snake_id]

        middle = Position(int(board.height / 2), int(board.width / 2))
        corners = [Position(0, 0), Position(0, board.width), Position(board.height, 0), Position(board.height,
                                                                                                 board.width)]

        escape_cost_dict, escape_direction = action_plan.escape_lane(my_head, valid_actions)

        # TODO: Unterscheidung der Params in Late game und early game abhängig von anzahl der Schlangen
        alpha = Params_Anxious.ALPHA_DISTANCE_SNAKE
        beta = Params_Anxious.BETA_DISTANCE_CORNERS
        gamma = Params_Anxious.GAMMA_DISTANCE_FOOD * 20 / my_snake.health
        theta = Params_Anxious.THETA_DISTANCE_MID
        phi = Params_Anxious.PHI_ESCAPE_DIRECTION
        omega_max = Params_Anxious.OMEGA_FLOOD_FILL_MAX
        omega_min = Params_Anxious.OMEGA_FLOOD_FILL_MIN

        cost = []

        for action in valid_actions:
            next_position = my_head.advanced(action)

            escape_value = escape_cost_dict[action]

            no_border = ActionPlan.punish_border_fields(next_position, my_head, grid_map.width, grid_map.height)

            distance_snakes = sum([Distance.manhattan_dist(next_position, enemy_head) for enemy_head in enemy_heads])

            distance_corners = sum([Distance.manhattan_dist(next_position, corner) for corner in corners])

            distance_mid = Distance.manhattan_dist(next_position, middle)

            flood_fill_value, relevant_food = FloodFill.get_fill_stats(board, next_position, my_snake.snake_id)

            distance_food = len(relevant_food)

            if len(board.snakes) > 2:
                distance = omega_max * flood_fill_value[my_snake.snake_id] + alpha * distance_snakes - \
                           gamma * distance_food - theta * distance_mid + no_border
            else:
                # enemy dist to food minimieren
                enemy_id = [snake.snake_id for snake in board.snakes if snake.snake_id != my_snake.snake_id][0]
                if flood_fill_value[enemy_id] < 6:
                    flood_fill_value[enemy_id] = (6 - flood_fill_value[enemy_id]) * -1000
                distance = omega_max * flood_fill_value[my_snake.snake_id] - omega_min * flood_fill_value[enemy_id] - gamma * distance_food

            cost.append(distance)

        if valid_actions:
            best_action = valid_actions[np.argmax(cost)]
            print(best_action)
        else:
            best_action = None

        return best_action
