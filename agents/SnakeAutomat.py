import math
from typing import Tuple, List, Optional
from agents.BaseAgent import BaseAgent
import numpy as np

from environment.Battlesnake.helper.DirectionUtil import DirectionUtil
from environment.Battlesnake.model.GameInfo import GameInfo
from environment.Battlesnake.model.MoveResult import MoveResult
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.model.Occupant import Occupant
from util.kl_priority_queue import KLPriorityQueue
import time
from environment.Battlesnake.model.SnakeState import SnakeState


class SnakeAutomat:
    
    def __init__(
            self, 
            snake: Snake,
            snake_type: bool,
            valid_actions: Direction,
    ):
        self.state = None
        self.snake = snake
        self.snake_type = snake_type
        self.previous_actions = []
        self.valid_actions = valid_actions
        self.previous_positions: List[Position]

    def get_state(self, snake_type, my_snake: Snake, snakes: List[Snake]):
        """
        hungry
        agressive
        provocative
        anxious
        """
        pass

    def update_my_state(self):
        pass

    def update_enemy_state(self):
        pass

    def reset_state(self):
        pass

    def _hidden_markov(self):
        pass


"""
def get_state(self, my_snake, snakes):
    if my_snake.get_length() % 2 == 1:
        for snake in snakes:
            if snake.get_length >= my_snake.get_length:
                return SnakeState.INFERIORHUNGRY  # hungry but inferior
        return SnakeState.HUNGRY  # hungry and the largest snake
    if my_snake.get_health <= 20:
        for snake in snakes:
            if snake.get_length >= my_snake.get_length:
                return SnakeState.INFERIORHUNGRY  # hungry but inferior
        return SnakeState.HUNGRY  # hungry and the largest snake
    for snake in snakes:
        if snake.get_length >= my_snake.get_length:
            return SnakeState.INFERIOR
        else:
            return SnakeState.SUPERIOR
"""