from board import Piece, Board
import move as md
import numpy as np

def evaluate(board):
    base = {
        Piece.WP.value: 1,   Piece.BP.value: -1,
        Piece.WN.value: 3,   Piece.BN.value: -3,
        Piece.WB.value: 3,   Piece.BB.value: -3,
        Piece.WR.value: 5,   Piece.BR.value: -5,
        Piece.WQ.value: 9,   Piece.BQ.value: -9,
        Piece.WK.value: 100, Piece.BK.value: -100,
    }
    
    score = 0
    for r in range(8):
        for c in range(8):
            piece = board.get_piece((r, c))
            score += base.get(piece, 0)
    
    return score
                
def minimax(board, depth, color, a=-np.inf, b=np.inf) :
    if depth == 0:
        return evaluate(board), None
    
    moves = md.legal_all_moves(board, color)
    best_move = None
    best = -np.inf if color == 1 else np.inf

    for start, end in moves:
        new_board = md.move_piece(board, start, end)
        score, unused = minimax(new_board, depth - 1, -color, a, b)

        if color == 1: 
            if score > best:
                best = score
                best_move = (start, end)
            a = max(a, best)
            if b <= a :
                break
        else: 
            if score < best:
                best = score
                best_move = (start, end)
            b = min(b, best)
            if b <= a:
                break
    return best, best_move
        