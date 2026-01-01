from board import Board
import moves.move_tables as tb


b = Board()
b.fen_to_board('8/8/8/8/8/8/2p5/8 w - - 0 1')

center = b.pieces['BP']

print(b)
Board.print_bb(center)
print(center)
pawn_moves, pawn_atks = tb.compute_pawn_move(center, -1)
b.print_bb(pawn_moves)
b.print_bb(pawn_atks)

