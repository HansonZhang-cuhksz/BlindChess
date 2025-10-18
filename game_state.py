import streamlit as st
from utils import *
import chess

games = {}

def subscribe_game(game_id, pwd):
    assert game_id in games, "Game ID not found"
    assert not games[game_id].guest_online, "Already subscribed"
    assert games[game_id].pwd == pwd, "Invalid password"
    games[game_id].guest_online = True
    return games[game_id]
    
def unsubscribe_game(game_id):
    assert game_id in games, "Game ID not found"
    assert games[game_id].guest_online, "Not subscribed"
    games[game_id].guest_online = False

class GameState:
    def __init__(self, pwd, game_id, first_selection):
        self.pwd = pwd
        self.game_id = game_id
        if first_selection == "Random":
            self.first = random.choice(["Host", "Guest"])
        else:
            self.first = "Host" if first_selection == "Me" else "Guest"
        self.guest_online = False
        self.board = chess.Board()
        self.started = False
        self.exited = False
        self._host_to_guest = ""
        self._guest_to_host = ""
        games[game_id] = self

    def read_guest(self):
        ret = self._guest_to_host
        self._guest_to_host = ""
        return ret
    
    def write_guest(self, msg):
        self._host_to_guest = msg

    def read_host(self):
        ret = self._host_to_guest
        self._host_to_guest = ""
        return ret

    def write_host(self, msg):
        self._guest_to_host = msg

    def __del__(self):
        assert self.game_id in games, "Game ID not found in registry"
        del games[self.game_id]
        self.exited = True

    def game_exited(self):
        return self.exited or not self.guest_online