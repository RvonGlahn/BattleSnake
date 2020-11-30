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
from environment.Battlesnake.model.SnakeState import SnakeState

"""
möglichst in der Mitte bleiben
A-Star nur auswählen wenn health kleiner als X sonst chase tail, oder große Schlangen provozieren
Wahrscheinlichkeit ein Food zu bekommen beachten
Für A-star nur Path zu den nächsten und wahrscheinlichsten Foods berechnen Grenze für zu große Abstände
"""


def manhattan_dist(pos1, pos2):
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


class KILabAgent(BaseAgent):

    def get_valid_actions(self, board, possible_actions, snakes, my_snake, grid_map):
        my_head = my_snake.get_head()
        snake_tails = []
        valid_actions = []

        for snake in snakes:
            snake_tails.append(snake.get_tail())

        for direction in possible_actions:
            next_position = my_head.advanced(direction)

            # outofbounds
            if board.is_out_of_bounds(next_position):
                continue

            # body crash -> ganze Gegner Schlange minus letzten Teil
            if grid_map.get_value_at_position(next_position) is Occupant.Snake and next_position not in snake_tails:
                continue

            # head crash -> Alle möglichen Richtungen des Heads der Gegner Schlange beachten
            for snake in snakes:
                if snake.snake_id is not my_snake.snake_id:
                    if snake.get_length() >= my_snake.get_length():
                        head = snake.get_head()
                        positions_enemy = [head.advanced(action) for action in snake.possible_actions()]
                        if next_position in positions_enemy:
                            continue
            valid_actions.append(direction)

        return valid_actions

    def get_state(self, my_snake, snakes):
        if my_snake.get_length() % 2 == 1:
            for snake in snakes:
                if snake.get_length() >= my_snake.get_length():
                    return SnakeState.INFERIORHUNGRY  # hungry but inferior
            return SnakeState.HUNGRY  # hungry and the largest snake
        if my_snake.get_health() <= 20:
            for snake in snakes:
                if snake.get_length() >= my_snake.get_length():
                    return SnakeState.INFERIORHUNGRY  # hungry but inferior
            return SnakeState.HUNGRY  # hungry and the largest snake
        for snake in snakes:
            if snake.get_length() >= my_snake.get_length():
                return SnakeState.INFERIOR
            else:
                return SnakeState.SUPERIOR

    def bestCorner(self, board: BoardState, you: Snake):

        bottom_left, bottom_right, top_left, top_right = ((), Position(1, 1)), \
                                                         ((), Position(1, board.height - 1)), \
                                                         ((), Position(board.width - 1, 1)), \
                                                         ((), Position(board.width - 1, board.height - 1))
        #get a distance between the corners and enemy snakes
        for snake in board.snakes:
            head = snake.get_head()
            np.append(top_left[0], self.euclidean_heuristic(top_left[1], head))
            np.append(top_right[0], self.euclidean_heuristic(top_right[1], head))
            np.append(bottom_left[0], self.euclidean_heuristic(bottom_left[1], head))
            np.append(bottom_right[0], self.euclidean_heuristic(bottom_right[1], head))

        #sustract your distance to the corners from the value that exists from the distance of the enemy snakes
        your_head = you.get_head()
        bottom_left = (np.abs(np.average(bottom_left[0]) - self.euclidean_heuristic(bottom_left[1], your_head)),
                       Position(1, 1))
        bottom_right = (np.abs(np.average(bottom_right[0]) - self.euclidean_heuristic(bottom_right[1], your_head)),
                        Position(board.width - 1, 1))
        top_left = (np.abs(np.average(top_left[0]) - self.euclidean_heuristic(top_left[1], your_head)),
                    Position(1, board.height - 1))
        top_right = (np.abs(np.average(top_right[0]) - self.euclidean_heuristic(top_right[1], your_head)),
                     Position(board.width - 1, board.height - 1))

        corners = np.zeros(shape=top_left, dtype=np.float64)
        np.append(corners, top_left)
        np.append(corners, top_right)
        np.append(corners, bottom_left)
        np.append(corners, bottom_right)

        best_corner = Position(0, 0)
        value = 0
        #take the best corner
        for corner in corners:
            if corner[0] >= value:
                best_corner = corner[1]
                value = corner[0]

        return best_corner

    def strategy(self, board: BoardState, you: Snake, grid_map):

        """
        :param board:
        :param you:
        :param grid_map:
        :return:
        """

        head = you.get_head()
        tail = you.get_tail()

        corner = self.bestCorner(board, you)

        dist_path_array = []

        # check if any part of the snake is in a corner, if so then chase tail, else go to the best corner
        if corner in you.body:
            print("Chasing Tail")
            dist_path_array.append(KILabAgent.a_star_search(head, tail, board, grid_map))
        else:
            print("Trying to reach Corner")
            dist_path_array.append(KILabAgent.a_star_search(head, corner, board, grid_map))

        return dist_path_array

    def get_name(self):
        return 'Jürgen'

    def start(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        pass

    def move(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake) -> MoveResult:

        grid_map: GridMap[Occupant] = board.generate_grid_map()
        # if health, lenght, usw. < X: -> A-Star Search nur im Notfall
        if self.get_state(you, board.snakes) == SnakeState.HUNGRY or self.get_state(you,
                                                                                    board.snakes) == SnakeState.INFERIORHUNGRY:
            food_action = self.follow_food(you, board, grid_map)
            next_action = food_action
        else:
            next_action = self.strategy(board, you, grid_map)

        """
        possible_actions = you.possible_actions()
        valid_actions = self.get_valid_actions(board, possible_actions, board.snakes, you, grid_map)
        if not valid_actions:
            print("Keine validen ACtions!!!!!!!!!!!!")
        next_action = np.random.choice(valid_actions)
        """

        ########################################
        #
        # Hier kommt die Strategie
        #
        ########################################
        print(next_action)
        return MoveResult(direction=next_action)

    def end(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        pass

    def get_relevant_food(self, my_head, snakes, all_food):
        enemy_heads = [snake.get_head() for snake in snakes if snake.get_head() is not my_head]
        my_close_food = []
        for food in all_food:
            enemy_dist_to_food = min([manhattan_dist(food, head) for head in enemy_heads])
            my_dist_to_food = manhattan_dist(food, my_head)
            if my_dist_to_food <= enemy_dist_to_food and my_dist_to_food <= 10:
                my_close_food.append(food)
        return my_close_food

    def follow_food(self, snake: Snake, board: BoardState, grid_map: GridMap):

        head = snake.get_head()

        relevant_food = self.get_relevant_food(head, board.snakes, board.food)

        dist_path_array = []
        for food in relevant_food:
            # start_time = time.time()
            # Kill thread if it takes too long
            dist_path_array.append(KILabAgent.a_star_search(head, food, board, grid_map))
            # print("--- %s seconds ---" % (time.time() - start_time))
        return dist_path_array

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
        euc_dist = math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
        return euc_dist

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
                        cost = KILabAgent.euclidean_heuristic(search_field, next_position) \
                               + cost_so_far[str(next_position)]
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
