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
    def path_similarity(path1: List[Position], path2: List[Position]):

        # adjust path length expects path with different length but same starting position
        if len(path1) > len(path2):
            path1 = path1[:len(path2)]
        if len(path2) > len(path1):
            path2 = path2[:len(path1)]

        cost = 0
        for pos1, pos2 in zip(path1, path2):
            cost += Distance.manhattan_dist(pos1, pos2)
        return cost

    def min_distance_to_enemy_heads(self):
        pass
