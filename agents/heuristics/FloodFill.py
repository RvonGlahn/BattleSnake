from typing import List, Dict
import numpy as np
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState


class FloodFill:

    @staticmethod
    def calcuate_circle(head, depth, fill_board, snake_index):
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

        copy_snakes = board.snakes.copy()
        snakes = [copy_snakes[i] for i in order]

        for snake in snakes:
            for pos in snake.body:
                fill_board[pos.x][pos.y] = 99

        # iterativ Kreise um Schlange ziehen
        depth = 1
        while calculating:
            # größte Schlange zuerst
            snake_index = 0
            for snake in snakes:
                fill_stats = FloodFill.calcuate_circle(snake.get_head(), depth, fill_board, snake_index)
                # wie in valid actions nur erreichbare Felder markieren
                # wenn alle Felder verteilt auffüllen
                snake_index += 1
            depth += 1
        return fill_stats

