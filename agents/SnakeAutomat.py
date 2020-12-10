import math
from typing import List, Dict
import numpy as np
from agents.States import States

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap
import numpy as np
from sklearn import hmm


class SnakeAutomat:

    def __init__(
            self,
            snake: Snake,
            enemy: bool,
            valid_actions: Direction,
    ):
        self.snake: Snake = snake
        self.enemy: bool = enemy
        self.state = States.HUNGRY if self.enemy else self.status = States.ANXIOUS
        self.previous_positions: List[Position] = []
        self.Behaviour: Dict = {
            "attack_head": 0,
            "force_outside": 0,
            "flee_from_enemy": 0,
            "chase_food": 0
        }

    def __eq__(self, other_state):
        return self.state == other_state

    def get_state(self) -> States:
        return self.state

    def update_my_state(self, enemy_snakes: List[Snake], states: Dict, round_number: int) -> None:

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

    def update_enemy_state(self, enemy_snakes) -> None:
        pass




    def update_behaviour(self):
        # Update Behaviour if snakes are near each other
        pass

    def reset_state(self, enemy: bool):
        if enemy:
            self.state = States.AGRESSIVE
        else:
            self.state = States.ANXIOUS

    """
    def _hidden_markov(self):

        startprob = np.array([0.3, 0.3, 0.3, 0.1])
        transmat = np.array([[0.35, 0.35, 0.2, 0.1],
                             [0.3, 0.25, 0.2, 0.25],
                             [0.3, 0.3, 0.2, 0.2],
                             [0.3, 0.3, 0.2, 0.2]])

        means = np.array([[0.0, 0.0], [3.0, -3.0], [5.0, 10.0]])
        covars = np.tile(np.identity(2), (3, 1, 1))

        model = hmm.GaussianHMM(4, "full", startprob, transmat)
        model.means_ = means
        model.covars_ = covars
        X, Z = model.sample(100)
    """


