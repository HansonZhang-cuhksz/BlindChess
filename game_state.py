import random
import chess

games = {}
public_games = set()

def subscribe_game(name, pwd):
    assert name in games, "Game name not found"
    assert not games[name].guest_online, "Already subscribed"
    assert games[name].pwd == pwd, "Invalid password"
    games[name].guest_online = True
    return games[name]

def unsubscribe_game(name):
    assert name in games, "Game ID not found"
    assert games[name].guest_online, "Not subscribed"
    games[name].guest_online = False

class GameState:
    def __init__(self, name, pwd, first_selection, public):
        self.name = name
        self.pwd = pwd
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
        games[name] = self
        self.is_public = public
        if public:
            public_games.add(name)

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

    def clean(self):
        assert self.name in games, "Game ID not found in registry"
        del games[self.name]
        self.exited = True
        if self.name in public_games:
            public_games.remove(self.name)

    def game_exited(self):
        return self.exited or not self.guest_online