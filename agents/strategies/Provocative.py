from typing import Tuple, List, Dict
import numpy as np
from agents.heuristics.Distance import Distance
from agents.States import States
from agents.strategies.Anxious import Anxious
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Direction import Direction
from environment.Battlesnake.model.grid_map import GridMap
from agents.gametree.AStar import AStar
from agents.heuristics.MovementProfile import MovementProfile
from agents.SnakeAutomat import SnakeAutomat

##############
# TODO:
# - Hungry Snakes berücksichtigen
# - wenn hungry und agressive gleich nah - > hungry provozieren
# - MovementProfile einbeziehen
# - Agressive Schlangen zum Rand locken
#       - Feste Punkte am Rand
#       - Check ob Punkte sinnvoll sind (andere Schlangen usw. ...)
##############


class Provocative:

    @staticmethod
    def provocate(you: Snake, board: BoardState, grid_map: GridMap, states: Dict, automats: Dict) -> List[Tuple[Position, Direction]]:

        head = you.get_head()
        target_snake = None
        hunted = False
        run = False
        trap = False

        # alle relevanten snakes = alle mit state AGGRESSIVE
        aggressive_snakes = []
        hungry_snakes = []

        for snake in board.snakes:
            if snake.snake_id == you.snake_id:
                pass
            else:
                if states[snake.snake_id] == States.AGRESSIVE:
                    aggressive_snakes.append(snake)
                if states[snake.snake_id] == States.HUNGRY:
                    hungry_snakes.append(snake)
                hunt_profile = automats[snake.snake_id].movement_profile_predictions["head"] #prüfen, ob eine Schlange Jürgen jagt
                if len(hunt_profile) > 0:
                    target_snake = snake
                    hunted = True
                    break
                target_snake = snake
                target = snake.get_head()

        if not hunted and not run and len(aggressive_snakes) > 0:
            best_distance = 999999
            for snake in aggressive_snakes:
                distance = [Distance.manhattan_dist(head, snake.get_head())]
                if distance < best_distance:
                    best_distance = distance
                    target_snake = snake
                    target = snake.get_head()
            trap = True

        if hunted: 
            
            #nächste gute Ecke suchen
            bottom_left, bottom_right, top_left, top_right = (Position(3, 3)), \
                                                         (Position(3, board.height - 3)), \
                                                         (Position(board.width - 3, 3)), \
                                                         (Position(board.width - 3, board.height - 3))
            allcorners = []
            allcorners.extend((bottom_left, bottom_right, top_left, top_right))
            
            best_corner = allcorners[0]
            dist = [Distance.manhattan_dist(best_corner, head)]
            for corner in allcorners:
                
                dist_corner = [Distance.manhattan_dist(corner, head)]
                if (dist_corner < dist):
                    best_corner = corner
            
            cost, path = AStar.a_star_search(head, best_corner, board, grid_map)
            
            if cost == 0:
                run = True #wieder zur mitte weglaufen
                hunted = False
            else:
                _, next_step = path[0]
                return next_step

        if run:#zur mitte laufen
            mid = Position(board.width//2,board.height//2)
            cost, path = AStar.a_star_search(head, mid, board, grid_map)
            if cost == 0:
                hunted = True
                run = False
            _, next_step = path[0]
            return next_step

        if trap:
            cost, path = AStar.a_star_search(head, target, board, grid_map)
            _, next_step = path[0]
            return next_step

        possible_actions = you.possible_actions()
        random_action = np.random.choice(possible_actions)
        # random action ausgeben
        return None

    @staticmethod
    def _free(position: Position, board: BoardState) -> bool:
        if board.is_out_of_bounds(position):
            return False
        if board.is_occupied(position):
            return False
        return True
