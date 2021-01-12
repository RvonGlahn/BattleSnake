from typing import Tuple, List
import numpy as np

from agents.heuristics.RelevantFood import RelevantFood
from agents.heuristics.Distance import Distance
from agents.gametree.AStar import AStar
from agents.heuristics.ValidActions import ValidActions
from agents.SnakeAutomat import SnakeAutomat

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap


class Hungry:

    @staticmethod
    def follow_food(snake: Snake, board: BoardState, grid_map: GridMap, reachable_food: List[Position]) \
            -> List[Tuple[Position, Direction]]:
        my_head = snake.get_head()
        food = None

        relevant_foods = RelevantFood.get_relevant_food(snake, board.snakes, reachable_food, board.width, board.height)
        print("Relevant Food:", food)
        if not relevant_foods:
            return []

        start_distance = 99
        # get food that is nearest to my head
        for relevant_food in relevant_foods:
            distance = Distance.manhattan_dist(my_head, relevant_food)
            if distance < start_distance:
                food = relevant_food
                start_distance = distance
        print("best food:", food)
        if not food or start_distance > 15:
            return []
        cost, path = AStar.a_star_search(my_head, food, board, grid_map)
        path_array = path

        return path_array

    @staticmethod
    def hunger(snake: Snake, board: BoardState, grid_map: GridMap, food_path: List[Position],
               valid_actions: List[Direction], my_automat: SnakeAutomat) -> Tuple[Direction, List[Position]]:

        possible_actions = snake.possible_actions()
        back_up_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, snake, grid_map, False)

        if valid_actions:
            action = np.random.choice(valid_actions)
        else:
            action = np.random.choice(back_up_actions)

        if not food_path:
            food_path = Hungry.follow_food(snake, board, grid_map, my_automat.reachable_food)
        if food_path:
            print("Food_Path: ", food_path)
            if food_path[0][1] in valid_actions:
                print("Läuft")
                action = food_path[0][1]
                food_path.pop(0)
            """
            elif snake.health < 10 and food_path[0][1] in back_up_actions:
                action = food_path[0][1]
                food_path.pop(0)
            """
        else:
            food_path = []
        print(action)

        return action, food_path
