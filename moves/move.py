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

def reverse_bb(bb) : 
    bb = ((bb & 0x5555555555555555) << 1) | ((bb >> 1) & 0x5555555555555555)
    bb = ((bb & 0x3333333333333333) << 2) | ((bb >> 2) & 0x3333333333333333)
    bb = ((bb & 0x0F0F0F0F0F0F0F0F) << 4) | ((bb >> 4) & 0x0F0F0F0F0F0F0F0F)
    bb = ((bb & 0x00FF00FF00FF00FF) << 8) | ((bb >> 8) & 0x00FF00FF00FF00FF)
    bb = ((bb & 0x0000FFFF0000FFFF) << 16) | ((bb >> 16) & 0x0000FFFF0000FFFF)
    bb = (bb << 32) | (bb >> 32)

    return tb.bitmask(bb)

#----------------#
#     LOOKUPS    #
#----------------#

def knight_lookup(bb, same_occ) :
    return tb.KNIGHT_MOVES[bb] & ~same_occ

def king_lookup(bb, same_occ) :
    return tb.KING_MOVES[bb] & ~same_occ

def pawn_lookup(bb, color, same_occ, opp_occ) : # TODO: implement ep
    moves = tb.PAWN_WHITE_MOVES[bb] if color > 0 else tb.PAWN_BLACK_MOVES[bb]
    attacks = tb.PAWN_WHITE_ATTACKS[bb] if color > 0 else tb.PAWN_BLACK_ATTACKS[bb]

    return (moves & ~(same_occ | opp_occ)) | (attacks & opp_occ) # issue, double pawn move at beginning can be done if piece in middle

def hq(bb, occ, mask) : # hyperbola quintessence
    mask_occ = mask & occ
    reverse = reverse_bb(bb) << 1

    left = mask_occ - (bb << 1) # o ^ o-2r
    right = reverse_bb(reverse_bb(mask_occ) - reverse)
    moves = (left ^ right) & mask

    return moves

def rook_hq(bb, occ) :
    sq = lssb_sq(bb)

    r = tb.ROWS[sq // 8]
    c = tb.COLUMNS[sq % 8]

    return hq(bb, occ, r) | hq(bb, occ, c)

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

def rooks_pseudo_moves(board: b) :
    same_occ = board.same_occ()
    all_occ = board.all_occ()
    bb = board.pieces['WR'] if board.color > 0 else board.pieces['BR']
    moves = []

    while bb:
        bb, least = pop_lssb(bb)
        start = lssb_sq(least)
        possible_moves = rook_hq(least, all_occ) & ~ same_occ
        moves.extend(moves_to_tuples(possible_moves, start))

    return moves