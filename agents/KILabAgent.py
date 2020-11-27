import math
from typing import Tuple, List, Optional
from agents.BaseAgent import BaseAgent
import numpy as np

from environment.Battlesnake.helper.DirectionUtil import DirectionUtil
from environment.Battlesnake.model.GameInfo import GameInfo
from environment.Battlesnake.model.MoveResult import MoveResult
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Occupant import Occupant
from util.kl_priority_queue import KLPriorityQueue
import time

class KILabAgent(BaseAgent):

    def get_name(self):
        return 'Rettan'

    def start(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        pass

    def move(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake) -> MoveResult:

        grid_map: GridMap[Occupant] = board.generate_grid_map()

        food_action = self.follow_food(you, board, grid_map)
        if food_action is not None:
            return MoveResult(direction=food_action)

        possible_actions = you.possible_actions()
        random_action = np.random.choice(possible_actions)
        return MoveResult(direction=random_action)

    def end(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        pass

    def follow_food(self, snake: Snake, board: BoardState, grid_map: GridMap):

        head = snake.get_head()

        for food in board.food:
            start_time = time.time()
            distance, path = KILabAgent.a_star_search(head, food, board, grid_map)
            print("--- %s seconds ---" % (time.time() - start_time))

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
    def euclidean_heuristic(p1: Position, p2: Position) -> float:
        euc_dist = math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2)
        return euc_dist

    @staticmethod
    def a_star_search(start_field: Position,
                      search_field: Position,
                      board: BoardState,
                      grid_map: GridMap) -> Tuple[int, List[Tuple[Position, Direction]]]:
        print(start_field, search_field, "\n")

        queue = KLPriorityQueue()
        came_from = {}                  # current node ist key parent ist value
        cost_so_far = {str(start_field): 0}                # summierte Kosten

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
                    if (str(next_position) not in cost_so_far.keys()) or (cost_so_far[str(current_position)] < cost_so_far[str(next_position)]):
                        cost_so_far[str(next_position)] = cost_so_far[str(current_position)] + 1
                        cost = KILabAgent.euclidean_heuristic(search_field, next_position) + cost_so_far[str(next_position)]
                        queue.put(cost, (next_position, direction))
            # Get best position from Priority Queue
            pos_dir_tuple = queue.get()
            best_position = pos_dir_tuple[0]
            best_direction = pos_dir_tuple[1]
            # reverse direction to get poistion where we came from
            opposite_direction = KILabAgent.reverse_direction(best_direction)
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
