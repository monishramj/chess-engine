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

#--------------------------#
#   SINGULAR PIECE MOVES   #
#--------------------------#

def knight_lookup(bb, same_occ) :
    return tb.KNIGHT_MOVES[bb] & tb.bitmask(~same_occ)

def king_lookup(bb, same_occ) :
    return tb.KING_MOVES[bb] & tb.bitmask(~same_occ)

def pawn_lookup(bb, color, all_occ, opp_occ, ep=0) :
    moves = tb.PAWN_WHITE_MOVES[bb] if color > 0 else tb.PAWN_BLACK_MOVES[bb]
    attacks = tb.PAWN_WHITE_ATTACKS[bb] if color > 0 else tb.PAWN_BLACK_ATTACKS[bb]
    step = tb.north_one(bb) if color > 0 else tb.south_one(bb)

    if step & all_occ: # might need refining, leave as if else for now ig
        moves = 0
    else:
        moves &= tb.bitmask(~all_occ)

    attacks &= opp_occ | ep

    return moves | attacks # TODO: promotion!

def hq(bb, occ, mask) : # hyperbola quintessence
    mask_occ = mask & occ
    reverse = reverse_bb(bb) << 1

    left = mask_occ - (bb << 1) # o ^ o-2r
    right = reverse_bb(reverse_bb(mask_occ) - reverse)
    moves = (left ^ right) & mask

    return moves

def rook_hq(bb, all_occ) :
    sq = lssb_sq(bb)

    r = tb.ROWS[sq // 8]
    c = tb.COLUMNS[sq % 8]

    return hq(bb, all_occ, r) | hq(bb, all_occ, c)

def bishop_hq(bb, all_occ) :
    diag = tb.DIAGONALS[bb]
    anti_diag = tb.ANTI_DIAGONALS[bb]

    return hq(bb, all_occ, diag) | hq(bb, all_occ, anti_diag)

def queen_hq(bb, all_occ):
    return rook_hq(bb, all_occ) | bishop_hq(bb, all_occ)

#---------------------#
#     PSEUDO MOVES    #
#---------------------#

def step_pseudo_moves(board: b, piece: str, lookup) :
    if not (piece == 'N' or piece == 'K'):
        raise ValueError('Wrong piece, only use N or K for step_pseudo_moves()')
    
    same_occ = board.same_occ()
    bb = board.same_piece(piece)
    moves = []

    while bb:
        bb, least = pop_lssb(bb)
        start = lssb_sq(least)
        possible_moves = lookup(least, same_occ)
        moves.extend(moves_to_tuples(possible_moves, start))

    return moves

def sliding_pseudo_moves(board: b, piece: str, hq) :
    if not (piece == 'B' or piece == 'R' or piece == 'Q'):
        raise ValueError('Wrong piece, only use B, R, or Q for sliding_pseudo_moves()')
    
    same_occ = board.same_occ()
    all_occ = board.all_occ()
    bb = board.same_piece(piece)
    moves = []

    while bb:
        bb, least = pop_lssb(bb)
        start = lssb_sq(least)
        possible_moves = hq(least, all_occ) & tb.bitmask(~same_occ)
        moves.extend(moves_to_tuples(possible_moves, start))

    return moves

def pawn_pseudo_moves(board: b) :
    bb = board.same_piece('P')
    color = board.color
    opp_occ = board.opp_occ()
    all_occ = board.all_occ()
    ep = board.ep_sq
    moves = []

    while bb:
        bb, least = pop_lssb(bb)
        start = lssb_sq(least)
        possible_moves = pawn_lookup(least, color, all_occ, opp_occ, ep)
        moves.extend(moves_to_tuples(possible_moves, start))

    return moves

#-----------------#
#     LEGALITY    #
#-----------------#

def in_check(board: b) -> bool :
    bb = board.same_piece('K')
    same_occ = board.same_occ()
    all_occ = board.all_occ()
    
    if knight_lookup(bb, same_occ) & board.opp_piece('N') :
        return True
    
    if king_lookup(bb, same_occ) & board.opp_piece('K') :
        return True
    
    if rook_hq(bb, all_occ) & (board.opp_piece('R') | board.opp_piece('Q')) :
        return True
    
    if bishop_hq(bb, all_occ) & (board.opp_piece('B') | board.opp_piece('Q')) :
        return True
    
    king_pawn_attacks = tb.PAWN_WHITE_ATTACKS[bb] if board.color > 0 else tb.PAWN_BLACK_ATTACKS[bb] 
    # leave this at the end, so less computation if others True
    if (king_pawn_attacks) & board.opp_piece('P') :
        return True
    
    return False
