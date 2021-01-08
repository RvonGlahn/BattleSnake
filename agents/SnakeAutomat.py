from typing import List, Dict
import statistics

from agents.heuristics.MovementProfile import MovementProfile
from agents.States import States
from agents.heuristics.Distance import Distance
from agents.Hyperparameters import Params_Automat

from environment.Battlesnake.model.board_state import GridMap
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake

###########################
# TODO: update Behaviour
###########################


class SnakeAutomat:

    def __init__(
            self,
            snake: Snake,
            enemy: bool
    ):
        self.snake: Snake = snake
        self.enemy: bool = enemy
        self.state = States.HUNGRY if self.enemy else States.ANXIOUS
        self.previous_positions: List[Position] = []
        self.length_history: List[int] = []
        self.food_history = []
        self.distance_to_enemy_heads: List[int] = []

        self.move_profil = MovementProfile()
        self.move_profile_predictions: Dict = {
            "food": [],
            "head": []
        }

        self.behaviour: Dict = {
            "attack_head": 0,
            "force_outside": 0,
            "flee_from_enemy": 0,
            "chase_food": 0,
            "chase_tail": 0  # Schwerpunkt berechnen
        }

    def __eq__(self, other_state: States):
        return self.state == other_state

    def update_snake(self, snake: Snake) -> None:
        self.snake = snake

    def monitor_length(self, length: int) -> None:
        self.length_history.append(length)
        if len(self.length_history) > Params_Automat.MONITOR_LENGTH:
            self.length_history.pop(0)

    def monitor_food(self, food_number: int) -> None:
        self.food_history.append(food_number)
        if len(self.length_history) > Params_Automat.MONITOR_FOOD:
            self.length_history.pop(0)

    def monitor_dist_to_enemies(self, dist: int) -> None:
        self.distance_to_enemy_heads.append(dist)
        if len(self.distance_to_enemy_heads) > Params_Automat.MONITOR_DISTANCE:
            self.distance_to_enemy_heads.pop(0)

    def add_position(self, position: Position) -> None:
        self.previous_positions.append(position)
        if len(self.previous_positions) > Params_Automat.MONITOR_DISTANCE:
            self.previous_positions.pop(0)

    def reset_positions(self) -> None:
        self.previous_positions = []

    def reset_state(self, enemy: bool) -> None:
        if enemy:
            self.state = States.AGRESSIVE
        else:
            self.state = States.ANXIOUS

    def get_state(self) -> States:
        return self.state

    def update_my_state(self, snakes: List[Snake], states: Dict, round_number: int) -> None:

        enemy_snakes = [snake for snake in snakes if snake.snake_id is not self.snake.snake_id]

        # TODO: schlaue Regelung ob Anxious oder Hungry -> Relevant Food hier reinbringen? 
        if self.snake.health < Params_Automat.HUNGER_HEALTH_BOUNDARY + 20 and statistics.mean(self.food_history) < 4:
            self.state = States.HUNGRY
            return
        if self.snake.health < Params_Automat.HUNGER_HEALTH_BOUNDARY:
            self.state = States.HUNGRY
            return
        else:
            self.state = States.ANXIOUS

        # check if game is in early stage and how many enemies are left
        if round_number < Params_Automat.ROUND_NUMBER_BOUNDARY or len(enemy_snakes) >= Params_Automat.ENEMIES_ALIVE:

            for enemy in enemy_snakes:
                # check if we are shorter than near snakes and if snakes are agressive
                if self.snake.get_length() < enemy.get_length() and states[enemy.snake_id] is States.AGRESSIVE:
                    self.state = States.ANXIOUS
                    return

        # check if game lasts longer and we can provocate
        else:
            self.state = States.PROVOCATIVE
            return

    def make_movement_profile_prediction(self, enemy_snakes: List[Snake], enemy_heads: List[Position],
                                         board: BoardState, grid_map: GridMap) -> None:

        for enemy in enemy_snakes:
            if enemy.get_length() < self.snake.get_length():
                self.move_profile_predictions["head"] = self.move_profil.get_head_profiles(self.snake.get_head(),
                                                                                           enemy_heads, board,
                                                                                           grid_map)

            self.move_profile_predictions["food"] = self.move_profil.get_food_profiles(self.snake.get_head(), board,
                                                                                       grid_map)

    def update_enemy_state(self, longest_snake: int) -> None:
        # get path to food or head that fits best the performed actions
        most_prob_food_path = 99999
        most_prob_head_path = 99999

        if self.move_profile_predictions["food"]:
            most_prob_food_path = min([Distance.path_similarity(f_profile, self.previous_positions)
                                       for f_profile in self.move_profile_predictions["food"]])

        if self.move_profile_predictions["head"]:
            most_prob_head_path = min([Distance.path_similarity(h_profile, self.previous_positions)
                                       for h_profile in self.move_profile_predictions["head"]])

        hungry = 0
        agressive = 0
        length_diff = self.length_history[0] - self.length_history[-1]
        head_dist_avg = sum(self.distance_to_enemy_heads)/len(self.distance_to_enemy_heads)

        # estimate correct state of Snake from assigning points to behaviour or snake_parameters
        if most_prob_food_path < most_prob_head_path:
            hungry += 1

        if most_prob_head_path < most_prob_food_path:
            agressive += 1

        if self.snake.health < 20:
            hungry += 1

        if self.snake.get_length() == longest_snake:
            agressive += 1

        if length_diff > 1:
            hungry += 1
        elif length_diff == 0:
            agressive += 1

        if self.state == States.AGRESSIVE:
            agressive += 1
        elif self.state == States.HUNGRY:
            hungry += 1

        if head_dist_avg < 4:
            agressive += 1
        elif head_dist_avg > 5:
            hungry += 1

    def update_behaviour(self, enemy_snakes: List[Snake]):
        # Update Behaviour if snakes are near each other
        pass
