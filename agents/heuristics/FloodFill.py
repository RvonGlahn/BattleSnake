from typing import Dict, Tuple, List
import numpy as np

from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Position import Position


class FloodFill:

    @staticmethod
    def closed_in():
        pass

    @staticmethod
    def flood_food(fill_board, foods):
        reachable_food = []
        for food in foods:
            if fill_board[food.x][food.y] == -50:
                reachable_food.append(food)

        return reachable_food


    @staticmethod
    def calcuate_step(fill_board, queue, snake_index, visited) -> int:
        x_size, y_size = fill_board.shape
        count = 0
        next_queue = []

        for (x, y) in queue[snake_index]:

            if (x, y) in visited:
                continue

            if fill_board[x][y] != 10 and fill_board[x][y] > -40:
                continue

            fill_board[x][y] = snake_index
            count += 1

            if x > 0 and (x - 1, y) not in visited:
                next_queue.append((x - 1, y))

            if x < (x_size - 1) and (x + 1, y) not in visited:
                next_queue.append((x + 1, y))

            if y > 0 and (x, y - 1) not in visited:
                next_queue.append((x, y - 1))

            if y < (y_size - 1) and (x, y + 1) not in visited:
                next_queue.append((x, y + 1))

            visited.append((x, y))

        queue[snake_index] = next_queue

        return count

    @staticmethod
    def get_fill_stats(board: BoardState, next_position: Position, my_id: str) -> Tuple[Dict, List[Position]]:
        # TODO: Food in der Gewichtung des boards einbeziehen

        flood_queue = []
        fill_stats = {}
        fill_board = np.full((board.width, board.height), 10)
        visited = []

        snake_length = [snake.get_length() for snake in board.snakes]
        snake_ids = [snake.snake_id for snake in board.snakes]
        order = np.argsort(snake_length)

        copy_snakes = board.snakes.copy()
        snakes = [copy_snakes[i] for i in order]

        # TODO: Body Überprüfen für meine Schlange
        snake_marker = -99
        for snake in snakes:
            if snake.snake_id == my_id:
                flood_queue.append([(next_position.x, next_position.y)])
                snake_marker = -50
            else:
                flood_queue.append([(snake.get_head().x, snake.get_head().y)])
            for pos in snake.body:
                if snake.snake_id == my_id and pos == snake.body[-1]:
                    continue
                fill_board[pos.x][pos.y] = snake_marker
                if pos is not snake.get_head():
                    visited.append((pos.x, pos.y))

            snake_marker += 1
            fill_stats[snake.snake_id] = 0

        # iterativ Bewegungsbereich erschließen
        while any(flood_queue):
            # größte Schlange zuerst
            snake_index = 0
            for snake_id in snake_ids:
                filled_fields_count = FloodFill.calcuate_step(fill_board, flood_queue, snake_index, visited)

                fill_stats[snake_id] += filled_fields_count

                snake_index += 1

        reachable_food = FloodFill.flood_food(fill_board, board.food)

        print(fill_board)
        # calculate fill stats
        return fill_stats, reachable_food
