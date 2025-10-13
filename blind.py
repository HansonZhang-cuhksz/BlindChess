import communicate
import chess
from random import Random
import sys
import time   

if __name__ == "__main__":
    comm = communicate.Comm(len(sys.argv) > 1)

    # Wait for opponent
    print(comm.MY_IP, comm.MY_PORT)
    print("Waiting for opponent...")
    while True:
        try:
            comm.send_message(".")
            comm.receive_message()
            break
        except ConnectionResetError:
            time.sleep(0.5)
        except KeyboardInterrupt as e:
            exit()

    rand = Random().random()
    comm.send_message(str(rand))
    oppo_rand = float(comm.receive_message())
    if rand == oppo_rand:
        exit()
    color = 'r' if rand > oppo_rand else 'b'

    board = chess.Board()
    print(board)
    turn = 'r'
    print("You are playing as", "Red" if color == 'r' else "Black")

    while True:
        print(board)

        if board.is_terminated(turn):
            print(f"Game over! {chess.opposite_color(turn)} wins!")
            break

        if turn == color:
            print("Your turn, you are playing as", "Red" if color == 'r' else "Black")

            while True:
                try:
                    x, y, piece_type, tx, ty = input("Move (x y piece_type tx ty)> ").split()
                    x, y, tx, ty = int(x), int(y), int(tx), int(ty)
                except ValueError:
                    print("Invalid input. Try again.")
                    continue
                if x not in range(10) or y not in range(9) or tx not in range(10) or ty not in range(9):
                    print("Invalid position. Try again.")
                    continue
                if piece_type not in chess.PIECE_TYPES:
                    print("Invalid piece type. Try again.")
                    continue
                this_king = board.find_king(turn)
                opponent_king = board.find_king(chess.opposite_color(turn))
                if (x, y) == this_king or (tx, ty) == this_king or (x, y) == opponent_king or (tx, ty) == opponent_king:
                    if piece_type != '将':
                        print("You must move the king when moving to or from the king's position. Try again.")
                        continue
                
                piece = None
                is_scam = False
                is_imaginary = False
                original_chess = None
                if not board.grid[x][y]:
                    if piece_type == '将':
                        print("You cannot scam with a king. Try again.")
                        continue
                    piece = chess.Chess(board, piece_type, turn, (x, y))
                    is_scam = True
                    is_imaginary = True
                elif board.grid[x][y].color == turn and board.grid[x][y].type == piece_type:
                    piece = board.grid[x][y]
                    if (tx, ty) not in [move.end for move in piece.get_allowed_moves()]:
                        is_scam = True
                else:
                    if piece_type == '将':
                        print("You cannot scam with a king. Try again.")
                        continue
                    piece = chess.Chess(board, piece_type, turn, (x, y))
                    original_chess = board.grid[x][y]
                    is_scam = True
                    is_imaginary = True

                move = chess.Move(piece, (tx, ty), is_imaginary, original_chess, define_original_chess=True)
                move.run()
                if board.king_in_check(turn):
                    print("Move puts own king in check. Try again.")
                    move.undo()
                    continue
                comm.send_message(f"{x} {y} {piece_type} {tx} {ty} {1 if is_scam else 0}")
                print("Waiting for opponent's response...")
                ret = comm.receive_message()
                
                match ret:
                    case "accepted":
                        print("Move accepted")
                        turn = chess.opposite_color(turn)
                        break
                    case "caught":
                        print("Scam caught")
                        move.undo()
                        turn = chess.opposite_color(turn)
                        if board.king_in_check(color):
                            print("You are in check! You lose!")
                            exit()
                        break
                    case "false":
                        print("Opponent false argue")
                        if board.king_in_check(chess.opposite_color(color)):
                            print("Opponent is in check! You win!")
                            break
                        break

        else:
            print("Waiting for opponent's move...")
            x, y, piece_type, tx, ty, is_scam = comm.receive_message().split()
            x, y, tx, ty = int(x), int(y), int(tx), int(ty)
            is_scam = is_scam == "1"
            print(f"Opponent's move: {piece_type} from ({x}, {y}) to ({tx}, {ty})")
            argue = input("Argue? (y/n)")
            if argue.lower() == 'y':
                if is_scam:
                    print("Caught a scam")
                    comm.send_message("caught")
                    if board.king_in_check(chess.opposite_color(color)):
                        print("Opponent is in check! You win!")
                        break
                    turn = chess.opposite_color(turn)
                    continue
                else:
                    print("False argue")
                    comm.send_message("false")
                    if board.king_in_check(color):
                        print("You are in check! You lose!")
                        break
            else:
                comm.send_message("accepted")
                turn = chess.opposite_color(turn)
            
            piece = None
            if is_scam:
                piece = chess.Chess(board, piece_type, chess.opposite_color(turn), (x, y))
                board.grid[x][y] = piece
            else:
                piece = board.grid[x][y]
            move = chess.Move(piece, (tx, ty))
            move.run()