from board import Board
import moves.move_tables as tb
import moves.move as m


b = Board()
b.fen_to_board('8/8/4p3/8/8/8/2p5/8 w - - 0 1')

center = b.pieces['BP']

print(b)
Board.print_bb(center)

print(m.lssb_sq(center))

