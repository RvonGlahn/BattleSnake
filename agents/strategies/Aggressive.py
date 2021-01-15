from typing import Tuple, List
import numpy as np

from agents.heuristics.Distance import Distance
from agents.heuristics.ValidActions import get_valid_neigbours
from agents.gametree.AStar import AStar
from agents.Hyperparameters import Params_Aggressive

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap


class Aggressive:

    @staticmethod
    def flood_kill(enemy: Snake, my_snake: Snake, kill_board: np.ndarray, board: BoardState, grid_map: GridMap):
        # TODO: Parameter snake_dead_in_rounds um mehr valide actions zu erhalten
        #  - breite des PFades auf 1 begrenzen
        my_head = my_snake.get_head()
        enemy_head = enemy.get_head()
        kill_actions = []
        search = False

        for part in enemy.body:
            kill_board[part.x][part.y] -= 1000
        kill_board[my_head.x][my_head.y] -= 1000

        x, y = np.unravel_index(kill_board.argmax(), kill_board.shape)

        print(kill_board)
        print(Position(x, y))
        for (pos_x, pos_y) in get_valid_neigbours(x, y, kill_board):
            if kill_board[pos_x][pos_y] < 0:
                x, y = pos_x, pos_y
                search = True
                break

        enemy_dist = Distance.manhattan_dist(enemy_head, Position(x, y))
        my_dist = Distance.manhattan_dist(my_head, Position(x, y))

        if enemy_dist > my_dist and search:
            cost, path = AStar.a_star_search(my_head, Position(x, y), board, grid_map)

            count = 0
            for pos, dir in path:
                if kill_board[pos.x][pos.y] >= 0:
                    return []

                abort_count = 0
                for (pos_x, pos_y) in get_valid_neigbours(x, y, kill_board):
                    if kill_board[pos_x][pos_y] < 0:
                        abort_count += 1
                if abort_count > 2 and count < 4:
                    return []
                if abort_count > 1 and 3 < count < my_dist:
                    return []
                kill_actions.append(dir)
                count += 1

        return kill_actions

    @staticmethod
    def aggressive():
        return Params_Aggressive.KILL_PATH.pop(0)

