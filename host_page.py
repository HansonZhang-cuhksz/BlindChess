import streamlit as st
import time

import chess
from utils import *
from game_state import *
from game_utils import *

def exit_game():
    st.session_state.game_state.clean()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.page = "home"
    st.rerun()

def handle_move(x, y, piece_type, tx, ty, board, turn):
    while True:
        this_king = board.find_king(turn)
        opponent_king = board.find_king(chess.opposite_color(turn))
        if (x, y) == this_king or (tx, ty) == this_king or (x, y) == opponent_king or (tx, ty) == opponent_king:
            if piece_type != '将':
                if st.session_state.color == turn:
                    st.session_state.temp_info = ("error","You must move the king when moving to or from the king's position. Try again.")
                    cancel_move()
                    continue
                else:
                    st.session_state.game_state.write_guest("validate king_override")
                    return
                    
        piece = None
        is_scam = False
        is_imaginary = False
        original_chess = None
        define_original_chess = False
        if not board.grid[x][y]:
            if piece_type == '将':
                if st.session_state.color == turn:
                    st.session_state.temp_info = ("error","You cannot scam with a king. Try again.")
                    cancel_move()
                    continue
                else:
                    st.session_state.game_state.write_guest("validate scam_king")
                    return
            piece = chess.Chess(board, piece_type, turn, (x, y))
            is_scam = True
            is_imaginary = True
        elif board.grid[x][y].color == turn and board.grid[x][y].type == piece_type:
            piece = board.grid[x][y]
            if (tx, ty) not in [move.end for move in piece.get_allowed_moves()]:
                is_scam = True
        else:
            if piece_type == '将':
                if st.session_state.color == turn:
                    st.session_state.temp_info = ("error","You cannot scam with a king. Try again.")
                    cancel_move()
                    continue
                else:
                    st.session_state.game_state.write_guest("validate scam_king")
                    return
            piece = chess.Chess(board, piece_type, turn, (x, y))
            original_chess = board.grid[x][y]
            define_original_chess = True
            is_scam = True
            is_imaginary = True
        move = chess.Move(piece, (tx, ty), is_imaginary, original_chess, define_original_chess)
        move.run()
        if board.king_in_check(turn):
            if st.session_state.color == turn:
                st.session_state.temp_info = ("error","Move puts own king in check. Try again.")
                cancel_move()
                continue
            else:
                st.session_state.game_state.write_guest("validate checkmate")
            move.undo()
            return is_scam
        else:
            if st.session_state.color != turn:
                st.session_state.game_state.write_guest("validate pass")
            move.undo()
            return is_scam

def handle_argue(last_move, argue, is_scam, board, turn):
    def handle_argue_host(argue, is_scam, board, last_board, turn):
        if argue.lower() == 'y':
            if is_scam:
                if last_board.king_in_check(turn):
                    st.session_state.info = ("success","You win: Opponent Scam Caught.")
                    st.session_state.game_state.write_guest("lose scam_caught")
                    st.session_state.status = "ended"
                    st.rerun()
                st.session_state.temp_info = ("info","Caught a scam! Opponent's turn skipped.")
                st.session_state.status = "move"
                st.session_state.game_state.write_guest("opponent caught")
                run = False
            else:
                if board.king_in_check(chess.opposite_color(turn)):
                    st.session_state.info = ("info","You lose: False Argue.")
                    st.session_state.game_state.write_guest("win false_argue")
                    st.session_state.status = "ended"
                    st.rerun()
                st.session_state.temp_info = ("error","False argue! Your turn skipped.")
                st.session_state.status = "wait_move"
                st.session_state.game_state.write_guest("opponent false")
                run = True
        else:
            st.session_state.temp_info = ("info","Opponent accepted.")
            st.session_state.status = "move"
            st.session_state.game_state.write_guest("opponent accepted")
            run = True
        if run:
            if board.is_terminated(chess.opposite_color(turn)):
                st.session_state.info = ("error","You lose: Checkmate.")
                st.session_state.game_state.write_guest("win Checkmate")
                st.session_state.status = "ended"
                st.rerun()
            return board
        else:
            return last_board

    def handle_argue_guest(argue, is_scam, board, last_board, turn):
        if argue.lower() == 'y':
            if is_scam:
                if last_board.king_in_check(turn):
                    st.session_state.info = ("error","You lose: Scam Caught.")
                    st.session_state.game_state.write_guest("win scam_caught")
                    st.session_state.status = "ended"
                    st.rerun()
                st.session_state.temp_info = ("error","Scam caught! Your turn skipped.")
                st.session_state.status = "wait_move"
                st.session_state.game_state.write_guest("caught")
                run = False
            else:
                if board.king_in_check(chess.opposite_color(turn)):
                    st.session_state.info = ("success","You win: Opponent False Argue.")
                    st.session_state.game_state.write_guest("lose false_argue")
                    st.session_state.status = "ended"
                    st.rerun()
                st.session_state.temp_info = ("info","Opponent false argue! Opponent's turn skipped.")
                st.session_state.status = "move"
                st.session_state.game_state.write_guest("false")
                run = True
        else:
            st.session_state.temp_info = ("info","Opponent accepted.")
            st.session_state.status = "wait_move"
            st.session_state.game_state.write_guest("accepted")
            run = True
        if run:
            if board.is_terminated(chess.opposite_color(turn)):
                st.session_state.info = ("success","You win: Checkmate.")
                st.session_state.game_state.write_guest("lose Checkmate")
                st.session_state.status = "ended"
                st.rerun()
            return board
        else:
            return last_board
    x, y, piece_type, tx, ty = last_move
    last_board = board.copy()
    if board.grid[x][y]:
        piece = board.grid[x][y]
    else:
        piece = chess.Chess(board, piece_type, turn, (x, y))
        board.grid[x][y] = piece
    move = chess.Move(piece, (tx, ty))
    move.run()
    if st.session_state.color == turn:
        return handle_argue_guest(argue, is_scam, board, last_board, turn)
    else:
        return handle_argue_host(argue, is_scam, board, last_board, turn)
    
def handle_guest_cmd():
    st.session_state.game_state.read_guest_cmd = st.session_state.game_state.read_guest()
    if st.session_state.game_state.read_guest_cmd:
        st.session_state.game_state.read_guest_cmd = st.session_state.game_state.read_guest_cmd.split()
        match st.session_state.game_state.read_guest_cmd[0]:
            case "move":
                x, y, piece_type, tx, ty = int(st.session_state.game_state.read_guest_cmd[1]), int(st.session_state.game_state.read_guest_cmd[2]), st.session_state.game_state.read_guest_cmd[3], int(st.session_state.game_state.read_guest_cmd[4]), int(st.session_state.game_state.read_guest_cmd[5])
                st.session_state.last_move = (x, y, piece_type, tx, ty)
                st.session_state.opponent_is_scam = handle_move(x, y, piece_type, tx, ty, st.session_state.game_state.board, chess.opposite_color(st.session_state.color))
            case "argue":
                st.session_state.game_state.board = handle_argue(st.session_state.last_move, st.session_state.game_state.read_guest_cmd[1], st.session_state.opponent_is_scam, st.session_state.game_state.board, st.session_state.color)
            case "validated":
                x, y, piece_type, tx, ty = st.session_state.last_move
                st.session_state.info = ("info",f"Opponent moved {piece_type} from {get_pos_str(x, y)} to {get_pos_str(tx, ty)}. Your turn to argue.")
                st.session_state.status = "argue"

def handle_confirm():
    match st.session_state.status:
        case "argue":
            st.session_state.game_state.board = handle_argue(st.session_state.last_move, "y", st.session_state.opponent_is_scam, st.session_state.game_state.board, chess.opposite_color(st.session_state.color))
        case "move":
            if not (st.session_state.pos_from and st.session_state.pos_to and st.session_state.selected_piece):
                st.session_state.temp_info = ("error","Please select from, to positions and piece type.")
                st.rerun()
            x, y, piece_type, tx, ty = *st.session_state.pos_from, st.session_state.selected_piece, *st.session_state.pos_to
            st.session_state.opponent_is_scam = handle_move(x, y, piece_type, tx, ty, st.session_state.game_state.board, st.session_state.color)
            st.session_state.game_state.write_guest("move " + " ".join(map(str, [x, y, piece_type, tx, ty])))
            st.session_state.last_move = (x, y, piece_type, tx, ty)
            st.session_state.status = "wait_argue"
            cancel_move()

def handle_cancel():
    match st.session_state.status:
        case "argue":
            st.session_state.game_state.board = handle_argue(st.session_state.last_move, "n", st.session_state.opponent_is_scam, st.session_state.game_state.board, chess.opposite_color(st.session_state.color))
        case "move":
            st.session_state.temp_info = ("info","Move cancelled")
            cancel_move()

def host_game_page():
    game_page(
        st.session_state.game_state.first == "Host",
        exit_game,
        handle_guest_cmd,
        handle_confirm,
        handle_cancel
    )

def new_game_page():
    new_game_container = st.empty()
    with new_game_container.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.subheader("Create a New Game")
            ai_opponent = st.checkbox("Play against AI Opponent", value=False)
            if not ai_opponent:
                name = st.text_input("Game Name (Optional):", value="")
                password = st.text_input("Password (Optional):", type="password")
                public = st.checkbox("Public Game (Visible to others)", value=False)
            else:
                name = "AI_Game_" + str(random.randint(0, 0xFFFFFFFF))
                password = ""
                public = False
            first_selection = st.selectbox("First:", ["Random", "Me", "Opponent"])
            if st.button("Create Game"):
                if not name:
                    name = "Game_" + str(random.randint(0, 0xFFFFFFFF))
                if name in games:
                    st.error("Game name already exists. Please choose another name.")
                    st.stop()
                st.session_state.game_state = GameState(name, password, first_selection, public, use_ai=ai_opponent)
                st.session_state.is_host = True
                st.session_state.page = "lobby_host"
                new_game_container.empty()
                st.rerun()
            if st.button("Back to Home"):
                st.session_state.page = "home"
                new_game_container.empty()
                st.rerun()

def host_lobby_page():
    lobby_host_container = st.empty()
    with lobby_host_container.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Back to Home"):
                exit_game()
            if not st.session_state.game_state.guest_online:
                st.info("Game Name: " + st.session_state.game_state.name)
                st.warning("⏳ Waiting for opponent to join...")
            else:
                st.success("✅ Opponent joined!")
                if st.button("Start Game"):
                    st.session_state.game_state.started = True
                    st.session_state.page = "game_host"
                    lobby_host_container.empty()
                    st.rerun()
    time.sleep(PAGE_REFRESH_DELAY)
    st.rerun()