from environment.Battlesnake.model.board_state import BoardState
from agents.RemoteAgent import RemoteAgent
from agents.Hyperparameters import Params_Fitness
from environment.battlesnake_environment import BattlesnakeEnvironment
from agents.KILabAgent import KILabAgent
import time
import random


class FitnessFunction:

    @staticmethod
    def fitness_value():
        turn = Params_Fitness.turn
        board = Params_Fitness.board
        my_id = Params_Fitness.my_id

        snake_alive = [snake for snake in board.snakes if my_id == snake.snake_id]
        if snake_alive or len(board.snakes) > 2:
            return turn / len(board.snakes)
        else:
            return turn / len(board.snakes) + 1

    @staticmethod
    def run_game():
        # TODO: attribute error abfangen
        possible_agents = []

        remote_agent = RemoteAgent(url='130.75.31.206:8001')
        possible_agents.append(remote_agent)
        remote_agent2 = RemoteAgent(url='130.75.31.206:8002')
        possible_agents.append(remote_agent2)
        remote_agent3 = RemoteAgent(url='130.75.31.206:8003')
        possible_agents.append(remote_agent3)
        """
        remote_agent4 = RemoteAgent(url='130.75.31.206:8004')
        possible_agents.append(remote_agent4)
        remote_agent5 = RemoteAgent(url='130.75.31.206:8005')
        possible_agents.append(remote_agent5)
        """
        remote_agent6 = RemoteAgent(url='130.75.31.206:8008')
        possible_agents.append(remote_agent6)

        agents = random.choice(possible_agents)
        agents.append(KILabAgent())

        env = BattlesnakeEnvironment(
            width=11,
            height=11,
            agents=agents,
            act_timeout=0.4,
            export_games=False
        )

        env.reset()
        env.render()

        while True:
            step_start_time = time.time()
            env.handle_input()
            end = env.step()
            env.render()
            step_time = int((time.time() - step_start_time) * 1000)

            env.wait_after_step(step_time)
            if end:
                break
