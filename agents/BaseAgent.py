from abc import abstractmethod
from environment.Battlesnake.model.GameInfo import GameInfo
from environment.Battlesnake.model.MoveResult import MoveResult
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState


class BaseAgent:

    @abstractmethod
    def get_name(self):
        pass

    def get_color(self):
        return None

    def user_key_pressed(self, key):
        pass

    @abstractmethod
    def start(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        pass

    @abstractmethod
    def move(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake) -> MoveResult:
        pass

    @abstractmethod
    def end(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        pass
