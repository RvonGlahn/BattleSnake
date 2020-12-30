import numpy as np
from typing import List, Dict, Tuple
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
            base_board: np.ndarray
    ):
        self.value_board = base_board

    def _evaluate_corridor(self, direction: Direction, x: int, y: int) -> int:

        # check if corridor is valid
        if x == 0:
            x += 1
        elif x == self.value_board.shape[0]-1:
            x -= 1
        if y == 0:
            y += 1
        elif y == self.value_board.shape[1]-1:
            y -= 1

        if direction == Direction.UP:
            return np.sum(self.value_board[0:x, y]) + np.sum(self.value_board[0:x, y-1]) + \
                   np.sum(self.value_board[0:x, y+1])

        if direction == Direction.DOWN:
            return np.sum(self.value_board[x+1:, y]) + np.sum(self.value_board[x+1:, y-1]) + \
                   np.sum(self.value_board[x+1:, y+1])

        if direction == Direction.LEFT:
            return np.sum(self.value_board[x, 0:y]) + np.sum(self.value_board[x-1, 0:y]) + \
                   np.sum(self.value_board[x+1, 0:y])

        if direction == Direction.RIGHT:
            return np.sum(self.value_board[x, y+1:]) + np.sum(self.value_board[x - 1, y+1:]) + \
                   np.sum(self.value_board[x + 1, y+1:])

    def _add_movement_prediction(self):
        pass

    def escape_lane(self, my_head: Position, valid_actions: List[Direction]) -> Tuple[Dict, Direction]:
        cost = 0
        cost_dict = {}
        best_direction: Direction = None
        x, y = my_head.x, my_head.y
        # add movement_profile

        for direction in valid_actions:
            new_cost = self._evaluate_corridor(direction, x, y)
            cost_dict[direction] = new_cost
            if new_cost < cost:
                cost = new_cost
                best_direction = direction

        return cost_dict, best_direction

    def _calculate_provocate_cost(self, grid_map: GridMap) -> None:
        pass

    def provocate_lane(self) -> Direction:
        pass
