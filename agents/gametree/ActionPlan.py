import numpy as np
from typing import List, Dict
# import numba

from agents.States import States
from agents.heuristics.Distance import Distance
from agents.SnakeAutomat import SnakeAutomat

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Direction import Direction


class ActionPlan:

    def __init__(
            self,
            grid_map: GridMap,
            state: States,
            base_board: np.ndarray
    ):
        self.value_board = base_board

        if state == States.ANXIOUS:
            self._calculate_escape_board(grid_map)
        if state == States.PROVOCATIVE:
            self._calculate_provocate_board(grid_map)

    def _calculate_escape_board(self, grid_map: GridMap) -> None:
        pass

    def _calculate_provocate_board(self, grid_map: GridMap) -> None:
        pass

    def _evaluate_corridor(self) -> None:
        # width, length, snake_heads near corridor
        pass

    def _add_relevant_snake(self, snake, snake_automat: SnakeAutomat) -> None:
        pass

    def escape_lane(self, snakes: List[Snake], automats: Dict) -> Direction:
        pass

    def provocate_lane(self) -> Direction:
        pass
