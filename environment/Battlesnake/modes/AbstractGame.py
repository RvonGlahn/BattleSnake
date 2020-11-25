from typing import List, Optional, Dict
from abc import abstractmethod

from environment.Battlesnake.model import GameInfo
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.helper.helper import Helper


class AbstractGame:

    def __init__(self, game_info: GameInfo):

        self.state: Optional[BoardState] = None
        self.game_info: GameInfo = game_info
        self.turn = None

    @abstractmethod
    def create_initial_board_state(self, width: int, height: int, snake_ids: List[str]):
        pass

    @abstractmethod
    def create_next_board_state(self, moves: Dict[str, Direction]):
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        pass
