import math
from typing import Tuple, List, Optional
from agents.heuristics.RelevantFood import RelevantFood
from agents.heuristics.Distance import Distance

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap
from util.kl_priority_queue import KLPriorityQueue


class Search:

    @staticmethod
    def follow_food(snake: Snake, board: BoardState, grid_map: GridMap) -> List[Tuple[Position, Direction]]:
        head = snake.get_head()
        food = None

        relevant_foods = RelevantFood.get_relevant_food(head, board.snakes, board.food)

        start_distance = 0

        # get food that is the futhest away from enemies heads
        for relevant_food in relevant_foods:
            distance = min([Distance.manhattan_dist(enemy.get_head(), relevant_food) for enemy in board.snakes if
                            enemy.get_head() is not head])
            if distance > start_distance:
                food = relevant_food

        cost, path = Search.a_star_search(head, food, board, grid_map)
        path_array = path

        return path_array

    @staticmethod
    def reverse_direction(d):
        if d == Direction.UP:
            return Direction.DOWN
        elif d == Direction.LEFT:
            return Direction.RIGHT
        elif d == Direction.RIGHT:
            return Direction.LEFT
        elif d == Direction.DOWN:
            return Direction.UP

    @staticmethod
    def a_star_search(start_field: Position,
                      search_field: Position,
                      board: BoardState,
                      grid_map: GridMap) -> Tuple[int, List[Tuple[Position, Direction]]]:
        print(start_field, search_field, "\n")

        queue = KLPriorityQueue()
        came_from = {}  # current node ist key parent ist value
        cost_so_far = {str(start_field): 0}  # summierte Kosten

        current_position = start_field

        first = True

        while not queue.empty() or first:
            first = False
            # Check if Current Position is goal state
            if current_position == search_field:
                break

            # append cost for each unvisited valid direction
            for direction in Direction:
                next_position = current_position.advanced(direction)
                if grid_map.is_valid_at(next_position.x, next_position.y):

                    # check if state wasnt visited or cost of visited state is lower
                    if (str(next_position) not in cost_so_far.keys()) \
                            or (cost_so_far[str(current_position)] < cost_so_far[str(next_position)]):

                        cost_so_far[str(next_position)] = cost_so_far[str(current_position)] + 1
                        cost = Distance.euclidean_distance(search_field, next_position) + cost_so_far[str(next_position)]
                        queue.put(cost, (next_position, direction))

            # Get best position from Priority Queue
            pos_dir_tuple = queue.get()
            best_position = pos_dir_tuple[0]
            best_direction = pos_dir_tuple[1]

            # reverse direction to get poistion where we came from
            opposite_direction = Search.reverse_direction(best_direction)

            # only use undiscovered nodes
            if best_position not in came_from:
                came_from[best_position] = (best_position.advanced(opposite_direction), best_direction)
            current_position = best_position

        # Berechnung des Pfades anhand von came_from
        cost = cost_so_far[str(current_position)]
        path: List[Tuple[Position, Direction]] = []
        while not current_position == start_field:
            path.append(came_from[current_position])
            current_position = came_from[current_position][0]
        path = path[::-1]

        return cost, path
