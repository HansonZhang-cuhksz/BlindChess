import streamlit as st
from streamlit_javascript import st_javascript
import time

import chess
from utils import *
from game_state import *

def exit_game():
    if st.session_state.is_host:
        del st.session_state.game_state
    else:
        unsubscribe_game(st.session_state.game_state.game_id)
    st.session_state.page = "home"
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def cancel_move():
    st.session_state.pos_from = None
    st.session_state.pos_to = None
    st.session_state.selected_piece = None
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

def handle_host_cmd():
    st.session_state.game_state.read_host_cmd = st.session_state.game_state.read_host()
    if st.session_state.game_state.read_host_cmd:
        st.session_state.game_state.read_host_cmd = st.session_state.game_state.read_host_cmd.split()
        match st.session_state.game_state.read_host_cmd[0]:
            case "move":
                assert st.session_state.status == "wait_move", f"Not waiting for move, status is {st.session_state.status}"
                _, x, y, piece_type, tx, ty = st.session_state.game_state.read_host_cmd
                x, y, tx, ty = 9 - int(x), 8 - int(y), 9 - int(tx), 8 - int(ty)
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
            if st.session_state.is_host:
                st.session_state.game_state.board = handle_argue(st.session_state.last_move, "y", st.session_state.opponent_is_scam, st.session_state.game_state.board, chess.opposite_color(st.session_state.color))
            else:
                st.session_state.game_state.write_host("argue y")
        case "move":
            if not (st.session_state.pos_from and st.session_state.pos_to and st.session_state.selected_piece):
                st.session_state.temp_info = ("error","Please select from, to positions and piece type.")
                st.rerun()
            x, y, piece_type, tx, ty = *st.session_state.pos_from, st.session_state.selected_piece, *st.session_state.pos_to
            if st.session_state.is_host:
                st.session_state.opponent_is_scam = handle_move(x, y, piece_type, tx, ty, st.session_state.game_state.board, st.session_state.color)
                st.session_state.game_state.write_guest("move " + " ".join(map(str, [x, y, piece_type, tx, ty])))
                st.session_state.last_move = (x, y, piece_type, tx, ty)
                st.session_state.status = "wait_argue"
            else:
                st.session_state.game_state.write_host("move " + " ".join(map(str, [9 - x, 8 - y, piece_type, 9 - tx, 8 - ty])))
                st.session_state.status = "wait_validation"
            cancel_move()

def handle_cancel():
    match st.session_state.status:
        case "argue":
            if st.session_state.is_host:
                st.session_state.game_state.board = handle_argue(st.session_state.last_move, "n", st.session_state.opponent_is_scam, st.session_state.game_state.board, chess.opposite_color(st.session_state.color))
            else:
                st.session_state.game_state.write_host("argue n")
        case "move":
            st.session_state.temp_info = ("info","Move cancelled")
            cancel_move()

st.set_page_config(
    page_title="Blind Chess",
    page_icon="♟️",
    layout="wide"
)
st.session_state.is_vertical = st_javascript("window.innerWidth") < 800
st.session_state.setdefault("page", "home")
match st.session_state.page:
    case "home":
        home_container = st.empty()
        with home_container.container():
            if st.session_state.is_vertical:
                col1 = col2 = col3 = st.container()
            else:
                col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.title("♟️ Blind Chess")
                if st.button("New Game"):
                    st.session_state.page = "new_game"
                    home_container.empty()
                    st.rerun()
                if st.button("Join Game"):
                    st.session_state.page = "join_game"
                    home_container.empty()
                    st.rerun()
    case "new_game":
        new_game_container = st.empty()
        with new_game_container.container():
            if st.session_state.is_vertical:
                col1 = col2 = col3 = st.container()
            else:
                col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.subheader("Create a New Game")
                password = st.text_input("Password (Optional):", type="password")
                first_selection = st.selectbox("First:", ["Random", "Me", "Opponent"])
                if st.button("Create Game"):
                    game_id = get_random_id(games.keys())
                    st.session_state.game_state = GameState(password, game_id, first_selection)
                    st.session_state.is_host = True
                    st.session_state.page = "lobby_host"
                    new_game_container.empty()
                    st.rerun()
                if st.button("Back to Home"):
                    st.session_state.page = "home"
                    new_game_container.empty()
                    st.rerun()
    case "join_game":
        join_game_container = st.empty()
        with join_game_container.container():
            if st.session_state.is_vertical:
                col1 = col2 = col3 = st.container()
            else:
                col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.subheader("Join an Existing Game")
                game_id = st.text_input("Game ID:")
                password = st.text_input("Password (Optional):", type="password")
                if st.button("Join Game"):
                    if not game_id.isdigit():
                        st.error("Game ID must be an integer.")
                        st.stop()
                    game_id = int(game_id)
                    try:
                        st.session_state.game_state = subscribe_game(game_id, password)
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
                if st.button("Back to Home"):
                    st.session_state.page = "home"
                    join_game_container.empty()
                    st.rerun()
    case "lobby_host":
        lobby_host_container = st.empty()
        with lobby_host_container.container():
            if st.session_state.is_vertical:
                col1 = col2 = col3 = st.container()
            else:
                col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Back to Home"):
                    exit_game()
                if not st.session_state.game_state.guest_online:
                    st.info("Game ID: " + str(st.session_state.game_state.game_id))
                    st.warning("⏳ Waiting for opponent to join...")
                else:
                    st.success("✅ Opponent joined!")
                    if st.button("Start Game"):
                        st.session_state.game_state.started = True
                        st.session_state.page = "game"
                        lobby_host_container.empty()
                        st.rerun()
        time.sleep(PAGE_REFRESH_DELAY)
        st.rerun()
    case "lobby_guest":
        lobby_guest_container = st.empty()
        with lobby_guest_container.container():
            if st.session_state.is_vertical:
                col1 = col2 = col3 = st.container()
            else:
                col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("Back to Home"):
                    exit_game()
                if st.session_state.game_state.exited:
                    st.error("Host has closed the game. Returning to home page...")
                    time.sleep(SLOW_DELAY)
                    exit_game()
                if not st.session_state.game_state.started:
                    st.info("⏳ Waiting for host to start the game...")
                    time.sleep(PAGE_REFRESH_DELAY)
                    st.rerun()
        st.session_state.page = "game"
        lobby_guest_container.empty()
        st.rerun()
    case "game":
        match st.session_state.game_state.first:
            case "Host":
                st.session_state.color = 'r' if st.session_state.is_host else 'b'
            case "Guest":
                st.session_state.color = 'b' if st.session_state.is_host else 'r'
        st.session_state.setdefault("status", "move" if st.session_state.color == 'r' else "wait_move")
        st.session_state.setdefault("selected_piece", None)
        st.session_state.setdefault("info", ("info", ""))
        st.session_state.setdefault("last_info", ("info", ""))
        st.session_state.setdefault("temp_info", ("info", ""))
        match st.session_state.status:
            case "wait_move":
                st.session_state.info = ("info","Waiting for opponent's move...")
            case "wait_argue":
                st.session_state.info = ("info","Waiting for opponent's argue...")
            case "move":
                st.session_state.info = ("info","Your turn to move")
        if st.session_state.is_vertical:
            col1 = col2 = col3 = st.container()
        else:
            col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Back to Home"):
                exit_game()
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
        with col2:
            st.session_state.setdefault("pos_from", None)
            st.session_state.setdefault("pos_to", None)
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
                        if st.button(label, key=f"{row}_{col_idx}"):
                            if st.session_state.status == "move":
                                if not st.session_state.pos_from:
                                    st.session_state.pos_from = (row, col_idx - 1)
                                    st.rerun()
                                elif not st.session_state.pos_to:
                                    st.session_state.pos_to = (row, col_idx - 1)
                                    st.rerun()
        with col3:
            for piece_type in chess.PIECE_TYPES:
                if st.button(piece_type):
                    if st.session_state.status == "move":
                        st.session_state.selected_piece = piece_type
            if st.button("Confirm"):
                handle_confirm()
            if st.button("Cancel"):
                handle_cancel()
            if st.session_state.selected_piece:
                st.write(st.session_state.selected_piece)
        if st.session_state.game_state.game_exited():
            st.error("Opponent has left the game. Returning to home page...")
            time.sleep(SLOW_DELAY)
            exit_game()
        if st.session_state.is_host:
            handle_guest_cmd()
        else:
            handle_host_cmd()
        time.sleep(PAGE_REFRESH_DELAY)
        st.rerun()