import numpy as np
from typing import List, Dict, Tuple

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Direction import Direction


class ActionPlan:

    def __init__(
            self,
            base_board: np.ndarray
    ):
        self.value_board = base_board

    def _evaluate_corridor(self, direction: Direction, x: int, y: int):

        # TODO: Breite der Lane einbeziehen ohne Gegner
        #  Fluchtweg einberechnen. Pfad muss mind. 2 breit sein
        #  check if corridor is valid
        #  corridor auf 5 beschränken
        x_max, y_max = self.value_board.shape[0]-1, self.value_board.shape[1]-1

        # handle boundary points
        if x == 0:
            x += 1
        elif x == x_max:
            x -= 1
        if y == 0:
            y += 1
        elif y == y_max:
            y -= 1

        x_lower = x-5 if x > 5 else 0
        x_upper = x+5 if x < x_max-5 else x_max
        y_lower = y-5 if y > 5 else 0
        y_upper = y+5 if y < y_max-5 else y_max

        if direction == Direction.LEFT:
            lane = np.sum(self.value_board[x_lower:x, y])

            corridor = lane + np.sum(self.value_board[x_lower:x, y-1]) + np.sum(self.value_board[x_lower:x, y+1])
            norm_corridor = corridor / (x - x_lower)

            return lane, norm_corridor

        if direction == Direction.RIGHT:
            lane = np.sum(self.value_board[x+1:x_upper, y])

            corridor = lane + np.sum(self.value_board[x+1:x_upper, y-1]) + np.sum(self.value_board[x+1:x_upper, y+1])
            norm_corridor = corridor / (x_upper - x)

            return lane, norm_corridor

        if direction == Direction.DOWN:
            lane = np.sum(self.value_board[x, y_lower:y])

            corridor = lane + np.sum(self.value_board[x-1, y_lower:y]) + np.sum(self.value_board[x+1, y_lower:y])
            norm_corridor = corridor / (y - y_lower)

            return lane, norm_corridor

        if direction == Direction.UP:
            lane = np.sum(self.value_board[x, y+1:y_upper])

            corridor = lane + np.sum(self.value_board[x - 1, y+1:y_upper]) + np.sum(self.value_board[x + 1, y+1:y_upper])
            norm_corridor = corridor / (y_upper - y)

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

        return cost_dict

    @staticmethod
    def punish_border_fields(next_position: Position, my_head: Position, width: int, height: int) -> int:
        distance_no_border = 0

        if next_position.x == 0 or next_position.y == 0 or next_position.x == width - 1 \
                or next_position.y == height - 1:
            distance_no_border = -10000
        if next_position.x == 1 and my_head.x != 0:
            distance_no_border = -2500
        if next_position.y == 1 and my_head.y != 0:
            distance_no_border = -2500
        if next_position.x == width - 2 and my_head.x != width - 1:
            distance_no_border = -2500
        if next_position.y == height - 2 and my_head.x != height - 1:
            distance_no_border = -2500

        return distance_no_border

