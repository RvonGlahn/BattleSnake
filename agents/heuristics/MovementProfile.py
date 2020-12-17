from typing import List, Tuple

from agents.gametree.AStar import AStar
from agents.heuristics.Distance import Distance

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Position import Direction
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.board_state import GridMap


####################################
# TODO:
# - RNN/LSTM/Transformer? Vorhersage von Zügen mit wenig und schnellem Training
# - metrik für abdrängen: Voronoi/ Death-Lane
####################################


class MovementProfile:
    def __init__(self):
        self.precision: float

    @staticmethod
    def get_food_profiles(head: Position, board: BoardState, grid_map: GridMap) -> List[List[Tuple[Position,
                                                                                                   Direction]]]:
        profiles = []

        for food in board.food:
            if Distance.manhattan_dist(head, food) < 10:
                cost, path = AStar.a_star_search(head, food, board, grid_map)
                profiles.append(path)

        return profiles

    @staticmethod
    def get_head_profiles(head: Position, enemy_heads: List[Position], board: BoardState, grid_map: GridMap) -> \
            List[List[Tuple[Position, Direction]]]:

        profiles = []

        for enemy_head in enemy_heads:
            if Distance.manhattan_dist(head, enemy_head) < 15:
                cost, path = AStar.a_star_search(head, enemy_head, board, grid_map)
                profiles.append(path)

        return profiles

    # mithilfe von Voronoi Diagramm o.Ä. Profil für Feldvorteil der Snake errechnen
    @staticmethod
    def get_bully_profile(self) -> List[Position]:
        pass

    @staticmethod
    def improve_profile():
        pass
