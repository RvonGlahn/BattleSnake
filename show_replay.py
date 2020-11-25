import pygame
import time
import argparse

from environment.battlesnake_environment import BattlesnakeEnvironment
from environment.Battlesnake.importer.Importer import Importer
from environment.Battlesnake.renderer.game_renderer import GameRenderer

parser = argparse.ArgumentParser(description='Load and show a replay file.')
parser.add_argument('-f', '--file', help='The path to the replay file', required=True)
parser.add_argument('-t', '--tps', help='Desired ticks per second', default=5)
args = parser.parse_args()

game, turns, move_list = Importer.load_replay_file(args.file)

assert len(move_list) >= 1

# TODO: Could be moved to header
width, height = move_list[0].width, move_list[0].width
num_snakes = len(move_list[0].snakes)

renderer = GameRenderer(width, height, num_snakes)

# Note: On Mac OS there is a bug in pygame 1.9.
# when only a grey window shows up, try installing pygame version 2

# initial wait time before start
move = move_list[0]
renderer.display(move)
pygame.time.wait(3000)

for move in move_list:
    renderer.display(move)
    pygame.time.wait(int(1000 / int(args.tps)))

# wait so window doesn't close
while True:
    pygame.display.update()
