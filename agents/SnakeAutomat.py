from typing import List, Dict

from agents.heuristics.MovementProfile import MovementProfile
from agents.States import States
from agents.heuristics.Distance import Distance

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake


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
        self.length_history:  List[int] = []
        self.distance_to_enemy_heads: List[int] = []
        self.movement_profile_predictions: Dict = {
            "food": [],
            "head": []
        }
        self.behaviour: Dict = {
            "attack_head": 0,
            "force_outside": 0,
            "flee_from_enemy": 0,
            "chase_food": 0,
            "chase_tail": 0     # Schwerpunkt berechnen
        }

    def __eq__(self, other_state: States):
        return self.state == other_state

    def update_snake(self, snake: Snake) -> None:
        self.snake = snake

    def monitor_length(self, length: int) -> None:
        self.length_history.append(length)
        if len(self.length_history) > 10:
            self.length_history.pop(0)

    def monitor_dist_to_enemies(self, dist: int) -> None:
        self.distance_to_enemy_heads.append(dist)
        if len(self.distance_to_enemy_heads) > 10:
            self.distance_to_enemy_heads.pop(0)

    def add_position(self, position: Position) -> None:
        self.previous_positions.append(position)
        if len(self.previous_positions) > 10:
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

        if self.snake.health < 25:
            self.state = States.HUNGRY
            return

        # check if game is in early stage and how many enemies are left
        if round_number < 150 or len(enemy_snakes) >= 3:

            for enemy in enemy_snakes:
                # check if we are shorter than near snakes and if snakes are agressive
                if self.snake.get_length() < enemy.get_length() and states[enemy.snake_id] is States.AGRESSIVE:
                    self.state = States.ANXIOUS
                    return

        # check if game lasts longer and we can provocate
        else:
            self.state = States.PROVOCATIVE
            return

    def make_movement_profile_prediction(self, enemy_snakes: List[Snake], food: List[Position],
                                         enemy_heads: List[Position]) -> None:

        for enemy in enemy_snakes:
            if enemy.get_length() < self.snake.get_length():
                self.movement_profile_predictions["head"] = MovementProfile.get_head_profiles(food)
            self.movement_profile_predictions["food"] = MovementProfile.get_food_profiles(enemy_heads)

    def update_enemy_state(self) -> None:
        # get path to food or head that fits best the performed actions
        most_prob_food_path = min([Distance.path_similarity(f_profile, self.previous_positions)
                                   for f_profile in self.movement_profile_predictions["food"]])

        most_prob_head_path = min([Distance.path_similarity(h_profile, self.previous_positions)
                                   for h_profile in self.movement_profile_predictions["head"]])
        ###########################
        # TODO: set state of snake
        # relevant infos:
        # health, movement_profile, length_delta, distance_to_other snakes, longest_snake
        ###########################
        if most_prob_food_path < most_prob_head_path or self.snake.health < 20:
            self.state = States.HUNGRY

        if most_prob_head_path < most_prob_food_path:
            self.state = States.AGRESSIVE

        # if length klein aber dist to head auch klein PROVOCATIVE
        # if length klein und dist to head groß dann ANXIOUS

    def update_behaviour(self, enemy_snakes: List[Snake]):
        # Update Behaviour if snakes are near each other
        pass
