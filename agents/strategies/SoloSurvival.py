from typing import Tuple, List
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position

from environment.Battlesnake.model.grid_map import GridMap
from agents.heuristics.Distance import Distance
from agents.gametree.AStar import AStar


class SoloSurvival:

    @staticmethod
    def next_step(snake: Snake, board: BoardState, grid_map: GridMap) -> Direction:

        head = snake.get_head()
        health = snake.get_health()

        middle = Position(board.height // 2, board.width // 2)
        corners = [Position(0, 0), Position(0, board.width), Position(board.height, 0), Position(board.height,
                                                                                                 board.width)]
        if middle in snake.get_body():
            if SoloSurvival.needFood(snake, board):
                #find cheapest way to eat
                pass
            else:
                next_step = SoloSurvival.tailGate(snake, board)
                return next_step
        else:
            _, path = AStar.a_star_search_wofood(head, middle, board, grid_map)
            _, next_direction = path[0]
            return next_direction


    @staticmethod
    def needFood(snake: Snake, board: BoardState) -> Tuple[bool, Position]:

        health = snake.get_health()
        food_around = SoloSurvival.food_all_around_body(snake, board)
        if health < 10:
            if food_around:
                if health == 1:
                    _, food_pos = SoloSurvival.best_food_around_body(snake, board)
                    return True, food_pos
            else:
                dist, food_pos = SoloSurvival.best_food_around_body(snake, board)
                if (health - dist) == 0:
                    return True, food_pos
                else:
                    dist, food_pos = SoloSurvival.find_next_food(snake, board)
                    if dist <= health:
                        return True, food_pos
        else:
            return False, snake.get_head()

    @staticmethod
    def tailGate(snake: Snake, board: BoardState) -> Direction:

        head = snake.get_head()
        tail = snake.get_tail()
        distance = Distance.manhattan_dist(head, tail)
        if distance == 1:
            for direction in Direction:
                if head.advanced(direction) == tail:
                    return direction
        else:
            _, path = AStar.a_star_search_wofood(head, tail, board)
            _, next_direction = path[0]
            return next_direction

    @staticmethod
    def food_all_around_body(snake: Snake, board: BoardState) -> bool:

        body = snake.get_body()
        food_next_to_body = 0
        for part in body:
            thispart = False
            for direction in Direction:
                if board.is_occupied_by_food(part.advanced(direction)):
                    thispart = True
            if thispart:
                food_next_to_body += 1
        if food_next_to_body == len(body):
            return True
        else:
            return False

    @staticmethod
    def best_food_around_body(snake: Snake, board: BoardState) -> Tuple[int, Position]:

        length = snake.get_length()
        health = snake.get_health()
        body = snake.get_body()
        foods = List[Tuple[int, Position]]
        position = 0
        for part in body:
            for direction in Direction:
                if board.is_occupied_by_food(part.advanced(direction)):
                    foods.append(position, part)
            position += 1






    @staticmethod
    def find_next_food(snake: Snake, board: BoardState) -> Tuple[int, Position]:

        head = snake.get_head()
        health = snake.get_health()
        all_food = board.food
        if len(all_food) == 0:
            return None
        best_dist = 99999
        best_food = None
        for food in all_food:
            food_dist = Distance.manhattan_dist(head, food)
            if food_dist == health:
                return food_dist, food
            else:
                diff = (food_dist - health)
                if (best_dist > diff) and diff > 0:
                    best_dist = diff
                    best_food = food
        return best_dist, best_food
