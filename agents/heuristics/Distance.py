import math
from environment.Battlesnake.model.Position import Position


class Distance:

    @staticmethod
    def manhattan_dist(pos1, pos2) -> int:
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    @staticmethod
    def euclidean_distance(p1: Position, p2: Position) -> float:
        euc_dist = math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
        return euc_dist
