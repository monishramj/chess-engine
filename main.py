from board import Board
import move as md



b = Board()
b.fen_to_board('rnbqk1nr/pppppppp/8/4b3/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1')
print(b)
print(md.available_moves(b, (3,4)))
md.in_check(b, 1)

# best, move = md.minimax(b, 3, -1)
# start, end = move
# print(md.move_piece(b, start, end))

