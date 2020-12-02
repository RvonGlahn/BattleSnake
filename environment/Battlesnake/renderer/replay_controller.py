import pygame

from environment.Battlesnake.importer.Importer import Importer
from environment.Battlesnake.renderer.game_renderer import GameRenderer
import sys
import time
import os
from tkinter import *  # not advisable to import everything with *
# from tkinter import filedialog

# root = Tk()


class ReplayController:

    def __init__(self, board_states):
        self.games = []
        self.games_index = 0
        self.board_states = board_states
        self.paused = False
        self.current_step = 0
        self.speed = 1
        self.last_step_ts = time.time()
        self.renderer = None


        self.reset()
        # self.open_masker()

    def show_game(self, index):
        self.games_index = index
        board_states = self.games[index]

        width, height = self.board_states[0].width, self.board_states[0].width
        num_snakes = len(self.board_states[0].snakes)

        self.renderer = GameRenderer(width, height, num_snakes)

        self.board_states = board_states
        self.reset()

    def reset(self):

        self.show_step(0)
        self.set_speed(1)

    def set_speed(self, s):
        self.speed = s
        w = self.get_step_wait_time()
        x = max(int(w*1000), 20)
        pygame.key.set_repeat(200, x)

    def update(self):

        self.handle_input()
        self.handle_step_replay()

        # root.update_idletasks()
        # root.update()

    def show_step(self, index):
        if index < 0 or index >= len(self.board_states):
            return

        self.last_step_ts = time.time()
        self.current_step = index
        move = self.board_states[index]

        if self.renderer is not None:
            self.renderer.display(move)

    def handle_step_replay(self):

        if self.paused:
            return

        now = time.time()
        time_diff = now - self.last_step_ts

        if time_diff >= self.get_step_wait_time():
            self.go_forward()

    def get_step_wait_time(self):
        if self.speed == 3:
            return 0
        elif self.speed == 2:
            return 0.100
        else:
            return 0.250

    def toggle_pause(self):
        self.paused = not self.paused
        self.last_step_ts = time.time()

    def go_back(self):
        self.show_step(self.current_step - 1)

    def go_forward(self):
        self.show_step(self.current_step + 1)

    def handle_input(self):

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                # print(event.key)
                self.user_key_pressed(event.key)

            elif event.type == pygame.KEYUP:
                pass

            elif event.type == pygame.QUIT:
                print("Game quit by user!")
                pygame.quit()
                sys.exit()

    def user_key_pressed(self, key):
        # print('key', key)

        if key == pygame.K_r:
            print('user pressed reset')
            self.reset()

        elif key == pygame.K_1:
            print('set speed: 1')
            self.set_speed(1)

        elif key == pygame.K_2:
            print('set speed: 2')
            self.set_speed(2)

        elif key == pygame.K_3:
            print('set speed: 3')
            self.set_speed(3)

        elif key == pygame.K_LEFT:
            print('previous state')
            self.paused = True
            self.go_back()

        elif key == pygame.K_RIGHT:
            print('next state')
            self.paused = True
            self.go_forward()

        elif key == pygame.K_p:
            print('toggle pause')
            self.toggle_pause()

    # def open_masker(self):
    #     global audio_file_name
    #     audio_file_name = filedialog.askopenfilename(filetypes=(("Audio Files", ".wav .ogg"),   ("All Files", "*.*")))

    def load_replay(self, replay_path):
        print('load', replay_path)
        game, turns, move_list = Importer.load_replay_file(replay_path)
        if len(move_list) == 0:
            print('replay is empty')
            return

        self.games.append(move_list)

    def load_replays_from_folder(self, folder_path):

        replay_paths = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            extension = os.path.splitext(filename)[1]
            if not os.path.isfile(file_path) or extension != '.replay':
                continue

        for replay_path in replay_paths:
            self.load_replay(replay_path)
