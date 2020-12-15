import numpy as np
import numba


class EscapePlan:

    def __init__(self, width, height, grid_map):
        self.value_board = np.zeros((width, height))
        self._calculate_value_board(grid_map)

    def _get_snake_radius(self):
        pass

    def _calculate_value_board(self,grid_map):
        pass

    def _evaluate_corridor(self):
        # width, length, snake_heads near corridor
        pass

    def add_relevant_snake(self, snake, snake_automat):
        pass

    def escape(self):
        pass

