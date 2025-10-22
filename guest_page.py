import streamlit as st
import time

import chess
from utils import *
from game_state import *
from game_utils import *

def exit_game():
    unsubscribe_game(st.session_state.game_state.name)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.page = "home"
    st.rerun()

def handle_host_cmd():
    st.session_state.game_state.read_host_cmd = st.session_state.game_state.read_host()
    if st.session_state.game_state.read_host_cmd:
        st.session_state.game_state.read_host_cmd = st.session_state.game_state.read_host_cmd.split()
        match st.session_state.game_state.read_host_cmd[0]:
            case "move":
                assert st.session_state.status == "wait_move", f"Not waiting for move, status is {st.session_state.status}"
                _, x, y, piece_type, tx, ty = st.session_state.game_state.read_host_cmd
                x, y, tx, ty = 9 - int(x), 8 - int(y), 9 - int(tx), 8 - int(ty)
                st.session_state.last_move = (x, y, piece_type, tx, ty)
                st.session_state.info = ("info",f"Opponent moved {piece_type} from {get_pos_str(x, y)} to {get_pos_str(tx, ty)}. Your turn to argue.")
                st.session_state.status = "argue"
            case "validate":
                assert st.session_state.status == "wait_validation", f"Not waiting for validation, status is {st.session_state.status}"
                match st.session_state.game_state.read_host_cmd[1]:
                    case "pass":
                        st.session_state.game_state.write_host("validated")
                        st.session_state.status = "wait_argue"
                    case "king_override":
                        st.session_state.temp_info = ("error","You must move the king when moving to or from the king's position. Try again.")
                        st.session_state.status = "move"
                        cancel_move()
                    case "scam_king":
                        st.session_state.temp_info = ("error","You cannot scam with a king. Try again.")
                        st.session_state.status = "move"
                        cancel_move()
                    case "checkmate":
                        st.session_state.temp_info = ("error","Move puts own king in check. Try again.")
                        st.session_state.status = "move"
                        cancel_move()
            case "caught":
                assert st.session_state.status == "argue", f"Not processing argue, status is {st.session_state.status}"
                st.session_state.temp_info = ("error","Caught a scam! Opponent's turn skipped.")
                st.session_state.status = "move"
            case "false":
                assert st.session_state.status == "argue", f"Not processing argue, status is {st.session_state.status}"
                st.session_state.temp_info = ("error","False argue! Your turn skipped.")
                st.session_state.status = "wait_move"
            case "accepted":
                assert st.session_state.status == "argue", f"Not processing argue, status is {st.session_state.status}"
                st.session_state.temp_info = ("info","Accepted. Your turn.")
                st.session_state.status = "move"
            case "opponent":
                assert st.session_state.status == "wait_argue", f"Not waiting for argue, status is {st.session_state.status}"
                match st.session_state.game_state.read_host_cmd[1]:
                    case "caught":
                        st.session_state.temp_info = ("error","Scam caught! Your turn skipped.")
                        st.session_state.status = "wait_move"
                    case "false":
                        st.session_state.temp_info = ("info","Opponent false argue! Opponent's turn skipped.")
                        st.session_state.status = "move"
                    case "accepted":
                        st.session_state.temp_info = ("info","Opponent accepted. Waiting for your move.")
                        st.session_state.status = "wait_move"
            case "win":
                match st.session_state.game_state.read_host_cmd[1]:
                    case "scam_caught":
                        st.session_state.info = ("success","You win: Opponent Scam Caught.")
                    case "false_argue":
                        st.session_state.info = ("success","You win: Opponent False Argue.")
                    case "Checkmate":
                        st.session_state.info = ("success","You win: Checkmate.")
                st.session_state.status = "ended"
                st.rerun()
            case "lose":
                match st.session_state.game_state.read_host_cmd[1]:
                    case "scam_caught":
                        st.session_state.info = ("error","You lose: Scam Caught.")
                    case "false_argue":
                        st.session_state.info = ("error","You lose: False Argue.")
                    case "Checkmate":
                        st.session_state.info = ("error","You lose: Checkmate.")
                st.session_state.status = "ended"
                st.rerun()

def handle_confirm():
    match st.session_state.status:
        case "argue":
            st.session_state.game_state.write_host("argue y")
        case "move":
            if not (st.session_state.pos_from and st.session_state.pos_to and st.session_state.selected_piece):
                st.session_state.temp_info = ("error","Please select from, to positions and piece type.")
                st.rerun()
            x, y, piece_type, tx, ty = *st.session_state.pos_from, st.session_state.selected_piece, *st.session_state.pos_to
            st.session_state.game_state.write_host("move " + " ".join(map(str, [9 - x, 8 - y, piece_type, 9 - tx, 8 - ty])))
            st.session_state.status = "wait_validation"
            cancel_move()

def handle_cancel():
    match st.session_state.status:
        case "argue":
            st.session_state.game_state.write_host("argue n")
        case "move":
            st.session_state.temp_info = ("info","Move cancelled")
            cancel_move()

def guest_game_page():
    game_page(
        st.session_state.game_state.first != "Host",
        exit_game,
        handle_host_cmd,
        handle_confirm,
        handle_cancel
    )

def join_game(name, password, join_game_container):
    try:
        st.session_state.game_state = subscribe_game(name, password)
    except AssertionError as e:
        match str(e):
            case "Game ID not found":
                st.error("Game ID does not exist.")
            case "Already subscribed":
                st.error("Game is already full.")
            case "Invalid password":
                st.error("Incorrect password.")
        st.stop()
    st.session_state.is_host = False
    st.session_state.page = "lobby_guest"
    join_game_container.empty()
    st.rerun()

def join_game_page():
    join_game_container = st.empty()
    with join_game_container.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Refresh"):
                st.rerun()
        with col2:
            st.subheader("Join an Existing Game")
            name = st.text_input("Game Name:")
            password = st.text_input("Password (Optional):", type="password")
            if st.button("Join Game"):
                join_game(name, password, join_game_container)
            if st.button("Back to Home"):
                st.session_state.page = "home"
                join_game_container.empty()
                st.rerun()
            st.write("**Available Public Games:**")
            for name in public_games:
                st.write(name)

def guest_lobby_page():
    if st.session_state.game_state.name in public_games:
        public_games.remove(st.session_state.game_state.name)
    lobby_guest_container = st.empty()
    with lobby_guest_container.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Back to Home"):
                if st.session_state.game_state.is_public:
                    public_games.add(st.session_state.game_state.name)
                exit_game()
            if st.session_state.game_state.exited:
                st.error("Host has closed the game. Returning to home page...")
                time.sleep(SLOW_DELAY)
                exit_game()
            if not st.session_state.game_state.started:
                st.info("⏳ Waiting for host to start the game...")
                time.sleep(PAGE_REFRESH_DELAY)
                st.rerun()
    st.session_state.page = "game_guest"
    lobby_guest_container.empty()
    st.rerun()