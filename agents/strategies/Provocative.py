from typing import Tuple, List, Dict
import numpy as np
from agents.heuristics.Distance import Distance
from agents.States import States
from agents.heuristics.ValidActions import ValidActions
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
    def provocate(you: Snake, board: BoardState, grid_map: GridMap, states: Dict, automats: Dict) -> Direction:

        possible_actions = you.possible_actions()
        valid_actions = ValidActions.get_valid_actions(board, possible_actions, board.snakes, you, grid_map)
        head = you.get_head()
        relevant_snakes = []
        random_action = np.random.choice(valid_actions)

        for snake in board.snakes:
            if snake.snake_id == you.snake_id:
                pass
            else:
                relevant_snakes.append(snake)

        while len(relevant_snakes) > 0:
            target_snake = Provocative._nextsnake(relevant_snakes, head, states)

            if states[target_snake.snake_id] == States.HUNGRY:
                food_pathes = automats[target_snake.snake_id].move_profile_predictions["food"]
                dist = 99999
                food = Position(board.width//2, board.height//2)
                for path in food_pathes:
                    if len(path) < dist:
                        dist = len(path)
                        food, _= path[len(path)-1]
                cut, direc = Provocative._cuthungryoff(head, board, target_snake.get_head(), food, grid_map)
                if cut:
                    if direc in possible_actions:
                        return direc
                    else:
                        return random_action
                else:
                    relevant_snakes.remove(target_snake)

            target_head = None
            if states[target_snake.snake_id] == States.AGRESSIVE:
                head_pathes = automats[target_snake.snake_id].move_profile_predictions["head"]
                dist = 99999
                for path in head_pathes:
                    if len(path) < dist:
                        dist = len(path)
                        target_head, _ = path[len(path) - 1]
                if target_head == head:
                    direc = Provocative._provo(head, board, target_snake.get_head())
                    if direc in possible_actions:
                        return direc
                    else:
                        return random_action
                else:
                    relevant_snakes.remove(target_snake)

        #falls keine andere Action gefunden

        return random_action

        
    @staticmethod
    def _free(position: Position, board: BoardState) -> bool:
        if board.is_out_of_bounds(position):
            return False
        if board.is_occupied(position):
            return False
        return True

    @staticmethod
    def _provo(ownpos: Position, board: BoardState, enempos: Position) -> Direction:
        if Provocative._nearertowall(ownpos, board, enempos):
            dest = Provocative._nearertowall(ownpos, board)
            direc = Provocative._nextdirection(ownpos, dest)
            return direc
        else:
            middle = Position(board.width // 2, board.height // 2)
            direc = Provocative._nextdirection(ownpos, middle)
            return direc

    @staticmethod
    def _nextsnake(relevant_snakes: List[Snake], head: Position, states: Dict) -> Snake:
        nearest_distance = 99999
        target_snake = None
        for snake in relevant_snakes:
            distance = Distance.manhattan_dist(head, snake.get_head())
            if distance < nearest_distance:
                nearest_distance = distance
                target_snake = snake
            elif distance == nearest_distance:
                if states[snake.snake_id] == States.HUNGRY:
                    target_snake = snake
        return target_snake
    #
    # nächste Wandposition finden
    #    --w--
    #  |       |
    #  y       z
    #  |       |
    #    --x--
    #
    @staticmethod
    def _nearestwall(position: Position, board: BoardState) -> Position:
        x = Position(position.x, 0)
        y = Position(0, position.y)
        z = Position(board.width, position.x)
        w = Position(position.x, board.height)
        allwalls = [x, y, z, w]
        shortest = 99999
        nearest_wall = position
        for wall in allwalls:
            dist = [Distance.manhattan_dist(wall, position)]
            if dist < shortest:
                shortest = dist
                nearest_wall = wall
        return nearest_wall

    #
    # bool ob Weg einer Hungry Snake abgeschnitten werden kann + Direction
    #
    @staticmethod
    def _cuthungryoff(ownpos: Position, board: BoardState, enempos: Position, foodpos: Position, grid_map: GridMap) -> Tuple[bool, Direction]:

        _, enempath = AStar.a_star_search(enempos, foodpos, board, grid_map)
        db = {k:v for k, v in enempath}
        foo1 = Position(foodpos.x - 1,foodpos.y - 1)
        foo2 = Position(foodpos.x - 1, foodpos.y + 1)
        foo3 = Position(foodpos.x + 1, foodpos.y - 1)
        foo4 = Position(foodpos.x + 1, foodpos.y + 1)
        foo5 = Position(foodpos.x - 1, foodpos.y)
        foo6 = Position(foodpos.x + 1, foodpos.y)
        foo7 = Position(foodpos.x, foodpos.y - 1)
        foo8 = Position(foodpos.x, foodpos.y + 1)
        foods =[foo1, foo2, foo3, foo4, foo5, foo6, foo7, foo8]
        for food in foods: #TODO dauert vllt zu lange?
            _, mypath = AStar.a_star_search(ownpos, food, board, grid_map)
            da = {k:v for k, v in mypath}
            both = [(da[k], db[k])  for k in da.keys()&db.keys()]
            if len(both)>0:
                if len(mypath) < len(enempath):
                    _, nextdirection = mypath[0]
                    return True, nextdirection
        return False, Direction.DOWN

    #
    # prüfen, ob wir vor oder gleichauf mit dem aggressive Gegener sind, um zu verhindern, dass er uns fressen kann
    #
    @staticmethod
    def _infrontofhead(you: Snake, enemy: Snake, destination: Position) -> bool:
        ownhead = you.get_head()
        owndirection = Provocative._nextdirection(destination, ownhead)
        enemhead = enemy.get_head()
        enemybody = enemy.get_body()
        enembody = enemybody[0]
        enemdirection = AStar.reverse_direction(Provocative._nextdirection(enembody, enemhead))

        rel = Provocative._relativeposition(enemhead, ownhead)

        if owndirection == enemdirection:
            if owndirection == Direction.UP:
                if rel == 3 or rel == 4 or rel == 34:
                    return False
                else:
                    return True

            if owndirection == Direction.DOWN:
                if rel == 1 or rel == 2 or rel == 12:
                    return False
                else:
                    return True

            if owndirection== Direction.LEFT:
                if rel == 2 or rel == 4 or rel == 42:
                    return False
                else:
                    return True

            if owndirection == Direction.RIGHT:
                if rel == 1 or rel == 3 or rel == 13:
                    return False
                else:
                    return True
        else:
            #TODO ist hier überhaupt relevant, ob wir bereits in die gleiche Richtung laufen?

            pass



    #
    # nächste Direction um von aktueller Position in Richtung Ziel zu laufen
    #
    @staticmethod
    def _nextdirection(position: Position, destination: Position) -> Direction:
        rel = Provocative._relativeposition(destination, position)
        if rel == 12:
            return Direction.DOWN
        if rel == 24:
            return Direction.LEFT
        if rel == 34:
            return Direction.UP
        if rel == 13:
            return Direction.RIGHT
        if rel == 1:
            return np.random.choice([Direction.DOWN, Direction.RIGHT])
        if rel == 2:
            return np.random.choice([Direction.DOWN, Direction.LEFT])
        if rel == 3:
            return np.random.choice([Direction.UP, Direction.LEFT])
        if rel == 4:
            return np.random.choice([Direction.UP, Direction.RIGHT])


    #
    #  1    |    2
    #  ---- x -----
    #  3    |    4
    #
    # head ist der eigene Head, target ist das Ziel = anderer Kopf / Food
    # gibt an, in welchem Qadranten wir relativ zu unserem Ziel sind
    @staticmethod
    def _relativeposition(target: Position, head: Position) -> int:
        if target == head:
            return 0
        if (target.x - head.x) == 0:
            if (target.y - head.y) > 0:
                return 12
            else:
                return 34
        if (target.y - head.y) == 0:
            if (target.x - head.x) > 0:
                return 24
            else:
                return 13
        if (target.x - head.x) > 0:
            if (target.y - head.y) > 0:
                return 2
            else:
                return 4
        if (target.y - head.y) > 0:
            if (target.x - head.x) > 0:
                return 2
            else:
                return 1

    #sind wir näher zur Wall, der Gegner näher zur Mitte -> True
    #sinf wir näher zur Mitte, der Gegner näher zur Wall -> False
    @staticmethod
    def _nearertowall(ownpos: Position, board: BoardState, enempos: Position) -> bool:
        middle = Position(board.width//2, board.height//2)
        mydist = Distance.manhattan_dist(ownpos,middle)
        enemdist = Distance.manhattan_dist(enempos,middle)

        if mydist < enemdist:
            return False
        else:
            return True