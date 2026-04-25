from engine.board import Board
from engine.moves import move_tables as tb
from engine.moves import movegen as m


b = Board()
b.fen_to_board('8/q3np2/P1P4r/Pk2N1R1/3rPp2/8/3Q4/3K1b2 w - - 0 1')


print(b)
bishop = m.lssb(b.pieces['BQ'])
Board.print_bb(m.queen_attacks(bb=bishop, occ=b.all_occ()) & ~b.black_occ())
