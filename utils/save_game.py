import os
import json

def initiate_save_file():
    with open("game.json", "w") as f:
        data = {
            "current_level": 1
        }
        json.dump(data, f)
        
def save_game(level):
    with open("game.json", "w") as f:
        data = {
            "current_level": level
        }
        json.dump(data, f)
        
def load_game_level():
    if not os.path.exists("game.json"):
        initiate_save_file()
        
    with open("game.json", "r") as f:
        data = json.load(f)
        return data["current_level"]