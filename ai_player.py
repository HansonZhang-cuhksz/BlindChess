import streamlit as st

from llm import query

def ai_thread():
    while not st.session_state.game_state.exited:
        pass