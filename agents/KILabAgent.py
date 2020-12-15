from typing import List
import numpy as np
from agents.BaseAgent import BaseAgent
from agents.Decision import Decision

from environment.Battlesnake.model.GameInfo import GameInfo
from environment.Battlesnake.model.MoveResult import MoveResult
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Occupant import Occupant


class KILabAgent(BaseAgent):

    def __init__(self):
        self.food_path: List[Position] = []
        self.Decision = Decision()
        self.first = True

    def get_name(self):
        return 'Jürgen'

    def start(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        pass

    def move(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake) -> MoveResult:

        grid_map: GridMap[Occupant] = board.generate_grid_map()

        if self.first:
            print("Init Automats in move")
            self.Decision.set_up_automats(you, board.snakes)
            self.first = False

        self.Decision.set_round(turn)
        next_action = self.Decision.decide(you, board, grid_map, game_info)

        if next_action is None:
            next_action = np.random.choice(you.possible_actions())

        return MoveResult(direction=next_action)

    def end(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        del self.Decision
        del self.food_path
        del self.first
        pass

