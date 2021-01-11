from typing import List, Dict
import numpy as np

from agents.Hyperparameters import Params_Decision
from agents.States import States
from agents.heuristics.Distance import Distance
from agents.heuristics.ValidActions import ValidActions
from agents.strategies.Anxious import Anxious
from agents.strategies.Hungry import Hungry
from agents.strategies.Provocative import Provocative
from agents.SnakeAutomat import SnakeAutomat
from agents.gametree.ActionPlan import ActionPlan
from agents.strategies.SoloSurvival import SoloSurvival

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Direction import Direction
import time

###################
# TODO:
#  - time_limit in strategien / ActionPlan einbauen
#  - MovementProfile mit der Zeit verbessern
#  - update behaviour
#  - wenn kein food in der Nähe auf anxious wechseln aber food mehr priorisieren

###################


class Decision:

    def __init__(
            self
    ):
        self.my_snake_id: str = ""
        self.enemy_ids: List[str] = []
        self.my_food_path: List[Position] = []
        self.game_round: int = 0
        self.update_frequency = Params_Decision.UPDATE_FREQUENCY
        self.monitoring_time = Params_Decision.MONITOR_TIME

        self.automats: Dict = {}
        self.states: Dict = {}

        self.action_board = None
        self.default_board_score = None

    def set_default_board(self, height, width) -> None:
        init_board = np.zeros((height, width))
        for x in range(width):
            if x == 1:
                init_board[x][:] = 10
            elif x == width-2:
                init_board[x][:] = 10
            if x == 0 or x == width-1:
                init_board[x][:] = 25
                init_board[x][0] = 100
                init_board[x][-1] = 100
            else:
                init_board[x][0] = 25
                init_board[x][-1] = 25
                init_board[x][1] = 10
                init_board[x][-2] = 10

        self.default_board_score = init_board

    def set_up_automats(self, my_snake: Snake, snakes: List[Snake]) -> None:

        self.my_snake_id = my_snake.snake_id
        enemy = True

        for snake in snakes:

            if snake.snake_id != self.my_snake_id:
                self.enemy_ids.append(snake.snake_id)

            else:
                enemy = False
                self.my_snake_id = snake.snake_id

            self.automats[snake.snake_id] = SnakeAutomat(snake, enemy)
            self.states[snake.snake_id] = self.automats[snake.snake_id].state

    def _update_automats(self, board: BoardState, valid_board) -> None:

        snake_heads = [snake.get_head() for snake in board.snakes]
        longest_snake = max([snake.get_length() for snake in board.snakes])

        for index, snake in enumerate(board.snakes):
            automat = self.automats[snake.snake_id]

            automat.update_snake(snake)
            automat.add_position(snake.get_head())
            automat.monitor_dist_to_enemies(Distance.dist_to_closest_enemy_head(board.snakes, snake))
            automat.monitor_food(len(board.food))
            self.states[snake.snake_id] = self.automats[snake.snake_id].state

            if self.game_round % self.update_frequency == 0 and snake.snake_id != self.my_snake_id:
                automat.monitor_length(snake.get_length())

                enemy_snakes = board.snakes.copy()
                enemy_snakes.pop(index)

                enemy_heads = snake_heads.copy()
                enemy_heads.pop(index)

                if self.game_round != 0:
                    pass
                    # automat.update_enemy_state(longest_snake)
                # automat.make_movement_profile_prediction(enemy_snakes, enemy_heads, board, grid_map)
                # automat.update_behaviour()

        # update my snake state
        self.automats[self.my_snake_id].update_my_state(board, self._get_snake_states(), self.game_round,
                                                        valid_board)

    def _delete_dead_snake(self, dead_snakes: List[Snake]) -> None:
        for dead_snake in dead_snakes:
            if dead_snake.snake_id in self.automats.keys():
                del self.automats[dead_snake.snake_id]

    def _get_snake_states(self) -> Dict:
        states = {automat.snake.snake_id: automat.state for automat in self.automats.values()}
        return states

    def _call_strategy(self, you: Snake, board: BoardState, grid_map: GridMap,
                       valid_actions: List[Direction]) -> Direction:

        my_state = self.automats[self.my_snake_id].get_state()

        base_board = self.action_board + self.default_board_score
        action_plan = ActionPlan(base_board)

        if my_state == States.HUNGRY:
            action, self.my_food_path = Hungry.hunger(you, board, grid_map, self.my_food_path, valid_actions,
                                                      self.automats[self.my_snake_id])
            return action

        if my_state == States.ANXIOUS:
            return Anxious.avoid_enemy(you, board, grid_map, valid_actions, action_plan)

        if my_state == States.PROVOCATIVE:
            return Anxious.avoid_enemy(you, board, grid_map, valid_actions, action_plan)
            # return Provocative.provocate(you, board, grid_map, self.states, self.automats)

    def set_round(self, this_round) -> None:
        self.game_round = this_round

    def decide(self, you: Snake, board: BoardState, grid_map: GridMap) -> Direction:
        
        # SoloSurvival
        snakes = board.snakes
        if len(snakes) == 1 and snakes[0].snake_id == you.snake_id:
            return SoloSurvival.next_step(you, board, grid_map)
        # SoloSurvival

        if len(self.automats) != len(board.snakes):
            self._delete_dead_snake(board.dead_snakes)

        # init ValidActions object and get basic board for action_plan from multi_level
        valid_action = ValidActions(board, grid_map, you, self.states[self.my_snake_id])
        valid_actions, self.action_board, valid_board = valid_action.multi_level_valid_actions()

        # decide if we focus on monitoring enemies or on calculating our next move
        dist_to_closest_head = Distance.dist_to_closest_enemy_head(board.snakes, you)
        if dist_to_closest_head < Params_Decision.CLOSEST_HEAD_BOUNDARY:
            self.monitoring_time = Params_Decision.REDUCED_MONITORING_TIME

        self._update_automats(board, valid_board)

        next_action = self._call_strategy(you, board, grid_map, valid_actions)

        print("MyState:", self.automats[self.my_snake_id].get_state())

        return next_action
