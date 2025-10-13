PIECE_TYPES = ['兵', '车', '马', '炮', '象', '士', '将']
PIECE_COLORS = ['r', 'b']

def opposite_color(color):
    return 'r' if color == 'b' else 'b'

class Move:
    def __init__(self, chess, target, is_imaginary=False, original_chess=None, define_original_chess=False):
        self.start = chess.position
        self.end = target
        self.chess = chess
        self.board = chess.board
        self.is_capture = bool(self.board.grid[target[0]][target[1]])
        self.is_imaginary = is_imaginary
        self.original_chess = original_chess
        self.define_original_chess = define_original_chess
        self.done = False

    def __str__(self):
        return f"{self.chess.type} from {self.start} to {self.end}" + (f" capturing {self.board.grid[self.end[0]][self.end[1]].type}" if self.is_capture else "")

    def run(self):
        self.captured = self.board.grid[self.end[0]][self.end[1]]
        self.board.grid[self.start[0]][self.start[1]] = None
        self.chess.position = self.end
        self.board.grid[self.end[0]][self.end[1]] = self.chess
        self.is_checkmate = self._check_checkmate()
        self.done = True

    def undo(self):
        self.board.grid[self.start[0]][self.start[1]] = self.original_chess if self.define_original_chess else self.chess
        self.chess.position = self.start
        self.board.grid[self.end[0]][self.end[1]] = self.captured
        self.done = False
    
    def _check_checkmate(self):
        color = self.chess.color
        opponent_king_pos = self.board.find_king(opposite_color(color))
        for move in self.chess.get_allowed_moves():
            if move.end == opponent_king_pos:
                return True

class Chess:
    def __init__(self, board, type, color, position):
        assert type in PIECE_TYPES, "Invalid piece type"
        assert color in PIECE_COLORS, "Invalid color"
        assert position[0] in range(10) and position[1] in range(9), "Invalid position"
        self.type = type
        self.color = color
        self.position = position
        self.board = board

    def __str__(self):
        return f"{self.type} {self.color} at {self.position}"

    def get_allowed_moves(self):
        allowed_moves = []
        all_moves = self._get_all_moves()
        for move in all_moves:
            target = self.board.grid[move[0]][move[1]]
            if not target:
                allowed_moves.append(Move(self, move))
            elif target.color != self.color:
                allowed_moves.append(Move(self, move))
        return allowed_moves

    def _get_all_moves(self):
        match self.type:
            case '兵':
                if self.color == 'r':
                    if self.position[0] > 4:
                        return [(self.position[0] - 1, self.position[1])]
                    else:
                        return [(self.position[0] - 1, self.position[1]),
                                (self.position[0], self.position[1] - 1),
                                (self.position[0], self.position[1] + 1)]
                else:
                    if self.position[0] < 5:
                        return [(self.position[0] + 1, self.position[1])]
                    else:
                        return [(self.position[0] + 1, self.position[1]),
                                (self.position[0], self.position[1] - 1),
                                (self.position[0], self.position[1] + 1)]
            case '车':
                moves = []
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                for d in directions:
                    x, y = self.position
                    while True:
                        x += d[0]
                        y += d[1]
                        if 0 <= x < 10 and 0 <= y < 9:
                            if not self.board.grid[x][y]:
                                moves.append((x, y))
                            elif self.board.grid[x][y].color != self.color:
                                moves.append((x, y))
                                break
                            else:
                                break
                        else:
                            break
                return moves
            case '炮':
                moves = []
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                for d in directions:
                    x, y = self.position
                    moveable = True
                    while True:
                        x += d[0]
                        y += d[1]
                        if 0 <= x < 10 and 0 <= y < 9:
                            if moveable:
                                if not self.board.grid[x][y]:
                                    moves.append((x, y))
                                else:
                                    moveable = False
                            else:
                                if self.board.grid[x][y]:
                                    if self.board.grid[x][y].color != self.color:
                                        moves.append((x, y))
                                    break
                        else:
                            break
                return moves
            case '马':
                moves = []
                if self.position[0] >= 2:
                    if not self.board.grid[self.position[0]-1][self.position[1]]:
                        if self.position[1] >= 1:
                            moves.append((self.position[0] - 2, self.position[1] - 1))
                        if self.position[1] < 8:
                            moves.append((self.position[0] - 2, self.position[1] + 1))
                if self.position[0] < 7:
                    if not self.board.grid[self.position[0]+1][self.position[1]]:
                        if self.position[1] >= 1:
                            moves.append((self.position[0] + 2, self.position[1] - 1))
                        if self.position[1] < 8:
                            moves.append((self.position[0] + 2, self.position[1] + 1))
                if self.position[1] >= 2:
                    if not self.board.grid[self.position[0]][self.position[1]-1]:
                        if self.position[0] >= 1:
                            moves.append((self.position[0] - 1, self.position[1] - 2))
                        if self.position[0] < 8:
                            moves.append((self.position[0] + 1, self.position[1] - 2))
                if self.position[1] < 7:
                    if not self.board.grid[self.position[0]][self.position[1]+1]:
                        if self.position[0] >= 1:
                            moves.append((self.position[0] - 1, self.position[1] + 2))
                        if self.position[0] < 8:
                            moves.append((self.position[0] + 1, self.position[1] + 2))
                return moves
            case '象':
                moves = []
                x, y = self.position
                if x - 2 >= 0 and y - 2 >= 0:
                    if not self.board.grid[x - 1][y - 1] and not self.board.grid[x - 2][y - 2]:
                        moves.append((x - 2, y - 2))
                if x - 2 >= 0 and y + 2 < 9:
                    if not self.board.grid[x - 1][y + 1] and not self.board.grid[x - 2][y + 2]:
                        moves.append((x - 2, y + 2))
                if x + 2 < 10 and y - 2 >= 0:
                    if not self.board.grid[x + 1][y - 1] and not self.board.grid[x + 2][y - 2]:
                        moves.append((x + 2, y - 2))
                if x + 2 < 10 and y + 2 < 9:
                    if not self.board.grid[x + 1][y + 1] and not self.board.grid[x + 2][y + 2]:
                        moves.append((x + 2, y + 2))
                return moves
            case '士':
                if self.color == 'r':
                    if self.position == (8, 4):
                        return [(9, 3), (9, 5), (7, 3), (7, 5)]
                    else:
                        return [(8, 4)]
                else:
                    if self.position == (1, 4):
                        return [(0, 3), (0, 5), (2, 3), (2, 5)]
                    else:
                        return [(1, 4)]
            case '将':
                moves = []
                if self.color == 'r':
                    if self.position[0] > 7:
                        moves.append((self.position[0] - 1, self.position[1]))
                    if self.position[0] < 9:
                        moves.append((self.position[0] + 1, self.position[1]))
                    if self.position[1] > 3:
                        moves.append((self.position[0], self.position[1] - 1))
                    if self.position[1] < 5:
                        moves.append((self.position[0], self.position[1] + 1))
                else:
                    if self.position[0] > 0:
                        moves.append((self.position[0] - 1, self.position[1]))
                    if self.position[0] < 2:
                        moves.append((self.position[0] + 1, self.position[1]))
                    if self.position[1] > 3:
                        moves.append((self.position[0], self.position[1] - 1))
                    if self.position[1] < 5:
                        moves.append((self.position[0], self.position[1] + 1))
                opponent_king = self.board.find_king(opposite_color(self.color))
                if self.position[1] == opponent_king[1]:
                    clear_path = True
                    step = 1 if self.position[0] < opponent_king[0] else -1
                    for x in range(self.position[0] + step, opponent_king[0], step):
                        if self.board.grid[x][self.position[1]]:
                            clear_path = False
                            break
                    if clear_path:
                        moves.append(opponent_king)
                return moves

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(9)] for _ in range(10)]
        self._setup_board()

    def _setup_board(self):
        self.grid[0][0] = Chess(self, '车', 'b', (0, 0))
        self.grid[0][1] = Chess(self, '马', 'b', (0, 1))
        self.grid[0][2] = Chess(self, '象', 'b', (0, 2))
        self.grid[0][3] = Chess(self, '士', 'b', (0, 3))
        self.grid[0][4] = Chess(self, '将', 'b', (0, 4))
        self.grid[0][5] = Chess(self, '士', 'b', (0, 5))
        self.grid[0][6] = Chess(self, '象', 'b', (0, 6))
        self.grid[0][7] = Chess(self, '马', 'b', (0, 7))
        self.grid[0][8] = Chess(self, '车', 'b', (0, 8))
        self.grid[2][1] = Chess(self, '炮', 'b', (2, 1))
        self.grid[2][7] = Chess(self, '炮', 'b', (2, 7))
        for i in range(0, 9, 2):
            self.grid[3][i] = Chess(self, '兵', 'b', (3, i))
        self.grid[9][0] = Chess(self, '车', 'r', (9, 0))
        self.grid[9][1] = Chess(self, '马', 'r', (9, 1))
        self.grid[9][2] = Chess(self, '象', 'r', (9, 2))
        self.grid[9][3] = Chess(self, '士', 'r', (9, 3))
        self.grid[9][4] = Chess(self, '将', 'r', (9, 4))
        self.grid[9][5] = Chess(self, '士', 'r', (9, 5))
        self.grid[9][6] = Chess(self, '象', 'r', (9, 6))
        self.grid[9][7] = Chess(self, '马', 'r', (9, 7))
        self.grid[9][8] = Chess(self, '车', 'r', (9, 8))
        self.grid[7][1] = Chess(self, '炮', 'r', (7, 1))
        self.grid[7][7] = Chess(self, '炮', 'r', (7, 7))
        for i in range(0, 9, 2):
            self.grid[6][i] = Chess(self, '兵', 'r', (6, i))

    def __str__(self):
        board_str = "〇 0 1 2 3 4 5 6 7 8\n"
        for i, row in enumerate(self.grid):
            board_str += str(i) + " "
            for piece in row:
                if piece:
                    if piece.color == 'r':
                        board_str += f"\033[91m{piece.type}\033[0m"  # Red for 'r'
                    else:
                        board_str += f"{piece.type}"
                else:
                    board_str += "〇"
            board_str += "\n"
        return board_str

    def copy(self):
        new_board = Board()
        for i in range(10):
            for j in range(9):
                piece = self.grid[i][j]
                new_board.grid[i][j] = Chess(new_board, piece.type, piece.color, piece.position) if piece else None
        return new_board

    def find_king(self, color):
        for i in range(10):
            for j in range(9):
                piece = self.grid[i][j]
                if piece and piece.type == '将' and piece.color == color:
                    return (i, j)
        raise ValueError("King not found")

    def get_all_moves(self, color):
        moves = []
        for row in self.grid:
            for piece in row:
                if piece:
                    if piece.color == color:
                        moves.extend(piece.get_allowed_moves())
        return moves
    
    def is_terminated(self, next_color):
        terminated = True
        for move in self.get_all_moves(next_color):
            move.run()
            next_board = move.board
            if not next_board.king_in_check(next_color):
                terminated = False
            move.undo()
        return terminated

    def king_in_check(self, color):
        king_pos = self.find_king(color)
        opponent_moves = self.get_all_moves(opposite_color(color))
        for move in opponent_moves:
            if move.end == king_pos:
                return True
        return False

if __name__ == "__main__":
    board = Board()
    color_turn = 'r'
    while True:
        if board.is_terminated(color_turn):
            print(f"Game over! {opposite_color(color_turn)} wins!")
            break

        print(board)
        print(f"{color_turn}'s turn")

        while True:
            x, y = map(int, input("Chess> ").split())
            if x not in range(10) or y not in range(9):
                print("Invalid position. Try again.")
                continue
            chess = board.grid[x][y]
            if not chess or chess.color != color_turn:
                print("Invalid chess piece. Try again.")
                continue
            else:
                break
        all_moves = chess.get_allowed_moves()
        done = False
        while not done:
            dx, dy = map(int, input("Move> ").split())
            for move in all_moves:
                if move.end == (x + dx, y + dy):
                    move.run()
                    if board.king_in_check(color_turn):
                        print("Move puts own king in check. Try again.")
                        move.undo()
                    else:
                        color_turn = opposite_color(color_turn)
                    done = True
                    break
            else:
                print("Invalid move. Try again.")
                continue