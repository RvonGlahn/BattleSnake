from typing import List
import numpy as np
from agents.BaseAgent import BaseAgent
from agents.Decision import Decision
from agents.heuristics.ValidActions import ValidActions

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
        self.food_path: List[Position] = []
        self.Decision = Decision()
        self.Decision.set_up_automats(you, board.snakes)
        self.Decision.set_default_board(board.width, board.height)

    def move(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake) -> MoveResult:

        grid_map: GridMap[Occupant] = board.generate_grid_map()

        self.Decision.set_round(turn)
        next_action = self.Decision.decide(you, board, grid_map)

        if next_action is None:
            next_action = ValidActions.get_valid_actions(board, you.possible_actions(), board.snakes, you, grid_map)
            if next_action is None:
                next_action = np.random.choice(you.possible_actions())

        return MoveResult(direction=next_action)

    def end(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        self.food_path = []
        self.first = True


