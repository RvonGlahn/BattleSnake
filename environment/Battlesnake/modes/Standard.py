from environment.Battlesnake.helper.helper import Helper
from environment.Battlesnake.model.EliminationEvent import EliminatedCause, EliminationEvent
from environment.Battlesnake.model.Food import Food
from environment.Battlesnake.model.GameInfo import GameInfo
from environment.Battlesnake.model.grid_map import GridMap
from environment.Battlesnake.modes.AbstractGame import AbstractGame
from typing import List, Optional, Dict
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Direction import Direction
import random
import numpy as np


class CollisionElimination:

    def __init__(self, snake_id: str, cause: EliminatedCause, by: str):
        self.snake_id = snake_id
        self.cause = cause
        self.by = by


class StandardGame(AbstractGame):

    BOARD_SIZE_SMALL = 7
    BOARD_SIZE_MEDIUM = 11
    BOARD_SIZE_LARGE = 19

    def __init__(self, timeout=400):

        game_id = Helper.generate_game_id()
        game_info = GameInfo(game_id=game_id, ruleset_name='standard', ruleset_version='v1.0.0', timeout=timeout)

        super().__init__(game_info)

        self.food_spawn_chance = 0.15
        self.snake_max_health = 100
        self.snake_start_size = 3
        self.turn = 0

    def create_initial_board_state(self, width: int, height: int, snake_ids: List[str]):

        self.state: BoardState = BoardState(width=width, height=height)

        for snake_id in snake_ids:
            self.state.add_snake(Snake(snake_id=snake_id))

        self.place_snakes()
        self.place_food()

    def place_snakes(self):
        if self.is_known_board_size():
            self.place_snakes_fixed()
        else:
            self.place_snakes_randomly()

    def place_snakes_fixed(self):
        b = self.state

        width = self.state.width

        starting_positions = [
            Position(1, 1),
            Position(width - 2, width - 2),
            Position(1, width - 2),
            Position(width - 2, 1),
            Position(int((width - 1) / 2), 1),
            Position(width - 2, int((width - 1) / 2)),
            Position(int((width - 1) / 2), width - 2),
            Position(1, int((width - 1) / 2))
        ]

        num_snakes = len(b.snakes)
        if num_snakes > len(starting_positions):
            raise ValueError('too many snakes for fixed start positions')

        # starting_positions = [starting_positions[i] for i in range(num_snakes)]
        random.shuffle(starting_positions)

        for i in range(num_snakes):
            b.snakes[i].set_initial_position(starting_positions[i], n=self.snake_start_size)

    def place_snakes_randomly(self):

        b = self.state
        num_snakes = len(b.snakes)
        unoccupied_points = self.get_even_unoccupied_points()
        indices = np.random.choice(len(unoccupied_points), size=num_snakes, replace=False)

        for i in range(num_snakes):
            b.snakes[i].set_initial_position(unoccupied_points[indices[i]], n=self.snake_start_size)

    def place_food(self):
        if self.is_known_board_size():
            self.place_food_fixed()
        else:
            self.place_food_randomly()

    def place_food_fixed(self):
        b = self.state

        # Place 1 food within exactly 2 moves of each snake
        for s in b.snakes:
            snake_head = s.get_head()

            possible_food_locations = [
                Position(x=snake_head.x - 1, y=snake_head.y - 1),
                Position(x=snake_head.x - 1, y=snake_head.y + 1),
                Position(x=snake_head.x + 1, y=snake_head.y - 1),
                Position(x=snake_head.x + 1, y=snake_head.y + 1),
            ]

            available_food_locations = []

            for p in possible_food_locations:
                if not b.is_occupied_by_food(p):
                    available_food_locations.append(p)

            if len(available_food_locations) <= 0:
                raise ValueError('not enough space to place food')

            food_position = np.random.choice(available_food_locations)
            food = Food(position=food_position)
            b.add_food(food)

        # Finally, always place 1 food in center of board for dramatic purposes

        center_position = Position(x=int((b.width - 1) / 2), y=int((b.height - 1) / 2))

        if b.is_occupied(center_position):
            raise ValueError('not enough space to place food')

        center_food = Food(position=center_position)
        b.add_food(center_food)

    def place_food_randomly(self):
        self.spawn_food(len(self.state.snakes))

    def is_known_board_size(self):
        h = self.state.height
        w = self.state.width

        known_sizes = (StandardGame.BOARD_SIZE_SMALL, StandardGame.BOARD_SIZE_MEDIUM, StandardGame.BOARD_SIZE_LARGE)

        if h == w and h in known_sizes:
            return True
        else:
            return False

    def create_next_board_state(self, moves: Dict[str, Direction]):

        self.turn += 1

        self.move_snakes(moves)
        self.reduce_snake_health()

        self.maybeFeedSnakes()
        self.maybeSpawnFood()
        self.maybeEliminateSnakes()

        snakes_alive = []

        for s in self.state.snakes:
            if s.is_alive():
                snakes_alive.append(s)

        self.state.snakes = snakes_alive

    def move_snakes(self, moves: Dict[str, Direction]):
        b = self.state

        for i, snake in enumerate(b.snakes):

            if not snake.is_alive():
                continue

            if len(snake.body) == 0:
                raise ValueError('found snake with zero size body')

            move = moves[snake.snake_id]
            head = snake.get_head()
            new_head = head.advanced(move)

            if new_head is None:
                current_direction = snake.get_current_direction()

                if current_direction is not None:
                    move = current_direction
                else:
                    move = Direction.UP

                new_head = head.advanced(move)

            # Append new head, pop old tail
            snake.body.insert(0, new_head)
            snake.body.pop()

    def reduce_snake_health(self):

        for snake in self.state.snakes:
            snake.health -= 1

    def maybeEliminateSnakes(self):
        b: BoardState = self.state

        # First order snake indices by length.
        # In multi-collision scenarios we want to always attribute elimination to the longest snake.
        snakes_by_length = sorted(b.snakes, key=lambda s: len(s.body))

        # First, iterate over all non-eliminated snakes and eliminate the ones
        # that are out of health or have moved out of bounds.
        for snake in b.snakes:
            if not snake.is_alive():
                continue

            if len(snake.body) <= 0:
                raise ValueError('snake is length zero')

            if self.snake_is_out_of_health(snake):
                # snake.eliminated_cause = EliminatedCause.EliminatedByOutOfHealth
                ee = EliminationEvent(cause=EliminatedCause.EliminatedByOutOfHealth, turn=self.turn, by=None)
                snake.elimination_event = ee
                continue

            if self.snake_is_out_of_bounds(snake, board_width=b.width, board_height=b.height):
                # snake.eliminated_cause = EliminatedCause.EliminatedByOutOfBounds
                ee = EliminationEvent(cause=EliminatedCause.EliminatedByOutOfBounds, turn=self.turn, by=None)
                snake.elimination_event = ee

                continue

        # Next, look for any collisions. Note we apply collision eliminations
        # after this check so that snakes can collide with each other and be properly eliminated.

        collision_eliminations: List[CollisionElimination] = []

        for snake in b.snakes:
            if not snake.is_alive():
                continue

            if len(snake.body) <= 0:
                raise ValueError('snake is length zero')

            # Check for self-collisions first
            if self.snake_has_body_collided(snake, snake):
                collision_eliminations.append(CollisionElimination(
                    snake_id=snake.snake_id,
                    cause=EliminatedCause.EliminatedBySelfCollision,
                    by=snake.snake_id))
                continue

            # Check for body collisions with other snakes second
            has_body_collided = False

            for other_snake in snakes_by_length:
                if snake.snake_id == other_snake.snake_id:
                    continue

                if not other_snake.is_alive():
                    continue

                if self.snake_has_body_collided(snake, other_snake):
                    collision_eliminations.append(CollisionElimination(
                        snake_id=snake.snake_id,
                        cause=EliminatedCause.EliminatedByCollision,
                        by=other_snake.snake_id))
                    has_body_collided = True
                    break

            if has_body_collided:
                continue

            # Check for head-to-heads last
            has_head_collided = False

            for other_snake in snakes_by_length:
                if snake.snake_id == other_snake.snake_id:
                    continue

                if not other_snake.is_alive():
                    continue

                if self.snake_has_lost_head_to_head(snake, other_snake):
                    collision_eliminations.append(CollisionElimination(
                        snake_id=snake.snake_id,
                        cause=EliminatedCause.EliminatedByHeadToHeadCollision,
                        by=other_snake.snake_id))
                    has_head_collided = True
                    break

            if has_head_collided:
                continue

        # Apply collision eliminations
        for elimination in collision_eliminations:
            for snake in b.snakes:
                if snake.snake_id == elimination.snake_id:
                    ee = EliminationEvent(cause=elimination.cause, turn=self.turn, by=elimination.by)
                    snake.elimination_event = ee

                    break

    def snake_is_out_of_health(self, s: Snake):
        return s.health <= 0

    def snake_is_out_of_bounds(self, s: Snake, board_width: int, board_height: int):

        head = s.get_head()

        if head.x < 0 or head.x >= board_width:
            return True
        elif head.y < 0 or head.y >= board_height:
            return True

        return False

    def snake_has_body_collided(self, s: Snake, other: Snake):

        head = s.get_head()

        for i, body in enumerate(other.body):
            if i == 0:
                continue
            elif body.x == head.x and body.y == head.y:
                return True

        return False

    def snake_has_lost_head_to_head(self, s: Snake, other: Snake):
        head = s.get_head()
        other_head = other.get_head()

        if head.x == other_head.x and head.y == other_head.y:
            return len(s.body) <= len(other.body)

        return False

    def maybeFeedSnakes(self):
        b = self.state

        for f in b.food:

            food_has_been_eaten = False
            for snake in b.snakes:

                # Ignore eliminated and zero-length snakes, they can't eat.
                if not snake.is_alive() or len(snake.body) == 0:
                    continue

                head = snake.get_head()
                if head.is_position_equal_to(f):
                    self.feed_snake(snake)
                    food_has_been_eaten = True

            if food_has_been_eaten:
                b.food.remove(f)

    def feed_snake(self, snake: Snake):
        self.grow_snake(snake)
        snake.health = self.snake_max_health

    def grow_snake(self, snake: Snake):
        if len(snake.body) > 0:
            tail = snake.get_tail()
            snake.body.append(tail)

    def maybeSpawnFood(self):
        b = self.state

        # TODO implement https://github.com/BattlesnakeOfficial/rules/commit/c6d9ba12ab966380c78c366869428725e2288835
        # TODO implement https://github.com/BattlesnakeOfficial/rules/commit/ca4b6c5dce7f8008ab7da44d1581b77ddef97609

        if len(b.food) == 0 or np.random.uniform() <= self.food_spawn_chance:
            return self.spawn_food(1)

    def spawn_food(self, n):

        unoccupied_points = self.get_unoccupied_points()
        n = min(n, len(unoccupied_points))

        if n > 0:
            point_indices = np.random.choice(len(unoccupied_points), size=n, replace=False)

            for i in range(n):
                food = Food(position=unoccupied_points[point_indices[i]])
                self.state.add_food(food)

    def get_unoccupied_points(self) -> List[Position]:
        b = self.state
        occupied: GridMap[bool] = GridMap(width=b.width, height=b.height)

        for f in b.food:
            occupied.set_value_at_position(f, True)

        for snake in b.snakes:
            for p in snake.body:
                occupied.set_value_at_position(p, True)

        unoccupied_points = []
        for y in range(b.height):
            for x in range(b.width):
                if not occupied.get_value_at(x=x, y=y):
                    unoccupied_points.append(Position(x=x, y=y))

        return unoccupied_points

    def get_even_unoccupied_points(self) -> List[Position]:

        unoccupied_points = self.get_unoccupied_points()
        even_unoccupied_points = list(filter(lambda c: (c.x + c.y) % 2 == 0, unoccupied_points))
        return even_unoccupied_points

    def is_game_over(self) -> bool:
        num_snakes_remaining = 0

        for s in self.state.snakes:
            if s.is_alive():
                num_snakes_remaining += 1

        return num_snakes_remaining <= 1