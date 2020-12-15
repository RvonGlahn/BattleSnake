import math
from environment.Battlesnake.model.Position import Position
from typing import List


class Distance:

    @staticmethod
    def manhattan_dist(pos1, pos2) -> int:

        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    @staticmethod
    def euclidean_distance(p1: Position, p2: Position) -> float:

        euc_dist = math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
        return euc_dist

    @staticmethod
    def path_similarity(pred_path: List[Position], real_path: List[Position]):

        # adjust path length expects path with different length but same starting position
        if len(pred_path) > len(real_path):
            pred_path = pred_path[:len(real_path)]
        if len(real_path) > len(pred_path):
            path2 = real_path[:len(pred_path)]

        cost = 0
        for pos1, pos2 in zip(pred_path, real_path):
            cost += Distance.manhattan_dist(pos1[0], pos2)
        return cost

    @staticmethod
    def dist_to_closest_enemy_head(snakes, you):
        dist = min([Distance.manhattan_dist(snake.get_head(), you.get_head())
                    for snake in snakes if snake.snake_id != you.snake_id])
        return dist
