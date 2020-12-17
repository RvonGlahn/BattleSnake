from typing import List, Dict
import numpy as np

from agents.States import States
from agents.heuristics.Distance import Distance
from agents.heuristics.ValidActions import ValidActions
from agents.strategies.Anxious import Anxious
from agents.strategies.Hungry import Hungry
from agents.strategies.Agressive import Agressive
from agents.strategies.Provocative import Provocative
from agents.SnakeAutomat import SnakeAutomat

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.GameInfo import GameInfo
import time

###################
# TODO:
# - time_limit in strategien / ActionPlan einbauen
# - MovementProfile mit der Zeit verbessern
# - update behaviour
# - automaten nach relevanz sortieren
# - Nachdem man gegessen hat nicht Tail fressen
# - Valid_Actions auf Tiefe 2 erweitern oder flachen MaxN Tree einbauen
###################


class Decision:

    def __init__(
            self
    ):
        self.my_snake_id: str = ""
        self.enemy_ids: List[str] = []
        self.my_food_path: List[Position] = []
        self.game_round: int = 0
        self.update_frequency = 5
        self.automats: Dict = {}
        self.states: Dict = {}
        self.monitoring_time = 150

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
        # print("Set-Up Automat-States", self.states)
        print("My ID:", self.my_snake_id)

    def _update_automats(self, board: BoardState, grid_map: GridMap) -> None:

        print("Update Automats in decide")
        snake_heads = [snake.get_head() for snake in board.snakes]
        longest_snake = max([snake.get_length() for snake in board.snakes])

        for index, snake in enumerate(board.snakes):
            automat = self.automats[snake.snake_id]

            automat.update_snake(snake)
            automat.add_position(snake.get_head())
            automat.monitor_dist_to_enemies(Distance.dist_to_closest_enemy_head(board.snakes, snake))
            self.states[snake.snake_id] = self.automats[snake.snake_id].state

            if self.game_round % self.update_frequency == 0 and snake.snake_id != self.my_snake_id:
                automat.monitor_length(snake.get_length())

                enemy_snakes = board.snakes.copy()
                enemy_snakes.pop(index)

                enemy_heads = snake_heads.copy()
                enemy_heads.pop(index)

                if self.game_round != 0:
                    automat.update_enemy_state(longest_snake)
                automat.make_movement_profile_prediction(enemy_snakes, enemy_heads, board, grid_map)
                # automat.update_behaviour()

        # update my snake state
        self.automats[self.my_snake_id].update_my_state(board.snakes, self._get_snake_states(), self.game_round)

    def _delete_dead_snake(self, dead_snakes: List[Snake]) -> None:
        for dead_snake in dead_snakes:
            if dead_snake.snake_id in self.automats.keys():
                del self.automats[dead_snake.snake_id]

    def _get_snake_states(self) -> Dict:
        states = {automat.snake.snake_id: automat.state for automat in self.automats.values()}
        return states

    def _call_strategy(self, you: Snake, board: BoardState, grid_map: GridMap) -> Direction:
        my_state = self.automats[self.my_snake_id].get_state()
        
        if my_state == States.HUNGRY:
            action, self.my_food_path = Hungry.hunger(you, board, grid_map, self.my_food_path)
            return action

        if my_state == States.ANXIOUS:
            return Anxious.avoid_enemy(you, board, grid_map)

        if my_state == States.AGRESSIVE:
            return Agressive.attack()

        if my_state == States.PROVOCATIVE:
            return Provocative.provocate(you, board, grid_map, self.states, self.automats)

    def set_round(self, this_round):
        self.game_round = this_round

    def decide(self, you: Snake, board: BoardState, grid_map: GridMap, game_info: GameInfo) -> Direction:

        start_time = time.time()

        if len(self.automats) != len(board.snakes):
            self._delete_dead_snake(board.dead_snakes)

        # decide if we focus on monitoring enemies or on calculating our next move
        dist_to_closest_head = Distance.dist_to_closest_enemy_head(board.snakes, you)
        if dist_to_closest_head < 5:
            self.monitoring_time = 100

        self._update_automats(board, grid_map)

        next_action = self._call_strategy(you, board, grid_map)

        print(self.automats[self.my_snake_id].get_state())

        if self.game_round == 10:
            possible_actions = you.possible_actions()
            ValidActions.multi_level_valid_actions(board, possible_actions, board.snakes, you,  grid_map, 5)

        return next_action

