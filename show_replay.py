import pygame
import time
import argparse

from environment.Battlesnake.renderer.replay_controller import ReplayController
from environment.Battlesnake.importer.Importer import Importer

p = None
p = "/Users/christoph/ownCloud/KI-Labor/WS2020/Battlesnake/Wettbewerbe/Starter-Wettbewerb/Halbfinale/ichheissemarvin_Xiangliu_20-12-01_22-31-55.replay"
p = "/Users/christoph/ownCloud/KI-Labor/WS2020/Battlesnake/Wettbewerbe/Starter-Wettbewerb/Finale/TöndervonHaval_ichheissemarvin_20-12-01_20-57-09.replay"
p2 = "/Users/christoph/ownCloud/KI-Labor/WS2020/Battlesnake/Wettbewerbe/Starter-Wettbewerb/Vorrunde/"

parser = argparse.ArgumentParser(description='Load and show a replay file.')
parser.add_argument('-f', '--file', help='The path to the replay file', required=False, default=p)
args = parser.parse_args()

game, turns, move_list = Importer.load_replay_file(args.file)

assert len(move_list) >= 1

replay_controller = ReplayController(move_list)
replay_controller.load_replays_from_folder(p2)

replay_controller.show_game(0)
# Note: On Mac OS there is a bug in pygame 1.9.
# when only a grey window shows up, try installing pygame version 2

while True:
    replay_controller.update()
    pygame.time.wait(10)
