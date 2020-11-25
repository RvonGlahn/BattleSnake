import os
import json
from datetime import datetime

from environment.Battlesnake.model.GameInfo import GameInfo
from environment.Battlesnake.model.board_state import BoardState


class Exporter:

    def __init__(self, output_folder="replays", file_name=None):

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        filename = file_name or datetime.now().strftime('%y-%m-%d_%H-%M-%S')
        if not filename.endswith(".replay"):
            filename += ".replay"

        self.outpath = os.path.join(output_folder, filename)
        self.tempfile = os.path.join(output_folder, filename.replace(".replay", ".temp"))

        self.game_meta_info = {}
        self.history = []

    def add_initial_state(self, game_info: GameInfo):
        self.game_meta_info = game_info.export_json()

    def add_latest_game_step(self, game):
        self.history.append({
            "height": game.state.height,
            "width": game.state.width,
            "food": [f.export_json() for f in game.state.food],
            "snakes": [s.export_json() for s in game.state.all_snakes]
        })

        if game.is_game_over():
            self.write_replay_to_file()

    def write_replay_to_file(self):
        with open(self.tempfile, "w+") as f:
            json.dump({
                "game": self.game_meta_info,
                "total_turns": len(self.history),
                "moves": self.history
            }, f)

        os.rename(self.tempfile, self.outpath)
        print(f"Success! Wrote to {self.outpath}")
