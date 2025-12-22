from board import Piece, Board
import numpy as np

def move_piece(board, start=(0, 0), end=(0, 0)) :
    new_board = Board()
    new_board.board = board.board.copy()

    piece = new_board.get_piece(start)
    new_board.set_piece(tile=end, val=piece)
    new_board.set_piece(tile=start, val=Piece.EMPTY.value)

    return new_board

def available_moves(board, tile=(0,0)) :
    piece = board.get_piece(tile)
    r, c = tile
    moves = []

    offsets = []
    extend = True
    match abs(piece):
        case Piece.WP.value:           
            if Board.is_white(piece):
                dr = -1
            else: 
                dr = 1
            step = (r+dr, c)
            dstep = (r+(dr*2), c)

            if valid_move(board, tile=step, isWhite=True) and board.get_piece(step) == Piece.EMPTY.value:
                    moves.append(step)
            if r == 1 and valid_move(board, tile=dstep, isWhite=True) and board.get_piece(dstep) == Piece.EMPTY.value and board.get_piece(step) == Piece.EMPTY.value:
                moves.append(dstep)

            for dc in [-1, 1]:
                    move = (r+dr, c+dc)
                    if 0 <= move[1] <= 7 and Board.is_white(board.get_piece(move)):
                        moves.append(move)


        case Piece.WK.value :
            offsets = [(-1, -1), (-1, 0), (-1, 1),
                       ( 0, -1),          ( 0, 1),
                       ( 1, -1), ( 1, 0), ( 1, 1)]

            extend = False

        case Piece.WN.value :
            offsets = [
                        (-2, -1), (-2,  1),
                        (-1, -2), (-1,  2),
                        ( 1, -2), ( 1,  2),
                        ( 2, -1), ( 2,  1)
                        ]
            extend = False


        case Piece.WQ.value :
            offsets = [(-1, -1), (-1, 0), (-1, 1),
                       ( 0, -1),          ( 0, 1),
                       ( 1, -1), ( 1, 0), ( 1, 1)]

        case Piece.WB.value :
            offsets = [(-1, -1),(-1, 1),            
                       ( 1, -1),( 1, 1)]


        case Piece.WR.value :
            offsets = [(-1, 0), ( 0, -1),
                        ( 0, 1), ( 1, 0)]
        
    for dr, dc in offsets:
        if extend:
            r_curr, c_curr = r, c
            while True:
                r_curr += dr
                c_curr += dc
                if not valid_move(board, (r_curr, c_curr), isWhite=Board.is_white(piece)):
                    break
                moves.append((r_curr, c_curr))
                # stop if capture
                if board.get_piece((r_curr, c_curr)) != Piece.EMPTY.value:
                    break
        else :
            moves.append((r + dr, c + dc))

    # js double checking
    valid_moves = [move for move in moves if valid_move(board, move, isWhite=Board.is_white(piece))]
    return valid_moves
             
def valid_move(board, tile, isWhite=None):
    r, c = tile
    if not (0 <= r <= 7 and 0 <= c <= 7):
        return False
    target = board.get_piece(tile)
    if target == Piece.EMPTY.value:
        return True
    if isWhite is not None:
        return (Board.is_white(target) != isWhite) # bugged
    return False

def all_moves(board, color=1) : # 1 = white, -1 = black
    output = []
    for i in range(64) :
            tile = (i//8, i%8)
            if board.get_piece(tile) * color > 0 :
                moves = available_moves(board, tile)
                for move in moves :
                    output.append((tile, move))
            else :
                continue

    return output

def evaluate(board):
    basic_scores = {
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
            score += basic_scores.get(piece, 0)
    
    return score
                
def minimax(board, depth, color) :
    if depth == 0:
        return evaluate(board), None
    
    moves = all_moves(board, color)
    best_move = None
    best = -np.inf if color == 1 else np.inf

    for start, end in moves:
        new_board = move_piece(board, start, end)
        score, unused = minimax(new_board, depth - 1, -color)

        if color == 1: 
            if score > best:
                best = score
                best_move = (start, end)
        else: 
            if score < best:
                best = score
                best_move = (start, end)
                
    return best, best_move
        
