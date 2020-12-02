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


class SnakeAutomat(BaseAgent):
    
    def __init__(
            self, 
            snake, 
            snake_type, 
            valid_actions
    ):
        self.state = get_state(snake_type)
        self.head = 
        self.next_position = 
        self.snake

    def get_state(self, my_snake: Snake, snakes: List[Snake]):
        """
        hungry
        agressive
        provocative
        anxious
        """
        pass
    
    def _get_relevant_Corner(self, my_head, snakes, board):

    def hide_in_corner(self, board: BoardState, you: Snake, grid_map):

    def avoid_enemy(self, valid_actions: List[Direction], my_snake: Snake, snakes: List[Snake]):

    def attack_enemy():
