import unittest

from environment.Battlesnake.model.Food import Food
from environment.Battlesnake.model.Position import Position
from environment.Battlesnake.model.Snake import Snake
from environment.Battlesnake.model.board_state import BoardState


class BoardTestCase(unittest.TestCase):

    def test_clone(self):

        snake_a = Snake(snake_id="snake-a", body=[Position(x=3, y=3)])
        snake_b = Snake(snake_id="snake-a", body=[Position(x=9, y=9)])

        food_a = Food(x=1, y=2)

        snakes = [snake_a, snake_b]
        food = [food_a]

        board = BoardState(
            width=15,
            height=15,
            snakes=snakes,
            food=food
        )

        board_clone = board.clone()

        self.assertNotEqual(id(board), id(board_clone))
        self.assertNotEqual(id(board.snakes[0]), id(board_clone.snakes[0]))
        self.assertNotEqual(id(board.food[0]), id(board_clone.food[0]))

        board_export = board.to_json()
        board_clone_export = board_clone.to_json()

        self.assertEqual(board_export, board_clone_export)


if __name__ == '__main__':
    unittest.main()
