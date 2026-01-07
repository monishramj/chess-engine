from board import Board as b
import moves.move_tables as tb

#------------------------#
#     SETUP & HELPERS    #
#------------------------#

def pop_lssb(bb) -> tuple[int, int]: 
    if bb == 0:
        return 0, 0 
    return bb & (bb-1), bb & -bb # first is bb w/o lssb, second is bb w/ lssb
    
def lssb_sq(lssb) : # lssb as least sig set bit, so lowest 1 in bb?
    return lssb.bit_length() - 1

def moves_to_tuples(moves, start) :
    output = []
    while moves:
        moves, move = pop_lssb(moves)
        end = lssb_sq(move)
        output.append((start, end))

    return output

#----------------#
#     LOOKUPS    #
#----------------#

def knight_lookup(bb, same_occ) :
    return tb.KNIGHT_MOVES[bb] & ~same_occ

def king_lookup(bb, same_occ) :
    return tb.KING_MOVES[bb] & ~same_occ

# def bishop_lookup(bb, same_occ) :
#     return tb.BISHOP_MOVES[bb] & ~same_occ

# def rook_lookup(bb, same_occ) :
#     return tb.ROOK_MOVES[bb] & ~same_occ

# def queen_lookup(bb, same_occ) :
#     return tb.QUEEN_MOVES[bb] & ~same_occ

def pawn_lookup(bb, color, same_occ, opp_occ) : # TODO: implement ep
    moves = tb.PAWN_WHITE_MOVES[bb] if color > 0 else tb.PAWN_BLACK_MOVES[bb]
    attacks = tb.PAWN_WHITE_ATTACKS[bb] if color > 0 else tb.PAWN_BLACK_ATTACKS[bb]

    return (moves & ~(same_occ | opp_occ)) | (attacks & opp_occ) # issue, double pawn move at beginning can be done if piece in middle


#--------------#
#     MOVES    #
#--------------#

def knights_pseudo_moves(board: b) :
    same_occ = board.same_occ()
    bb = board.pieces['WN'] if board.color > 0 else board.pieces['BN']
    moves = []

    while bb:
        bb, least = pop_lssb(bb)
        start = lssb_sq(least)
        possible_moves = knight_lookup(least, same_occ)
        moves.extend(moves_to_tuples(possible_moves, start))

    return moves

def king_pseudo_moves(board: b) :
    same_occ = board.same_occ()
    bb = board.pieces['WK'] if board.color > 0 else board.pieces['BK']
    moves = []

    while bb:
        bb, least = pop_lssb(bb)
        start = lssb_sq(least)
        possible_moves = king_lookup(least, same_occ)
        moves.extend(moves_to_tuples(possible_moves, start))

    return moves
