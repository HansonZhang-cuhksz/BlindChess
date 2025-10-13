import tkinter as tk
from tkinter import messagebox
from chess import Board, opposite_color

CELL_SIZE = 60
ROWS, COLS = 10, 9

class XiangqiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BlindChess GUI")

        self.board = Board()
        self.turn = 'r'
        self.selected = None  # (row, col)
        self.allowed_moves = []  # list of Move objects for selected piece
        self.game_over = False

        self.canvas = tk.Canvas(
            root,
            width=COLS * CELL_SIZE,
            height=ROWS * CELL_SIZE,
            bg="#f2e8c9"  # light board color
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.status = tk.Label(root, text=f"{self.turn}'s turn")
        self.status.pack(pady=6)

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_highlights()
        self.draw_pieces()

    def draw_grid(self):
        # Draw cell borders
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1, x2, y2 = self.cell_bbox(r, c)
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#555", width=1)

    def draw_pieces(self):
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board.grid[r][c]
                if piece:
                    x, y = self.cell_center(r, c)
                    fill = "red" if piece.color == 'r' else "black"
                    self.canvas.create_text(
                        x, y, text=piece.type, fill=fill, font=("", 24, "bold")
                    )

    def draw_highlights(self):
        # Selected square
        if self.selected:
            r, c = self.selected
            x1, y1, x2, y2 = self.cell_bbox(r, c)
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#f39c12", width=3)

        # Allowed target dots
        for mv in self.allowed_moves:
            r, c = mv.end
            cx, cy = self.cell_center(r, c)
            rr = CELL_SIZE // 8
            color = "#2ecc71"  # green hint
            self.canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr, fill=color, outline=color)

    def on_click(self, event):
        if self.game_over:
            return

        r = event.y // CELL_SIZE
        c = event.x // CELL_SIZE
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return

        # No selection yet: try to select a piece of the side to move
        if self.selected is None:
            piece = self.board.grid[r][c]
            if piece and piece.color == self.turn:
                self.selected = (r, c)
                self.allowed_moves = piece.get_allowed_moves()
                self.draw()
            # else ignore clicks on empty/opponent squares
            return

        # Already selected: process second click
        sel_r, sel_c = self.selected
        selected_piece = self.board.grid[sel_r][sel_c]

        # Clicking own piece switches selection
        clicked_piece = self.board.grid[r][c]
        if clicked_piece and clicked_piece.color == self.turn and (r, c) != self.selected:
            self.selected = (r, c)
            self.allowed_moves = clicked_piece.get_allowed_moves()
            self.draw()
            return

        # Attempt to move to clicked cell if it's in allowed moves
        chosen = next((m for m in self.allowed_moves if m.end == (r, c)), None)
        if not chosen:
            # Keep selection; show info
            self.status.config(text="Invalid move. Try again.")
            return

        # Try the move; revert if puts own king in check
        chosen.run()
        if self.board.king_in_check(self.turn):
            chosen.undo()
            self.status.config(text="Move puts own king in check. Try again.")
            self.draw()
            return

        # Move accepted: switch turn, clear selection
        self.turn = opposite_color(self.turn)
        self.selected = None
        self.allowed_moves = []
        self.status.config(text=f"{self.turn}'s turn")
        self.draw()

        # Check termination for the side to move (same as CLI logic)
        if self.board.is_terminated(self.turn):
            messagebox.showinfo("Game Over", f"Game over! {opposite_color(self.turn)} wins!")
            self.game_over = True

    def cell_bbox(self, r, c):
        x1 = c * CELL_SIZE
        y1 = r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        return x1, y1, x2, y2

    def cell_center(self, r, c):
        x1, y1, x2, y2 = self.cell_bbox(r, c)
        return (x1 + x2) // 2, (y1 + y2) // 2


if __name__ == "__main__":
    root = tk.Tk()
    app = XiangqiGUI(root)
    root.mainloop()