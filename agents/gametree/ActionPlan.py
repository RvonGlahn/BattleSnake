import numpy as np
from typing import List, Dict, Tuple
# import numba

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Direction import Direction


class ActionPlan:

    def __init__(
            self,
            base_board: np.ndarray
    ):
        self.value_board = base_board

    def _evaluate_corridor(self, direction: Direction, x: int, y: int):

        # TODO: Breite der Lane einbeziehen ohne Gegner
        # Fluchtweg einberechnen. Pfad muss mind. 2 breit sein
        # check if corridor is valid
        if x == 0:
            x += 1
        elif x == self.value_board.shape[0]-1:
            x -= 1
        if y == 0:
            y += 1
        elif y == self.value_board.shape[1]-1:
            y -= 1

        if direction == Direction.LEFT:
            lane = np.sum(self.value_board[0:x, y])

            corridor = lane + np.sum(self.value_board[0:x, y-1]) + np.sum(self.value_board[0:x, y+1])
            norm_corridor = corridor / x

            return lane, norm_corridor

        if direction == Direction.RIGHT:
            lane = np.sum(self.value_board[x+1:, y])

            corridor = lane + np.sum(self.value_board[x+1:, y-1]) + np.sum(self.value_board[x+1:, y+1])
            norm_corridor = corridor / (self.value_board.shape[0]-x)

            return lane, norm_corridor

        if direction == Direction.DOWN:
            lane = np.sum(self.value_board[x, 0:y])

            corridor = lane + np.sum(self.value_board[x-1, 0:y]) + np.sum(self.value_board[x+1, 0:y])
            norm_corridor = corridor / y

            return lane, norm_corridor

        if direction == Direction.UP:
            lane = np.sum(self.value_board[x, y+1:])

            corridor = lane + np.sum(self.value_board[x - 1, y+1:]) + np.sum(self.value_board[x + 1, y+1:])
            norm_corridor = corridor / (self.value_board.shape[1]-y)

            return lane, norm_corridor

    def _add_movement_prediction(self):
        pass

    def escape_lane(self, my_head: Position, valid_actions: List[Direction]) -> Tuple[Dict, Direction]:
        cost = 0
        cost_dict = {}
        best_direction: Direction = None
        x, y = my_head.x, my_head.y
        # add movement_profile

        for direction in valid_actions:
            lane_cost, corridor_cost = self._evaluate_corridor(direction, x, y)
            new_cost = lane_cost + corridor_cost
            cost_dict[direction] = new_cost
            if new_cost < cost:
                cost = new_cost
                best_direction = direction

        return cost_dict, best_direction

    def _calculate_provocate_cost(self, grid_map: GridMap) -> None:
        pass

    def provocate_lane(self) -> Direction:
        pass

    @staticmethod
    def punish_border_fields(next_position: Position, my_head: Position, width: int, height: int) -> int:
        distance_no_border = 0

        if next_position.x == 0 or next_position.y == 0 or next_position.x == width - 1 \
                or next_position.y == height - 1:
            distance_no_border = -99999
        if next_position.x == 1 and my_head.x != 0:
            distance_no_border = -9999
        if next_position.y == 1 and my_head.y != 0:
            distance_no_border = -9999
        if next_position.x == width - 2 and my_head.x != width - 1:
            distance_no_border = -9999
        if next_position.y == height - 2 and my_head.x != height - 1:
            distance_no_border = -9999

        return distance_no_border

