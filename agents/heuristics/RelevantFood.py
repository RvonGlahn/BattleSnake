from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from typing import List
from agents.heuristics.Distance import Distance


class RelevantFood:

    @staticmethod
    def get_relevant_food(my_head: Position, snakes: List[Snake], all_food: List[Position]):
        enemy_heads = [snake.get_head() for snake in snakes if snake.get_head() is not my_head]
        my_close_food = []
        for food in all_food:
            enemy_dist_to_food = min([Distance.manhattan_dist(food, head) for head in enemy_heads])
            my_dist_to_food = Distance.manhattan_dist(food, my_head)
            if my_dist_to_food <= enemy_dist_to_food and my_dist_to_food <= 20:
                my_close_food.append(food)
        return my_close_food
