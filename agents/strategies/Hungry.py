from typing import Tuple, List
import numpy as np

from agents.heuristics.RelevantFood import RelevantFood
from agents.heuristics.Distance import Distance
from agents.heuristics.ValidActions import ValidActions

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap
from agents.gametree.AStar import AStar


class Hungry:

    @staticmethod
    def follow_food(snake: Snake, board: BoardState, grid_map: GridMap) -> List[Tuple[Position, Direction]]:
        my_head = snake.get_head()
        food = None

        relevant_foods = RelevantFood.get_relevant_food(my_head, board.snakes, board.food)

        start_distance = 0

        # get food that is the futhest away from enemies heads
        for relevant_food in relevant_foods:
            distance = min([Distance.manhattan_dist(enemy.get_head(), relevant_food) for enemy in board.snakes
                            if enemy.get_head() is not my_head])
            if distance > start_distance:
                food = relevant_food

        cost, path = AStar.a_star_search(my_head, food, board, grid_map)
        path_array = path

        return path_array

    @staticmethod
    def hunger(snake: Snake, board: BoardState, grid_map: GridMap, food_path: List[Position],
               valid_actions: List[Direction]) -> Tuple[Direction, List[Position]]:

        action: Direction

        if not food_path:
            food_path = Hungry.follow_food(snake, board, grid_map)
        if food_path[0][1] in valid_actions:
            action = food_path[0][1]
            food_path.pop(0)
        else:
            food_path = []
            action = np.random.choice(valid_actions)
        return action, food_path
