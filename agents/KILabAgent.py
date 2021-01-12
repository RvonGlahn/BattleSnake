from typing import List
import numpy as np
import time
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
        self.food_path: List[Position] = []
        self.Decision = Decision()
        self.Decision.set_up_automats(you, board.snakes)
        self.Decision.set_default_board(board.width, board.height)

    def move(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake) -> MoveResult:
        if you.latency:
            # time_available = game_info.timeout/1000 - you.latency
            print("Latency", you.latency)
        start_time = time.time()
        grid_map: GridMap[Occupant] = board.generate_grid_map()

        self.Decision.set_round(turn)
        next_action = self.Decision.decide(you, board, grid_map)

        if not next_action:
            possible_actions = you.possible_actions()
            for action in possible_actions:
                next_position = you.get_head().advanced(action)
                for snake in board.snakes:
                    if next_position == snake.get_tail() and snake.health != 100:
                        next_action = action
            if not next_action:
                next_action = np.random.choice(possible_actions)
        print("Move-DAUER: ", time.time() - start_time)
        return MoveResult(direction=next_action)

    def end(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        self.food_path = []
        self.first = True


