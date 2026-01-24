from board import Board as b
import moves.move_tables as tb
import moves.move as m

#------------------------#
#     SETUP & HELPERS    #
#------------------------#

# change to two functions b/c tuple usage slows it down
def lssb(bb) -> int : # returns only lssb
    return bb & -bb if bb != 0 else 0

def pop_lssb(bb) -> int : # returns bb w/o lssb
    return bb & (bb-1) if bb != 0 else 0 
    
def lssb_sq(lssb) -> int : # lssb as least sig set bit, so lowest 1 in bb?
    return lssb.bit_length() - 1

def bb_to_encoded(bb, start, flag) -> list :
    encoded_moves = []

    while bb:
        least = lssb(bb)
        end = lssb_sq(least)
        bb = pop_lssb(bb)
        encoded_moves.append(m.encode_move(start, end, flag))
    
    return encoded_moves
    

def reverse_bb(bb) -> int : 
    bb = ((bb & 0x5555555555555555) << 1) | ((bb >> 1) & 0x5555555555555555)
    bb = ((bb & 0x3333333333333333) << 2) | ((bb >> 2) & 0x3333333333333333)
    bb = ((bb & 0x0F0F0F0F0F0F0F0F) << 4) | ((bb >> 4) & 0x0F0F0F0F0F0F0F0F)
    bb = ((bb & 0x00FF00FF00FF00FF) << 8) | ((bb >> 8) & 0x00FF00FF00FF00FF)
    bb = ((bb & 0x0000FFFF0000FFFF) << 16) | ((bb >> 16) & 0x0000FFFF0000FFFF)
    bb = (bb << 32) | (bb >> 32)

    return tb.bitmask(bb)

def not_bb(bb) -> int :
    return tb.bitmask(~bb)

#--------------------------#
#   SINGULAR PIECE MOVES   #
#--------------------------#

def knight_lookup(bb, same_occ) -> int :
    return tb.KNIGHT_MOVES[bb] & not_bb(same_occ)

def king_lookup(bb, same_occ) -> int :
    return tb.KING_MOVES[bb] & not_bb(same_occ)

def pawn_lookup(bb, color, all_occ, opp_occ, ep_sq=0) -> int :
    start_rank = tb.ROWS[1] if color > 0 else tb.ROWS[6]
    move = tb.north_one if color > 0 else tb.south_one

    step = move(bb) & not_bb(all_occ)
    double = move(step) & not_bb(all_occ) if step and (start_rank & bb) else 0

    attacks = tb.PAWN_WHITE_ATTACKS[bb] if color > 0 else tb.PAWN_BLACK_ATTACKS[bb]

    captures = attacks & opp_occ
    ep = attacks & ep_sq
    
    return step, double, captures, ep

def hq(bb, all_occ, mask) -> int : # hyperbola quintessence
    mask_occ = mask & all_occ
    reverse = reverse_bb(bb) << 1

    left = mask_occ - (bb << 1) # o ^ o-2r
    right = reverse_bb(reverse_bb(mask_occ) - reverse)
    moves = (left ^ right) & mask

    return moves

def rook_hq(bb, all_occ) -> int :
    sq = lssb_sq(bb)

    r = tb.ROWS[sq // 8]
    c = tb.COLUMNS[sq % 8]

    return hq(bb, all_occ, r) | hq(bb, all_occ, c)

def bishop_hq(bb, all_occ) -> int :
    diag = tb.DIAGONALS[bb]
    anti_diag = tb.ANTI_DIAGONALS[bb]

    return hq(bb, all_occ, diag) | hq(bb, all_occ, anti_diag)

def queen_hq(bb, all_occ) -> int :
    return rook_hq(bb, all_occ) | bishop_hq(bb, all_occ)

#---------------------#
#     PSEUDO MOVES    #
#---------------------#

def step_pseudo_moves(board: b, piece: str) :
    if not (piece == 'N' or piece == 'K'):
        raise ValueError('Wrong piece, only use N or K for step_pseudo_moves()')
    
    lookup = knight_lookup if piece == 'N' else king_lookup
    
    same_occ = board.same_occ()
    opp_occ = board.opp_occ()
    empty = not_bb(board.all_occ())

    bb = board.same_piece(piece)

    moves = []

    while bb:
        least = lssb(bb)
        bb = pop_lssb(bb)
        start = lssb_sq(least)
        possible_moves = lookup(least, same_occ)

        moves.extend(bb_to_encoded(possible_moves & opp_occ, start, m.CAPTURE))
        moves.extend(bb_to_encoded(possible_moves & empty, start, m.QUIET))

    return moves

def sliding_pseudo_moves(board: b, piece: str) :
    if not (piece == 'B' or piece == 'R' or piece == 'Q'):
        raise ValueError('Wrong piece, only use B, R, or Q for sliding_pseudo_moves()')
    
    if piece == 'B':
        hq_func = bishop_hq
    elif piece == 'R':
        hq_func = rook_hq
    else:
        hq_func = queen_hq
    
    all_occ = board.all_occ()
    same_occ = board.same_occ()
    opp_occ = board.opp_occ()
    empty = not_bb(all_occ)

    bb = board.same_piece(piece)

    moves = []

    while bb:
        least = lssb(bb)
        bb = pop_lssb(bb)
        start = lssb_sq(least)
        possible_moves = hq_func(least, all_occ) & not_bb(same_occ)

        moves.extend(bb_to_encoded(possible_moves & opp_occ, start, m.CAPTURE))
        moves.extend(bb_to_encoded(possible_moves & empty, start, m.QUIET))

    return moves

def pawn_pseudo_moves(board: b) :
    def pawn_promo(start, end, captured):
        if captured:
            # Flags 10, 11, 12, 13
            return [
                m.encode_move(start, end, m.PROMOTE_Q_CAP),
                m.encode_move(start, end, m.PROMOTE_R_CAP),
                m.encode_move(start, end, m.PROMOTE_B_CAP),
                m.encode_move(start, end, m.PROMOTE_N_CAP)
            ]
        else:
            # Flags 6, 7, 8, 9
            return [
                m.encode_move(start, end, m.PROMOTE_Q),
                m.encode_move(start, end, m.PROMOTE_R),
                m.encode_move(start, end, m.PROMOTE_B),
                m.encode_move(start, end, m.PROMOTE_N)
            ]
    
    bb = board.same_piece('P')
    color = board.color
    opp_occ = board.opp_occ()
    all_occ = board.all_occ()
    ep_sq = board.ep_sq

    promo_rank = tb.ROWS[7] if color > 0 else tb.ROWS[0]

    moves = []

    while bb:
        least = lssb(bb)
        bb = pop_lssb(bb)
        start = lssb_sq(least)
        step, double, caps, ep = pawn_lookup(least, color, all_occ, opp_occ, ep_sq)

        # EP
        if ep :
            moves.append(m.encode_move(start, lssb_sq(ep), m.EP))

        # CAPTURES
        promo_caps = caps & promo_rank
        reg_caps = caps & ~promo_rank
        
        while promo_caps:
            target = lssb_sq(lssb(promo_caps))
            moves.extend(pawn_promo(start, target, True))
            promo_caps = pop_lssb(promo_caps)

        moves.extend(bb_to_encoded(reg_caps, start, m.CAPTURE))

        # PUSHES
        promo_push = step & promo_rank
        reg_push = step & ~promo_rank
        
        while promo_push:
            target = lssb_sq(lssb(promo_push))
            moves.extend(pawn_promo(start, target, False))
            promo_push = pop_lssb(promo_push)
        moves.extend(bb_to_encoded(reg_push, start, m.QUIET))

        # DOUBLE PUSH
        if double:
            moves.append(m.encode_move(start, lssb_sq(double), m.DOUBLE_PUSH))
        
    return moves

def castling_moves(board: b) :
    if in_check(board):
        return []

    moves = []
    all_occ = board.all_occ()

    color_offset = 0 if board.color > 0 else 2

    for i in range(color_offset, color_offset + 2):
        strat = tb.CASTLE[i]
    
        if not (board.castle_rights & strat['bit']):
            continue
            
        if all_occ & strat['empty']:
            continue
            
        is_legal = True
        for sq in strat['safe']:
            if sq_in_attack(sq, board, -board.color):
                is_legal = False
                break
        
        if is_legal:
            moves.append(m.encode_move(strat['start'], strat['end'], strat['flag']))

    return moves

#-----------------#
#     LEGALITY    #
#-----------------#

def sq_in_attack(sq: int, board: b, atk_color: int) -> bool :
    '''
    Docstring for sq_in_attack
    
    :param sq: Tile shifts from 0 (not board rep)
    :type sq: int
    '''
    bb = 1 << sq
    all_occ = board.all_occ()
    
    pref = 'W' if atk_color > 0 else 'B'
    p = board.pieces
    
    if tb.KNIGHT_MOVES[bb] & p[pref + 'N']:
        return True
    if tb.KING_MOVES[bb] & p[pref + 'K']:
        return True
    
    # switched for opponent attacks
    pawn_attacks = tb.PAWN_BLACK_ATTACKS[bb] if atk_color > 0 else tb.PAWN_WHITE_ATTACKS[bb]
    if pawn_attacks & p[pref + 'P']:
        return True
    
    if rook_hq(bb, all_occ) & (p[pref + 'R'] | p[pref + 'Q']):
        return True
    if bishop_hq(bb, all_occ) & (p[pref + 'B'] | p[pref + 'Q']):
        return True
    
    return False

def in_check(board: b) -> bool :
    return sq_in_attack(lssb_sq(board.same_piece('K')), board, -board.color)

def gen_pseudo_moves(board: b) -> list[int] :
    moves = step_pseudo_moves(board, 'N')
    moves.extend(step_pseudo_moves(board, 'K'))
    moves.extend(sliding_pseudo_moves(board, 'B'))
    moves.extend(sliding_pseudo_moves(board, 'R'))
    moves.extend(sliding_pseudo_moves(board, 'Q'))
    moves.extend(pawn_pseudo_moves(board))
    moves.extend(castling_moves(board))
    return moves

def gen_legal_moves(board: b) -> list[int] :
    moves = gen_pseudo_moves(board)
    # print('generated psuedo moves:', moves)
    legal_moves = []

    for move in moves:
        board.make_move(move)
        
        king_sq = lssb_sq(board.opp_piece('K'))
        # b.print_bb(king_sq)
        sq_attacked = sq_in_attack(king_sq, board, board.color)
        # print(sq_attacked)
        if not sq_attacked:
            # print(move)
            legal_moves.append(move)
       
        board.undo_move(move)
    
    return legal_moves

