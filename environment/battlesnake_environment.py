import multiprocessing

from agents.BaseAgent import BaseAgent
from typing import List, Optional, Dict
import pygame
import sys
import time
import traceback
from copy import deepcopy

from environment.Battlesnake.model.errors import AgentTimeoutError
from environment.Battlesnake.modes.Standard import StandardGame
from environment.Battlesnake.modes.AbstractGame import AbstractGame
from environment.Battlesnake.renderer.field_color import FieldColor
from environment.Battlesnake.renderer.game_renderer import GameRenderer
from environment.Battlesnake.helper.helper import Helper
from environment.Battlesnake.exporter.Exporter import Exporter

default_colors = [
    FieldColor.SNAKE_1_DEFAULT,
    FieldColor.SNAKE_2_DEFAULT,
    FieldColor.SNAKE_3_DEFAULT,
    FieldColor.SNAKE_4_DEFAULT,
]


class BattlesnakeEnvironment:

    def __init__(
            self,
            width: int,
            height: int,
            agents: List[BaseAgent],
            act_timeout: float,
            start_paused=False,
            speed_initial=1,
            export_games=False
    ):
        self.width = width
        self.height = height
        self.num_snakes = len(agents)
        self.snake_ids = None
        self.agents: List[BaseAgent] = agents
        self.game: Optional[AbstractGame] = None
        self.game_renderer = None
        self.act_timeout = act_timeout
        self.default_snake_colors = None

        self.speed = speed_initial
        self.paused = start_paused

        if self.paused:
            print("Press P to start game")

        self.export_games = export_games
        self.exporter = None

    def reset(self):

        self.snake_ids = [Helper.generate_snake_id() for _ in range(self.num_snakes)]

        self.default_snake_colors = default_colors.copy()

        self.exporter = Exporter() if self.export_games else None

        self.game = StandardGame(timeout=int(self.act_timeout * 1000))
        self.game.create_initial_board_state(width=self.width, height=self.height, snake_ids=self.snake_ids)

        self.update_snake_infos()
        self.game_renderer = GameRenderer(self.width, self.height, self.num_snakes)

        if self.export_games:
            self.exporter.add_initial_state(self.game.game_info)

    def update_snake_infos(self):

        board = self.game.state
        colors = self.default_snake_colors

        for idx, agent in enumerate(self.agents):
            snake_id = self.snake_ids[idx]
            snake = board.get_snake_by_id(snake_id)
            name = agent.get_name()
            color = agent.get_color()

            snake.snake_name = name

            if snake.snake_color is None:
                if color is None:
                    color = colors.pop(0)
                    colors.append(color)

                snake.snake_color = color

    def handle_input(self):

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                # print(event.key)
                self.user_key_pressed(event.key)

            elif event.type == pygame.QUIT:
                print("Game quit by user!")
                pygame.quit()
                sys.exit()

    def step(self):
        """
        :return: Gibt zurück, ob das Spiel beendet wurde
        """

        if self.paused:
            return

        if self.game.is_game_over():
            return True

        actions = {}
        board = self.game.state
        game_info = self.game.game_info
        turn = self.game.turn

        for idx, snake_id in enumerate(self.snake_ids):
            agent = self.agents[idx]
            snake = board.get_snake_by_id(snake_id)

            if turn == 0:
                BattlesnakeEnvironment.copy_and_call(
                    agent.start, timeout=2, snake_name=snake.snake_name,
                    game_info=game_info, turn=turn, board=board, you=snake)

            if not snake.is_alive():
                continue

            agent_action = None
            # IDEA: use Process and set timeout
            agent_move_result = BattlesnakeEnvironment.copy_and_call(
                agent.move, timeout=self.act_timeout, snake_name=snake.snake_name,
                game_info=game_info, turn=turn, board=board, you=snake)

            if agent_move_result is not None:
                agent_action = agent_move_result.direction

            actions[snake_id] = agent_action

        self.game.create_next_board_state(actions)

        if self.export_games:
            self.exporter.add_latest_game_step(self.game)

        is_game_over = self.game.is_game_over()
        for idx, snake_id in enumerate(self.snake_ids):
            agent = self.agents[idx]
            snake = board.get_snake_by_id(snake_id)

            call_end = False
            if not snake.is_alive() and snake.elimination_event.turn == turn:
                # check if snake dead in this turn
                call_end = True

            elif is_game_over:
                # notify alive snake that game has ended
                call_end = True

            if call_end:
                BattlesnakeEnvironment.copy_and_call(
                    agent.end, timeout=2,  snake_name=snake.snake_name,
                    game_info=game_info, turn=turn, board=board, you=snake)

        return is_game_over

    def render(self):
        self.game_renderer.display(self.game.state)

    def wait_after_step(self, action_time=0):

        if self.game.is_game_over():
            wait_time = 100
        else:

            if self.speed == 3:
                wait_time = 0
            elif self.speed == 2:
                wait_time = 100
            else:
                wait_time = 250

        final_wait_time = max(0, wait_time - action_time)
        if final_wait_time > 0:
            pygame.time.wait(final_wait_time)

    def wait_after_round(self):

        if self.speed == 3:
            wait_time = 500
        elif self.speed == 2:
            wait_time = 1000
        else:
            wait_time = 1500

        if wait_time > 0:
            pygame.time.wait(wait_time)

    def user_key_pressed(self, key):

        if key == pygame.K_r:
            print('user pressed reset')
            self.reset()

        elif key == pygame.K_1:
            print('set speed: 1')
            self.speed = 1

        elif key == pygame.K_2:
            print('set speed: 2')
            self.speed = 2

        elif key == pygame.K_3:
            print('set speed: 3')
            self.speed = 3

        elif key == pygame.K_p:
            print('toggle pause')
            self.paused = not self.paused

        else:
            for agent in self.agents:
                agent.user_key_pressed(key)

    @staticmethod
    def copy_and_call(func, timeout=None, snake_name=None, **kwargs):

        kwargs = deepcopy(kwargs)

        try:

            # return BattlesnakeEnvironment.call_process(func=func, timeout=timeout, **kwargs)
            return BattlesnakeEnvironment.call_sync(func=func, timeout=timeout, **kwargs)

        except AgentTimeoutError:
            print(
                'snake {}: timeout after {} seconds'.format(snake_name, timeout))

        except Exception:
            traceback.print_exc()
            print('snake {}: Exception raised in act method of agent'.format(snake_name))

    @staticmethod
    def call_sync(func, timeout=None, **kwargs):

        act_start_time = time.time()
        result = func(**kwargs)
        act_time = time.time() - act_start_time

        if timeout is not None:
            if act_time > timeout:
                raise AgentTimeoutError()

        return result

    @staticmethod
    def call_process(func, timeout=None, **kwargs):
        # TODO implement

        print('call_process with timeout {}'.format(timeout))
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        return_dict['test'] = 1

        def call(d, **kwargs):
            print('hello world')
            print(id(kwargs['board']))

            # print('got', kwargs)
            for i in range(4):
                print(i)
                time.sleep(1)

            d['call'] = 2
            print(d)

        p = multiprocessing.Process(target=call, args=(return_dict, ), kwargs=kwargs)
        p.start()

        # Wait for X seconds or until process finishes
        p.join(timeout=timeout)

        if p.exitcode is None:
            # agent did not terminate in time
            p.terminate()
            # p.join()
            raise AgentTimeoutError()

        print('x')
