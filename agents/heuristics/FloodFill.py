from typing import Dict, Tuple, List
import numpy as np

from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Position import Position


class FloodFill:

    @staticmethod
    def closed_in():
        pass

    @staticmethod
    def flood_food(fill_board, foods, index):
        reachable_food = []
        for food in foods:
            if fill_board[food.x][food.y] == index:
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

            if fill_board[x][y] != 10 and fill_board[x][y] not in [-99, -98, -97, -50, -49, -48, -47]:
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
    def get_fill_stats(board: BoardState, next_position: Position, my_id: str, new_pos: bool) -> Tuple[Dict,
                                                                                                       List[Position]]:
        # TODO: Food in der Gewichtung des boards einbeziehen

        flood_queue = []
        fill_stats = {}
        fill_board = np.full((board.width, board.height), 10)
        visited = []
        no_food = False if Position(next_position.x, next_position.y) in board.food else True

        snake_length = [snake.get_length() for snake in board.snakes]
        snake_ids = [snake.snake_id for snake in board.snakes]
        order = np.argsort(snake_length)

        copy_snakes = board.snakes.copy()
        snakes = [copy_snakes[i] for i in order][::-1]
        snake_ids = [snake_ids[i] for i in order][::-1]

        snake_marker = -99
        for snake in snakes:
            if snake.snake_id == my_id:
                flood_queue.append([(next_position.x, next_position.y)])
                if new_pos:
                    snake.body.insert(0, next_position)
                    if no_food:
                        del snake.body[-1]
                snake_marker = -50
            else:
                flood_queue.append([(snake.get_head().x, snake.get_head().y)])
            for pos in snake.body:
                fill_board[pos.x][pos.y] = snake_marker
                if pos is not snake.get_head():
                    visited.append((pos.x, pos.y))

            snake_marker += 1
            fill_stats[snake.snake_id] = 0

        # iterativ Bewegungsbereich erschließen
        my_index = 0
        count = 1
        while any(flood_queue):

            snake_index = 0

            # Tail iterativ freigeben
            idx = 0
            for snakey in snakes:
                if snakey.get_length() > count:
                    fill_board[snakey.body[-count].x][snakey.body[-count].y] = 10
                    if (snakey.body[-count].x, snakey.body[-count].y) in visited:
                        visited.remove((snakey.body[-count].x, snakey.body[-count].y))
                        # flood_queue[idx].append((snakey.body[-(count + 1)].x, snakey.body[-(count + 1)].y))
                idx += 1

            # größte Schlange zuerst
            for snake_id in snake_ids:
                filled_fields_count = FloodFill.calcuate_step(fill_board, flood_queue, snake_index, visited)

                fill_stats[snake_id] += filled_fields_count

                if snake_id == my_id:
                    my_index = snake_index
                snake_index += 1
            count += 1

        reachable_food = FloodFill.flood_food(fill_board, board.food, my_index)
        return fill_stats, reachable_food
