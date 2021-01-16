import numpy as np
from typing import List, Dict
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
#  - valid_boards für alle Richtungen addieren und schwerpunkt berechnen
#  - Länge der Pfade in Distanz wert mit einbeziehen
#  - negativer Floodfill für nahe gegner


class Anxious:

    @staticmethod
    def avoid_enemy(my_snake: Snake, board: BoardState, grid_map: GridMap, valid_actions: List[Direction],
                    action_plan: ActionPlan, direction_depth: Dict) -> Direction:

        if not valid_actions:
            possible_actions = my_snake.possible_actions()
            valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, my_snake,
                                                           grid_map, avoid_food=False)

        num_snakes = 4 - len(board.snakes)
        flood_dist = 6 if len(board.snakes) > 2 else 99

        my_head = my_snake.get_head()
        enemy_heads = [snake.get_head() for snake in board.snakes if snake.snake_id != my_snake.snake_id]

        middle = Position(int(board.height / 2), int(board.width / 2))
        corners = [Position(0, 0), Position(0, board.width), Position(board.height, 0), Position(board.height,
                                                                                                 board.width)]

        escape_cost_dict = action_plan.escape_lane(my_head, valid_actions)

        # TODO: Unterscheidung der Params in Late game und early game abhängig von anzahl der Schlangen
        p_head = Params_Anxious.ALPHA_DISTANCE_ENEMY_HEAD[num_snakes] * (-1)
        p_corner = Params_Anxious.BETA_DISTANCE_CORNERS[num_snakes]
        p_mid = Params_Anxious.THETA_DISTANCE_MID[num_snakes] * (-1)
        p_border = Params_Anxious.EPSILON_NO_BORDER[num_snakes]

        p_food = (Params_Anxious.GAMMA_DISTANCE_FOOD[num_snakes] * 20 / my_snake.health)
        p_flood_min = Params_Anxious.OMEGA_FLOOD_FILL_MIN[num_snakes] * (-1)
        p_flood_max = Params_Anxious.OMEGA_FLOOD_FILL_MAX[num_snakes]
        p_flood_dead = Params_Anxious.OMEGA_FLOOD_DEAD[num_snakes]

        p_corridor = Params_Anxious.RHO_ESCAPE_CORRIDOR[num_snakes] * (-1)
        p_length = Params_Anxious.TAU_PATH_LENGTH[num_snakes]

        total_cost = np.array([], dtype=np.float64)
        direction_cost = np.zeros(10)

        for action in valid_actions:

            next_position = my_head.advanced(action)

            # calculate flood fill
            flood_fill_value, relevant_food = FloodFill.get_fill_stats(board, next_position, my_snake.snake_id)
            enemy_flood = sum([flood_fill_value[snake.snake_id] for snake in board.snakes
                               if snake.snake_id != my_snake.snake_id
                               and Distance.manhattan_dist(snake.get_head(), my_head) < flood_dist])

            # calculate all costs for heuristics
            direction_cost[0] = direction_depth[action] * p_length

            direction_cost[1] = escape_cost_dict[action] * p_corridor

            direction_cost[2] = ActionPlan.punish_border_fields(next_position, my_head, grid_map.width,
                                                                grid_map.height) * p_border

            direction_cost[3] = sum([Distance.manhattan_dist(next_position, enemy_head)
                                     for enemy_head in enemy_heads]) * p_head

            direction_cost[4] = sum([Distance.manhattan_dist(next_position, corner)
                                     for corner in corners
                                     if Distance.manhattan_dist(next_position, corner) < 9]) * p_corner

            direction_cost[5] = Distance.manhattan_dist(next_position, middle) * p_mid

            direction_cost[6] = flood_fill_value[my_snake.snake_id] * p_flood_max
            direction_cost[7] = enemy_flood * p_flood_min

            direction_cost[8] = len(relevant_food) * p_food

            # extra points for killing enemy snake
            if num_snakes == 1:

                enemy_id = [snake.snake_id for snake in board.snakes if snake.snake_id != my_snake.snake_id][0]
                if flood_fill_value[enemy_id] < 20:
                    flood_kill_value = (20 - flood_fill_value[enemy_id]) * 1000
                    direction_cost[9] = flood_kill_value * p_flood_dead

            total_cost = np.append(total_cost, direction_cost.sum())
            direction_cost = np.zeros(10)

        if valid_actions:
            best_action = valid_actions[int(np.argmax(total_cost))]
            print(best_action)
        else:
            best_action = None

        return best_action
