from typing import Tuple, List, Optional
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.grid_map import GridMap
from agents.heuristics.Distance import Distance
from agents.gametree.AStar import AStar
from agents.heuristics.ValidActions import ValidActions
import numpy as np

class SoloSurvival:

    @staticmethod
    def next_step(snake: Snake, board: BoardState, grid_map: GridMap) -> Direction:

        head = snake.get_head()
        middle = Position(board.height // 2, board.width // 2)
        valid = []
        for direction in Direction:
            if not head.advanced(direction) in snake.get_body():
                valid.append(direction)

        if middle in snake.get_body():
            need, next_direction = SoloSurvival.need_food(snake, board)
            if need:
                if next_direction in valid:
                    return next_direction
                else:
                    return np.random.choice(valid)
            else:
                next_direction = SoloSurvival.tail_gate(snake, board, grid_map)
                if next_direction in valid:
                    return next_direction
                else:
                    return np.random.choice(valid)

        else:
            _, path = AStar.a_star_search_wofood(head, middle, board, grid_map)
            _, next_direction = path[0]
        if next_direction in valid:
            return next_direction
        else:
            return np.random.choice(valid)

    @staticmethod
    def need_food(snake: Snake, board: BoardState) -> Tuple[bool, Optional[Direction]]:

        health = snake.get_health()
        food_around = SoloSurvival.food_all_around_body(snake, board)
        if health < 10:
            if food_around:
                if health == 1:
                    _, food_pos = SoloSurvival.best_food_around_body(snake, board)
                    food_dir = SoloSurvival.direction_to_food(snake, food_pos)
                    return True, food_dir
            else:
                dist, food_pos = SoloSurvival.best_food_around_body(snake, board)
                if (health - dist) == 0:
                    food_dir = SoloSurvival.direction_to_food(snake, food_pos)
                    return True, food_dir
                else:
                    dist, food_pos = SoloSurvival.find_next_food(snake, board)
                    if dist <= health:
                        food_dir = SoloSurvival.direction_to_food(snake, food_pos)
                        return True, food_dir
        else:
            return False, None

    @staticmethod
    def tail_gate(snake: Snake, board: BoardState, grid_map : GridMap) -> Direction:

        head = snake.get_head()
        tail = snake.get_tail()
        body = snake.get_body()
        print("tail ",tail)
        distance = Distance.manhattan_dist(head, tail)
        if distance == 1:
            for direction in Direction:
                if head.advanced(direction) == tail:
                    return direction
        else:
            #cost, path = AStar.a_star_search_wofood(head, tail, board, grid_map)
            #_, next_direction = path[0]
            dist = 9999
            next_direction = None
            for direction in Direction:
                advanced_head = head.advanced(direction)
                d = Distance.manhattan_dist(advanced_head, tail)
                if advanced_head not in body:
                    if d < dist:
                        dist = d
                        next_direction = direction

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
                    foods.append((length - position), part)
            position += 1
        best_dist = 999999
        best_food = None
        for dist, food in foods:
            if (dist == snake.get_length()) and (health <= 1):
                return 1, food
            if dist < best_dist and dist <= health:
                if dist == health:
                    return dist, food
                best_dist = dist
                best_food = food
        return best_dist, best_food

    @staticmethod
    def find_next_food(snake: Snake, board: BoardState) -> Optional[Tuple[int, Position]]:

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

    @staticmethod
    def direction_to_food(snake: Snake, food: Position) -> Optional[Direction]:

        head = snake.get_head()
        for direction in Direction:
            if head.advanced(direction) == food:
                return direction
        return None
