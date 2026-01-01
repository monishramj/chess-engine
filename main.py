from board import Board
import moves.move_tables as tb


b = Board()
b.fen_to_board('8/2N5/8/8/8/8/8/8 w - - 0 1')

center = b.pieces['WN']

print(b)
Board.print_bb(center)
print(center)
print(tb.compute_knight_tables())

