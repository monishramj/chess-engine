from board import Board
import moves.move_tables as tb
import moves.move as m


b = Board()
b.fen_to_board('8/q3np2/P1P4r/Pk2N1R1/3rPp2/8/3Q4/3K1b2 w - - 0 1')


print(b)
unused, rook = m.pop_lssb(b.pieces['WR'])
Board.print_bb(m.rook_hq(bb= rook, occ= b.all_occ()) & ~b.same_occ())

