from typing import List, Dict
import numpy as np
import time

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.board_state import BoardState


class FloodFill:

    @staticmethod
    def calcuate_step(fill_board, queue, snake_index, visited):
        x_size, y_size = fill_board.shape
        count = 0
        next_queue = []

        for position in queue[snake_index]:

            if position in visited:
                continue

            if fill_board[position.x][position.y] != 10 and fill_board[position.x][position.y] != -99:
                continue

            fill_board[position.x][position.y] = snake_index
            count += 1

            if position.x > 0 and Position(position.x - 1, position.y) not in visited:
                next_queue.append(Position(position.x - 1, position.y))

            if position.x < (x_size - 1) and Position(position.x + 1, position.y) not in visited:
                next_queue.append(Position(position.x + 1, position.y))

            if position.y > 0 and Position(position.x, position.y - 1) not in visited:
                next_queue.append(Position(position.x, position.y - 1))

            if position.y < (y_size - 1) and Position(position.x, position.y + 1) not in visited:
                next_queue.append(Position(position.x, position.y + 1))

            visited.append(Position(position.x, position.y))

        queue[snake_index] = next_queue

        return count

    @staticmethod
    def get_fill_stats(board: BoardState) -> Dict:

        start_time = time.time()
        flood_queue = []
        fill_stats = {}
        fill_board = np.full((board.width, board.height), 10)
        visited = []

        # snake_heads = {snake.snake_id: snake.get_head() for snake in board.snakes}
        snake_length = [snake.get_length() for snake in board.snakes]
        snake_ids = [snake.snake_id for snake in board.snakes]
        order = np.argsort(snake_length)

        copy_snakes = board.snakes.copy()
        snakes = [copy_snakes[i] for i in order]

        for snake in snakes:
            flood_queue.append([snake.get_head()])
            for pos in snake.body:
                fill_board[pos.x][pos.y] = -99
            fill_stats[snake.snake_id] = 0

        # iterativ Bewegungsbereich erschließen
        while any(flood_queue):
            # größte Schlange zuerst
            snake_index = 0
            for snake_id in snake_ids:
                filled_fields_count = FloodFill.calcuate_step(fill_board, flood_queue, snake_index, visited)

                fill_stats[snake_id] += filled_fields_count

                snake_index += 1
        # calculate fill stats
        print(time.time() - start_time)
        return fill_stats
