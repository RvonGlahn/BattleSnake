from typing import Tuple, List
from agents.heuristics.Distance import Distance

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap
from agents.gametree.AStar import AStar


class Aggressive:
    # follow head of enemies that are smaller than Jürgen
    @staticmethod
    def attack(snakes: List[Snake], board: BoardState, grid_map: GridMap, you: Snake) -> List[Tuple[Position, Direction]]:
        
        head = you.get_head()
        target = None

        # alle relevanten snakes = alle kleiner als Jürgen
        relevant_snakes = []
        # dangerous snakes = größer/gleich Jürgen
        dangerous_snakes = []
        for snake in snakes:
            if snake.get_length < you.get_length:
                relevant_snakes.append(snake)
            else:
                dangerous_snakes.append(snake)

        best_distance = 0
        # jagd auf relevant snakes, die möglichst weit weg von dangerous snakes sind
        if len(dangerous_snakes) > 0:
            for rel_snake in relevant_snakes:
                distance = min([Distance.manhattan_dist(dan_snake.get_head(), rel_snake.get_head()) for dan_snake in dangerous_snakes])
                if distance > best_distance:
                    best_distance = distance
                    target = rel_snake.get_head()
        # sonst geringsten Abstand
        else:
            best_distance = 999999
            for rel_snake in relevant_snakes:
                distance = [Distance.manhattan_dist(head, rel_snake.get_head())]
                if distance < best_distance:
                    best_distance = distance
                    target = rel_snake.get_head()

        cost, path = AStar.a_star_search(head, target, board, grid_map)
        path_array = path

        return path_array
