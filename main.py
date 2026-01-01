from board import Board
import moves.move_tables as tb


b = Board()
b.fen_to_board('8/2K5/8/8/8/8/8/8 w - - 0 1')

center = b.pieces['WK']

print(b)
Board.print_bb(center)
print(center)
king_moves = tb.compute_tables(tb.compute_king_move)
print(b.print_bb(king_moves[8]))

