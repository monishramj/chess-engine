# chess-engine
A basic Python chess engine implementing a basic minimax algorithm with alpha-beta pruning for move evaluation and selection.

# Implementation
- Basic board
- Movement logic
- Minimax algorithm 

## TODO:
- Checks, checkmates, stalemates
- Special rules (promotion, en passant, castling)
- Positional evaluation
- GUI

# How to Run
The repository is in progress. To see it at work, try this sample code!!
```
from board import Board
import move as md

# initialize board
b = Board()
b.fen_to_board() # sets the board to a FEN position, you may input any string

# get legal moves for a piece
moves = md.available_moves(b, (6, 4))  # e2 pawn

# Find best move
score, (start, end) = md.minimax(b, depth=3, color=1)
new_board = md.move_piece(b, start, end)
```
