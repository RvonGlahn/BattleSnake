from typing import List
from agents.BaseAgent import BaseAgent
from agents.strategies.Hungry import Hungry
from agents.heuristics.Distance import Distance
from agents.heuristics.ValidActions import ValidActions
from agents.strategies.Anxious import Anxious
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

        # possible_actions = you.possible_actions()
        # valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, you, grid_map)
        # next_action = None

        # TODO: replace logic with decision
        if self.first:
            self.Decision.set_up_automats(board.snakes)
            self.first = False

        self.Decision.set_round(turn)
        next_action = self.Decision.decide(you, board, grid_map, game_info)

        """
        enemy_head_dist = min([Distance.manhattan_dist(snake.get_head(), you.get_head())
                               for snake in board.snakes if snake.snake_id is not you.snake_id])

        if enemy_head_dist < 10:
            next_action = Anxious.avoid_enemy(valid_actions, you, board.snakes)
        else:
            next_action = Anxious.hide_in_corner(board, you, grid_map)
        if you.health < 25:
            if not self.food_path:
                self.food_path = Hungry.follow_food(you, board, grid_map)
            if self.food_path[0][1] in valid_actions:
                next_action = self.food_path[0][1]
                self.food_path.pop(0)
            else:
                self.food_path = []
        """
        return MoveResult(direction=next_action)

    def end(self, game_info: GameInfo, turn: int, board: BoardState, you: Snake):
        pass

