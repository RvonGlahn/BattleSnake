from typing import Tuple, List
from agents.heuristics.RelevantFood import RelevantFood
from agents.heuristics.Distance import Distance

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
            distance = min([Distance.manhattan_dist(enemy.get_head(), relevant_food) for enemy in board.snakes if
                            enemy.get_head() is not my_head])
            if distance > start_distance:
                food = relevant_food
        print(food)
        cost, path = AStar.a_star_search(my_head, food, board, grid_map)
        path_array = path
        print(path_array)

        return path_array
