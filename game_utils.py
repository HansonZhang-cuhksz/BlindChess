import streamlit as st
import time

import chess
from utils import *

def cancel_move():
    st.session_state.pos_from = None
    st.session_state.pos_to = None
    st.session_state.selected_piece = None
    st.rerun()

def game_default(first):
    st.session_state.setdefault("status", "move" if first else "wait_move")
    st.session_state.setdefault("selected_piece", None)
    st.session_state.setdefault("info", ("info", ""))
    st.session_state.setdefault("last_info", ("info", ""))
    st.session_state.setdefault("temp_info", ("info", ""))
    st.session_state.setdefault("pos_from", None)
    st.session_state.setdefault("pos_to", None)

def display_msg():
    match st.session_state.status:
        case "wait_move":
            st.session_state.info = ("info","Waiting for opponent's move...")
        case "wait_argue":
            st.session_state.info = ("info","Waiting for opponent's argue...")
        case "move":
            st.session_state.info = ("info","Your turn to move")
    match st.session_state.info[0]:
        case "info":
            st.info(st.session_state.info[1])
        case "error":
            st.error(st.session_state.info[1])
        case "success":
            st.success(st.session_state.info[1])
    if st.session_state.last_info != st.session_state.info:
        st.session_state.temp_info = ("info", "")
    match st.session_state.temp_info[0]:
        case "info":
            st.info(st.session_state.temp_info[1])
        case "error":
            st.error(st.session_state.temp_info[1])
        case "success":
            st.success(st.session_state.temp_info[1])
    st.session_state.last_info = st.session_state.info

def display_board():
    cols = st.columns(10)
    for col_idx in range(1, 10):
        with cols[col_idx]:
            st.write("ABCDEFGHI"[col_idx - 1])
    for row in range(10):
        cols = st.columns(10)
        with cols[0]:
            st.write(row)
        for col_idx in range(1, 10):
            with cols[col_idx]:
                label = "⬜"
                if (row, col_idx - 1) == st.session_state.pos_from:
                    label = "🟦"
                if (row, col_idx - 1) == st.session_state.pos_to:
                    label = "🟩"
                if st.session_state.status == "argue":
                    if (row, col_idx - 1) == st.session_state.last_move[0:2]:
                        label = "🟥"
                    if (row, col_idx - 1) == st.session_state.last_move[3:5]:
                        label = "🟧"
                if st.button(label, key=f"{row}_{col_idx}"):
                    if st.session_state.status == "move":
                        if not st.session_state.pos_from:
                            st.session_state.pos_from = (row, col_idx - 1)
                            st.rerun()
                        elif not st.session_state.pos_to:
                            st.session_state.pos_to = (row, col_idx - 1)
                            st.rerun()

def display_options(handle_confirm_func, handle_cancel_func):
    st.write("")
    st.write("")
    st.write("")
    for piece_type in chess.PIECE_TYPES:
        if st.button(piece_type):
            if st.session_state.status == "move":
                st.session_state.selected_piece = piece_type
    if st.button("Confirm"):
        handle_confirm_func()
    if st.button("Cancel"):
        handle_cancel_func()
    if st.session_state.selected_piece:
        st.write(st.session_state.selected_piece)

def check_opponent_exit(exit_game_func):
    if st.session_state.game_state.game_exited():
        st.error("Opponent has left the game. Returning to home page...")
        time.sleep(SLOW_DELAY)
        exit_game_func()

def game_page(first, exit_game_func, handle_cmd_func, handle_confirm_func, handle_cancel_func):
    game_default(first)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Back to Home"):
            exit_game_func()
        display_msg()
    with col2:
        display_board()
    with col3:
        display_options(handle_confirm_func, handle_cancel_func)
    check_opponent_exit(exit_game_func)
    handle_cmd_func()
    time.sleep(PAGE_REFRESH_DELAY)
    st.rerun()