from typing import List, Dict
from agents.strategies.Hungry import Hungry
from agents.heuristics.Distance import Distance
from agents.heuristics.ValidActions import ValidActions
from agents.strategies.Anxious import Anxious
from agents.SnakeAutomat import SnakeAutomat

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Direction import Direction


class Decision:

    def __init__(self, snakes):
        self.my_snake_id: str = ""
        self.enemy_ids: List[str] = []
        self.my_food_path: List[Position] = []
        self.game_round: int = 0
        self.update_frequency = 5
        self.automats: Dict = self._set_up_automats(snakes)

    def _set_up_automats(self, snakes: List[Snake]) -> Dict:

        automat_dict = {}
        for snake in snakes:
            enemy = True

            if snake.snake_id is not self.my_snake_id:
                self.enemy_ids.append(snake.snake_id)

            else:
                enemy = False
                self.my_snake_id = snake.snake_id

            automat_dict[snake.snake_id] = SnakeAutomat(snake, enemy)
        return automat_dict

    def _update_automats(self, snakes):

        if self.game_round % 5 is 0:
            self.automats


    def _delete_dead_snake(self, dead_snakes: List[Snake]) -> None:
        for dead_snake in dead_snakes:
            if dead_snake.snake_id in self.automats.keys():
                del self.automats[dead_snake.snake_id]

    def set_round(self, this_round):
        self.game_round = this_round

    def decide(self, you: Snake, board: BoardState, grid_map: GridMap) -> Direction:

        next_action: Direction

        if len(self.automats) is not len(board.snakes):
            self._delete_dead_snake(board.dead_snakes)

        self._update_automats(board.snakes)

        # decide which actions are relevant for next move
        possible_actions = you.possible_actions()
        valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, you, grid_map)

        dist_to_closest_head = min([Distance.manhattan_dist(snake.get_head(), you.get_head())
                                    for snake in board.snakes if snake.snake_id is not you.snake_id])

        # decide if we focus on monitoring enemies or on calculating our next move
        if dist_to_closest_head < 10:
            # call gametree with strategies
            pass
        else:
            # observe enemies and get
            pass

        # call apropriate functions from automats and choose relevant input

        return next_action
