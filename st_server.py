import streamlit as st

import llm
from utils import *
from game_state import *
from host_page import host_game_page, host_lobby_page, new_game_page
from guest_page import guest_game_page, guest_lobby_page, join_game_page

def display_intro():
    st.write("Welcome to Blind Chess! In this game, players cannot see the board and must rely on verbal descriptions and memory to make their moves.")
    st.write("Click 'New Game' to create a game or 'Join Game' to enter an existing one.")
    st.write("**Game Rules:**")
    st.write("Each player takes turns to move a piece by specifying the piece type and its from/to positions. After each move, the opponent can choose to argue if they believe the move is invalid or a scam. If the argument is correct, the moving player's turn is skipped; if incorrect, the arguing player loses their next turn.")
    st.write("Especially, if the scam is caught and the king is in check, the scammer loses immediately. If a false argue leads to checkmate against the arguer, the arguer loses immediately.")
    st.write("Moving to or from the king's position requires moving the king itself. Scamming with a king is not allowed.")

def home_page():
    home_container = st.empty()
    with home_container.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("♟️ Blind Chess")
            new_col, join_col = st.columns(2)
            with new_col:
                if st.button("New Game"):
                    st.session_state.page = "new_game"
                    home_container.empty()
                    st.rerun()
            with join_col:
                if st.button("Join Game"):
                    st.session_state.page = "join_game"
                    home_container.empty()
                    st.rerun()
        display_intro()

st.set_page_config(
    page_title="Blind Chess",
    page_icon="♟️",
    layout="wide"
)
st.session_state.setdefault("page", "home")
match st.session_state.page:
    case "home":
        home_page()
    case "new_game":
        new_game_page()
    case "join_game":
        join_game_page()
    case "lobby_host":
        host_lobby_page()
    case "lobby_guest":
        guest_lobby_page()
    case "game_host":
        host_game_page()
    case "game_guest":
        guest_game_page()