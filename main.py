from board import Board, Piece
import move as md



b = Board()
b.fen_to_board('r1bqkb1r/ppp1pppp/2n2n2/3p4/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 1')
print(b)
print(md.available_moves(b, (4,1)))

best, move = md.minimax(b, 1, b.color)
start, end = move
print(md.move_piece(b, start, end))

