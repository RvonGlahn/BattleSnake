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


class KILabAgent(BaseAgent):

    def get_name(self):
        return 'NAME'

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
            distance, path = KILabAgent.a_star_search(head, food, board, grid_map)



    @staticmethod
    def a_star_search(start_field: Position,
                      search_field: Position,
                      board: BoardState,
                      grid_map: GridMap) -> Tuple[int, List[Tuple[Position, Direction]]]:

        queue = KLPriorityQueue()
        came_from = {}
        cost_so_far = {}


        # Berechnung des Pfades
        cost = None
        path: List[Tuple[Position, Direction]] = None


        return cost, path
