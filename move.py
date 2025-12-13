from board import Piece, Board

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
                moves.append((r-1, c))
                if r == 6:
                    moves.append((r-2, c))
                for dc in [-1, 1]:
                    move = (r-1, c+dc)
                    if 0 <= move[1] <= 7 and Board.is_black(board.get_piece(move)):
                        moves.append(move)
            else: 
                moves.append((r+1, c))
                if r == 1:
                    moves.append((r+2, c))
                for dc in [-1, 1]:
                    move = (r+1, c+dc)
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




# test code
b = Board()
pos = (5,4)
b.set_piece(pos, Piece.WB.value)
b.set_piece((1,6), Piece.BP.value)
b.set_piece((4,5), Piece.BP.value)
print(b)

moves = available_moves(b, tile=(6,5))
for move in moves:
    b.set_piece(tile=move, val=Piece.AM.value)

print(b)
