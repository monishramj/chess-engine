from board import Board
import move as md



b = Board()
b.fen_to_board()
print(b)
print(md.available_moves(b, (3,4)))

best, move = md.minimax(b, 3, -1)
start, end = move
print(md.move_piece(b, start, end))

