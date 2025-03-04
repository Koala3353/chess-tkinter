import tkinter as tk
from PIL import Image, ImageTk
import os
import chess

class ChessBoard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess Game")
        self.geometry("670x660")
        self.board = []
        self.selected_piece = None
        self.current_turn = 'w'  # White starts first
        self.chess_board = chess.Board()
        self.create_board()
        self.update_board()

    def create_board(self):
        colors = ["white", "gray"]
        for row in range(8):
            row_list = []
            for col in range(8):
                color = colors[(row + col) % 2]
                frame = tk.Frame(self, width=80, height=80, bg=color)
                frame.grid(row=row, column=col)
                frame.bind("<Button-1>", lambda event, r=row, c=col: self.on_click(r, c))
                row_list.append(frame)
            self.board.append(row_list)

    def update_board(self):
        piece_symbols = {
            'r': 'bRook', 'n': 'bKnight', 'b': 'bBishop', 'q': 'bQueen', 'k': 'bKing', 'p': 'bPawn',
            'R': 'wRook', 'N': 'wKnight', 'B': 'wBishop', 'Q': 'wQueen', 'K': 'wKing', 'P': 'wPawn'
        }
        for row in range(8):
            for col in range(8):
                piece = self.chess_board.piece_at(chess.square(col, 7 - row))
                if piece:
                    piece_symbol = piece_symbols[piece.symbol()]
                    img_path = os.path.join('mats', f'{piece_symbol}.png')
                    img = Image.open(img_path)
                    img = img.resize((80, 80), Image.LANCZOS)
                    img = ImageTk.PhotoImage(img)
                    if hasattr(self.board[row][col], 'piece_label'):
                        self.board[row][col].piece_label.config(image=img)
                        self.board[row][col].piece_label.image = img  # Keep a reference to avoid garbage collection
                    else:
                        label = tk.Label(self.board[row][col], image=img, bg=self.board[row][col].cget('bg'))
                        label.image = img  # Keep a reference to avoid garbage collection
                        label.grid(row=row, column=col)
                        label.bind("<Button-1>", lambda event, r=row, c=col: self.on_click(r, c))
                        self.board[row][col].piece_label = label
                else:
                    if hasattr(self.board[row][col], 'piece_label'):
                        self.board[row][col].piece_label.destroy()
                        del self.board[row][col].piece_label

    def on_click(self, row, col):
        print(f"Clicked on: ({row}, {col})")
        if self.selected_piece:
            self.move_piece(row, col)
        else:
            self.select_piece(row, col)

    def select_piece(self, row, col):
        piece = self.chess_board.piece_at(chess.square(col, 7 - row))
        if piece and piece.color == (self.current_turn == 'w'):
            from_square = chess.square(col, 7 - row)
            legal_moves = [move for move in self.chess_board.legal_moves if move.from_square == from_square]
            if legal_moves:
                if self.selected_piece:
                    old_row, old_col = self.selected_piece
                    self.board[old_row][old_col].config(bg=["white", "gray"][(old_row + old_col) % 2])
                self.selected_piece = (row, col)
                self.board[row][col].config(bg="yellow")
                print(f"Selected piece at: ({row}, {col})")
            else:
                print(f"No legal moves for piece at: ({row}, {col})")

    def move_piece(self, row, col):
        old_row, old_col = self.selected_piece
        if (old_row, old_col) == (row, col):
            self.selected_piece = None
            self.board[old_row][old_col].config(bg=["white", "gray"][(old_row + old_col) % 2])
            return

        move = chess.Move.from_uci(f"{chr(old_col + 97)}{8 - old_row}{chr(col + 97)}{8 - row}")
        if move in self.chess_board.legal_moves:
            self.chess_board.push(move)
            self.update_board()
            self.board[old_row][old_col].config(bg=["white", "gray"][(old_row + old_col) % 2])
            self.selected_piece = None

            # Check for checkmate
            if self.chess_board.is_checkmate():
                print("Checkmate!")
                self.show_checkmate_message()
                return

            # Switch turns
            self.current_turn = 'b' if self.current_turn == 'w' else 'w'
            print(f"Moved piece to: ({row}, {col})")
            print(self.chess_board)
        else:
            self.selected_piece = None
            self.board[old_row][old_col].config(bg=["white", "gray"][(old_row + old_col) % 2])
            print(f"Invalid move to: ({row}, {col})")
            self.vibrate_window()

        self.update_idletasks()  # Refresh the GUI

    def vibrate_window(self):
        x, y = self.winfo_x(), self.winfo_y()
        for _ in range(10):
            self.geometry(f"+{x + 10}+{y}")
            self.update()
            self.after(50)
            self.geometry(f"+{x - 10}+{y}")
            self.update()
            self.after(50)
        self.geometry(f"+{x}+{y}")

    def show_checkmate_message(self):
        winner = "White" if self.current_turn == 'b' else "Black"
        message = f"Checkmate! {winner} wins!"
        tk.messagebox.showinfo("Game Over", message)

if __name__ == "__main__":
    app = ChessBoard()
    app.mainloop()