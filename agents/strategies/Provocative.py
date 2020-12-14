from typing import Tuple, List
from agents.heuristics.Distance import Distance

from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap
from agents.gametree.AStar import AStar

class Provocative:

    @staticmethod
    def provocate(snakes: List[Snake], board: BoardState, grid_map: GridMap) -> List[Tuple[Position, Direction]]:
        
        head = you.get_head()
        target = None
        target_field = []
        target_snake = None

        #alle relevanten snakes = alle mit state AGGRESSIVE
        relevant_snakes = []

        for snake in snakes:
            if snake.state = States.AGRESSIVE:
                relevant_snakes.append(snake)

        while True:
            best_distance = 999999
            for snake in relevant_snakes:
                distance = [Distance.manhattan_dist(head, snake.get_head())]
                if distance < best_distance:
                    best_distance = distance
                    target_snake = snake
                    target = snake.get_head()
            
            x, y = target
            if _free(Position(x-5,y),board):
                target_field.append(Position(x-5,y))
            if _free(Position(x-5,y-5),board):
                target_field.append(Position(x-5,y-5))
            if _free(Position(x,y-5),board):
                target_field.append(Position(x,y-5))
            
            if len(target_field) == 0:
                relevant_snakes.remove(snake)
            else:
                break
        
        if len(target_field) == 0:
            possible_actions = you.possible_actions()
            random_action = np.random.choice(possible_actions)
            #random action ausgeben
            random_path: List[Tuple[Position, Direction]] = []
            random_path.append((head.advanced(random_action),random_action))
            return random_path
        else:
            dist = 999999
            for field in target_field:
                distance = [Distance.manhattan_dist(head, field)]
                if distance < dist:
                    dist = distance
                    target = field

            cost, path = AStar.a_star_search(head, target, board, grid_map)
            path_array = path

            return path_array
  
    @staticmethod
    def _free(position: Tupel, board: BoardState) -> Boolean:
        if board.is_out_of_bounds(position):
            return False
        if board.is_occupied(position):
            return False
        return True