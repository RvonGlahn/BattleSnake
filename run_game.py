from environment.battlesnake_environment import BattlesnakeEnvironment
from agents.RandomAgent import RandomAgent
from agents.KILabAgent import KILabAgent
import time

agents = [RandomAgent(), KILabAgent(), RandomAgent(), RandomAgent()]

env = BattlesnakeEnvironment(
    width=15,
    height=15,
    agents=agents,
    act_timeout=0.4,
    export_games=False
)

env.reset()
env.render()

while True:

    step_start_time = time.time()
    env.handle_input()
    env.step()
    env.render()
    step_time = int((time.time() - step_start_time) * 1000)

    env.wait_after_step(step_time)

