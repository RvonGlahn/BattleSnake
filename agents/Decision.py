from typing import List, Dict

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
# - MovementProfile erstellen
# - update_enemy state
# - update behaviour
# - automaten nach relevanz sortieren
# - Option A-Star auf X Schritte zu begrenzen und mehrere Inputs zu geben
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

    def set_up_automats(self, snakes: List[Snake]) -> Dict:

        enemy = True
        for snake in snakes:

            if snake.snake_id is not self.my_snake_id:
                self.enemy_ids.append(snake.snake_id)

            else:
                enemy = False
                self.my_snake_id = snake.snake_id

            self.automats[snake.snake_id] = SnakeAutomat(snake, enemy)

    def _update_automats(self, snakes: List[Snake], food, heads) -> None:
        snake_heads = [snake.get_head() for snake in snakes]
        for index, snake in enumerate(snakes):

            automat: SnakeAutomat = self.automats[snake.snake_id]
            automat.update_snake(snake)
            automat.monitor_length(snake.get_length())
            automat.add_position(snake.get_head())
            automat.monitor_dist_to_enemies(Distance.dist_to_closest_enemy_head(snakes, snake))

            if self.game_round % 5 is 0 and snake.snake_id is not self.my_snake_id:

                enemy_snakes = snakes.copy()
                enemy_snakes.pop(index)
                enemy_heads = snake_heads
                enemy_heads.pop(index)
                # automat.make_movement_profile_prediction(enemy_snakes, food, enemy_heads)
                # automat.update_behaviour()

    def _delete_dead_snake(self, dead_snakes: List[Snake]) -> None:
        for dead_snake in dead_snakes:
            if dead_snake.snake_id in self.automats.keys():
                del self.automats[dead_snake.snake_id]

    def _get_snake_states(self) -> Dict:
        states = {automat.snake.snake_id: automat.state for automat in self.automats}
        return states

    def _call_strategy(self, you: Snake, board: BoardState, grid_map: GridMap) -> Direction:
        state = self.automats[self.my_snake_id].get_state()

        if state == States.HUNGRY:
            possible_actions = you.possible_actions()
            valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, you, grid_map)
            action: Direction = Direction.UP
            if not self.my_food_path:
                self.my_food_path = Hungry.follow_food(you, board, grid_map)
            if self.food_path[0][1] in valid_actions:
                action = self.my_food_path[0][1]
                self.my_food_path.pop(0)
            else:
                self.food_path = []
            return action

        if state == States.ANXIOUS:
            return Anxious.avoid_enemy(you, board, grid_map)

        if state == States.AGRESSIVE:
            return Agressive.attack()

        if state == States.PROVOCATIVE:
            return Provocative.provocate()

    def set_round(self, this_round):
        self.game_round = this_round

    def decide(self, you: Snake, board: BoardState, grid_map: GridMap, game_info: GameInfo) -> Direction:

        next_action: Direction

        start_time = time.time()

        if len(self.automats) is not len(board.snakes):
            self._delete_dead_snake(board.dead_snakes)

        self._update_automats(board.snakes)

        dist_to_closest_head = Distance.dist_to_closest_enemy_head(board.snakes, you)

        # decide if we focus on monitoring enemies or on calculating our next move
        if dist_to_closest_head > 5:
            self.monitoring_time = 100

        # update enemy
        for automat in self.automats:
            if time.time() - start_time < self.monitoring_time:
                break
            # automat.update_enemy_state()

        self.automats[self.my_snake_id].update_my_state(board.snakes, self._get_snake_states(), self.game_round)

        # while time.time() - start_time < 350:
        next_action = self._call_strategy(you, board, grid_map)

        return next_action

