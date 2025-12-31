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
    is_white = Board.is_white(piece)
    r, c = tile
    moves = []

    offsets = []
    extend = True
    match abs(piece):
        case Piece.WP.value:   
            dr = -1 if is_white else 1
            start_row = 6 if is_white else 1

            step = (r+dr, c)
            dstep = (r+(dr*2), c)

            if in_bounds(step) and is_empty(board, step):
                moves.append(step)
                if r == start_row and in_bounds(dstep) and is_empty(board, dstep):
                    moves.append(dstep)

            for dc in [-1, 1]:
                    move = (r+dr, c+dc)
                    if in_bounds(move) and is_enemy(board, move, is_white):
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
                if not valid_move(board, (r_curr, c_curr), is_white):
                    break
                moves.append((r_curr, c_curr))
                # stop if capture
                if board.get_piece((r_curr, c_curr)) != Piece.EMPTY.value:
                    break
        else :
            moves.append((r + dr, c + dc))

    # double checking
    valid_moves = [move for move in moves if valid_move(board, move, is_white)]
    return valid_moves
             
def valid_move(board, tile, isWhite=None):
    if not in_bounds(tile):
        return False
    if is_empty(board, tile):
        return True
    if isWhite is not None:
        target = board.get_piece(tile)
        return (Board.is_white(target) != isWhite) # bugged
    return False

def in_bounds(tile):
    r, c = tile
    return 0 <= r <= 7 and 0 <= c <= 7

def is_empty(board, tile):
    return board.get_piece(tile) == Piece.EMPTY.value

def is_enemy(board, tile, isWhite):
    piece = board.get_piece(tile)
    return Board.is_white(piece) != isWhite

def in_check(board, color=1) : # NEED TO DO IT FROM KING'S PERSPECTIVE
    king_pos = None
    king_val = Piece.WK.value if color == 1 else Piece.BK.value

    for i in range(64) :
            tile = (i//8, i%8)
            piece = board.get_piece(tile)
            if piece == king_val:
                king_pos = tile
                break
    if king_pos is None:
        raise ValueError('Invalid board: king is missing')
    
    for i in range(64):
        offsets = [(-1, -1), (-1, 0), (-1, 1),
                       ( 0, -1),          ( 0, 1),
                       ( 1, -1), ( 1, 0), ( 1, 1)]
        
    return False

def basic_all_moves(board, color=1) : # 1 = white, -1 = black
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

def legal_all_moves(board, color=1) :
    moves = basic_all_moves(board, color)
    output = []
    for move in moves:
        if in_check(board, color):
            continue
        output.append(move)

    return output

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
    
    moves = legal_all_moves(board, color)
    best_move = None
    best = -np.inf if color == 1 else np.inf

    for start, end in moves:
        new_board = move_piece(board, start, end)
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
        
