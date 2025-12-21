from board import Board, Piece
import move as md



b = Board()
b.fen_to_board()
print(b)

# pos = (5,4)
# b.set_piece(pos, Piece.WP.value)
# b.set_piece((1,6), Piece.BP.value)
# b.set_piece((2,5), Piece.WR.value)
# print(b)

# md.all_moves(b, 1)
# print(md.evaluate(b))
