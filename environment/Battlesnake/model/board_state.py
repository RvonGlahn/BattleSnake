import copy

from .Food import Food
from .Snake import Snake
from typing import List, Optional
from .Position import Position
from .grid_map import GridMap
from .Occupant import Occupant


class BoardState:

    def __init__(
            self,
            width: int,
            height: int,
            snakes: Optional[List[Snake]] = None,
            food: Optional[List[Food]] = None,
    ):

        if width < 3 or height < 3:
            raise Exception("World size must be at least 3x3")

        self.snakes: List[Snake] = snakes if snakes is not None else []  # contains only alive snakes
        self.all_snakes: List[Snake] = copy.deepcopy(self.snakes)
        self.food: List[Food] = food if food is not None else []
        self.height = height
        self.width = width

    def add_snake(self, snake: Snake):
        self.snakes.append(snake)
        self.all_snakes.append(snake)

    def add_food(self, f: Food):
        self.food.append(f)

    def get_alive_snake_by_id(self, snake_id) -> Optional[Snake]:
        for s in self.snakes:
            if s.snake_id == snake_id:
                return s

        return None

    def get_snake_by_id(self, snake_id) -> Optional[Snake]:
        for s in self.all_snakes:
            if s.snake_id == snake_id:
                return s

        return None

    def is_out_of_bounds(self, p: Position):

        if p.x < 0 or p.x >= self.width:
            return True
        if p.y < 0 or p.y >= self.height:
            return True

        return False

    def is_occupied_by_food(self, p: Position):
        """Returns if the field is occupied by food"""

        for f in self.food:
            if f == p:
                return True
        return False

    def is_occupied_by_snake(self, p: Position):
        """Returns if the field is occupied by snake"""

        for s in self.snakes:
            for b in s.body:
                if b == p:
                    return True

        return False

    def is_occupied(self, p: Position):
        return self.is_occupied_by_food(p) or self.is_occupied_by_snake(p)

    def generate_grid_map(self) -> GridMap[Occupant]:

        grid_cache: GridMap = GridMap(self.width, self.height)

        for f in self.food:
            grid_cache.set_value_at_position(f, Occupant.Food)

        for snake in self.snakes:
            if not snake.is_alive():
                continue

            for b in snake.body:
                grid_cache.set_value_at_position(b, Occupant.Snake)

        return grid_cache

    def finished(self):
        return len(self.snakes) <= 1

    def get_all_snakes_sorted(self, reverse=False):

        def c(s: Snake):
            if s.elimination_event is None:
                return 9999999
            else:
                return s.elimination_event.turn

        snakes = sorted(self.all_snakes, key=c, reverse=reverse)
        return snakes

    @staticmethod
    def is_obstacle(o: Occupant):
        if o == Occupant.Snake:
            return True
        return False
