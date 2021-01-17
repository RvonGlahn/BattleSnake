from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from typing import List
from agents.heuristics.Distance import Distance


class RelevantFood:

    @staticmethod
    def get_relevant_food(my_snake: Snake, snakes: List[Snake], all_food: List[Position],
                          height: int, width: int) -> List[Position]:
        my_head = my_snake.get_head()

        enemy_heads = [snake.get_head() for snake in snakes if snake.get_head() is not my_head]
        my_close_food = []

        for food in all_food:

            if food.x == 0 or food.y == 0 or food.x == width-1 or food.y == height-1:
                enemy_dist_to_me = min([Distance.manhattan_dist(head, my_head) for head in enemy_heads])
                enemy_dist_to_food = min([Distance.manhattan_dist(head, food) for head in enemy_heads])
                if len(all_food) > 5 and my_snake.health > 50:
                    continue
                if my_snake.health > 25 and enemy_dist_to_food < 2:
                    continue
                if my_snake.health > 70 and enemy_dist_to_food < 2 and enemy_dist_to_me < 2:
                    continue

            my_close_food.append(food)

        if not my_close_food:
            my_close_food = all_food

        return my_close_food

    @staticmethod
    def check_relevant_food(valid_board, foods):
        reachable = False
        for food in foods:
            if valid_board[food.x][food.y] < 0:
                reachable = True

        return reachable
