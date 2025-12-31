from board import Board


b = Board()
b.fen_to_board()
print(b)
print(bin(b.pieces['WP']))

