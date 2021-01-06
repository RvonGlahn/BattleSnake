from typing import List, Dict
import numpy as np
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState


class FloodFill:

    def calcuate_circle(self):
        pass

    @staticmethod
    def get_fill_stats(board: BoardState) -> Dict:

        calculating = True
        fill_stats = {}
        fill_board = np.zeros(board.width, board.height)

        snake_heads = {snake.snake_id: snake.get_head() for snake in board.snakes}
        snake_length = [snake.get_length() for snake in board.snakes]
        snake_ids = [snake.snake_id for snake in board.snakes]
        order = np.argsort(snake_length)

        snakes = board.snakes.copy()
        snakes = [snakes[i] for i in order]

        # iterativ Kreise um Schlange ziehen
        depth = 1
        while calculating:
            # größte Schlange zuwerst
            for snake in snakes:
                FloodFill.calcuate_circle(snake.get_head(), depth)
                # wie in valid actionsn ur erreichbare Felder markieren
                # wenn alle Felder verteilt auffüllen
                depth += 1
        return fill_stats

