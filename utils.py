import time
import os
import random
import json
import streamlit as st

FAST_DELAY = 0.1
PAGE_REFRESH_DELAY = 0.5
SLOW_DELAY = 3.0

def get_pos_str(x, y):
    x = int(x)
    y = int(y)
    return "ABCDEFGHI"[y] + str(x)

def rmdir_thread(pth):
    while os.path.exists(pth):
        try:
            os.rmdir(pth)
        except OSError:
            time.sleep(FAST_DELAY)
        except PermissionError:
            time.sleep(FAST_DELAY)

def get_random_id(existing_ids=set()):
    new_id = random.randint(0, 0xFFFFFFFF)
    while new_id in existing_ids:
        new_id = random.randint(0, 0xFFFFFFFF)
    return new_id

def read_games(read_only=False):
    while True:
        with open(f"games.json", "r") as f:
            games = json.load(f)
        if games["lock"] == 0:
            if not read_only:
                games["lock"] = 1
                with open(f"games.json", "w") as f:
                    json.dump(games, f)
            return games
        time.sleep(FAST_DELAY)

def write_games(games):
    with open(f"games.json", "r") as f:
        current_games = json.load(f)
    assert current_games["lock"] == 1, "Lock not acquired"
    with open(f"games.json", "w") as f:
        games["lock"] = 0
        json.dump(games, f)

def read_game_data():
    while True:
        try:
            with open(f"games/{st.session_state.game_id}/game_data.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
        except FileNotFoundError:
            st.session_state.page = "home"
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def write_game_data(game_data):
    with open(f"games/{st.session_state.game_id}/game_data.json", "w") as f:
        json.dump(game_data, f)