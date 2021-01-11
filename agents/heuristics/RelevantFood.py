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

        # TODO: Richtiges Food fixen
        for food in all_food:
            enemy_dist_to_food = min([Distance.manhattan_dist(food, head) for head in enemy_heads])
            my_dist_to_food = Distance.manhattan_dist(food, my_head)

            if food.x == 0 or food.y == 0 or food.x == width-1 or food.y == height-1:
                enemy_dist_to_me = min([Distance.manhattan_dist(head, my_head) for head in enemy_heads])
                if len(all_food) > 1:
                    continue
                if enemy_dist_to_me < 4 and my_snake.health < 15:
                    continue

            my_close_food.append(food)

        if not my_close_food:
            my_close_food = all_food

        return my_close_food

    @staticmethod
    def check_relevant_food(valid_board, foods):
        # TODO: Checken ob das reicht oder mit Floodfill und dem Head ausweiten
        reachable = False
        for food in foods:
            if valid_board[food.x][food.y] < 0:
                reachable = True

        return reachable
