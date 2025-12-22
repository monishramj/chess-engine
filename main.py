from board import Board
import move as md



b = Board()
b.fen_to_board('rnbqkbnr/pppppppp/8/4N3/8/8/PPPPPPPP/RNBQKB1R w KQkq - 0 1')
print(b)
print(md.available_moves(b, (1,3)))

best, move = md.minimax(b, 2, b.color)
start, end = move
print(md.move_piece(b, start, end))

