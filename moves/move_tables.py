
#------------------------#
#     SETUP & HELPERS    #
#------------------------#
# https://josherv.in/2021/03/19/chess-1/

def bitmask(num) :
    return num & ((1 << 64) - 1)

COLUMNS = [0x0101010101010101 << i for i in range(8)]
ROWS = [0xFF << (i*8) for i in range(8)]

def east_one(bb) :
    return bitmask(bb << 1) & ~COLUMNS[0]
def west_one(bb) :
    return bitmask(bb >> 1) & ~COLUMNS[7]   
def north_one(bb) :
    return bitmask(bb << 8)
def south_one(bb) :
    return bitmask(bb >> 8)

KNIGHT_SETUP = {
    6: bitmask(~(COLUMNS[0] | COLUMNS[1] | ROWS[7])),
    10: bitmask(~(COLUMNS[6] | COLUMNS[7] | ROWS[7])),
    15: bitmask(~(COLUMNS[0] | ROWS[6] | ROWS[7])),
    17: bitmask(~(COLUMNS[7] | ROWS[6] | ROWS[7])),
    -6: bitmask(~(COLUMNS[6] | COLUMNS[7] | ROWS[0])),
    -10: bitmask(~(COLUMNS[0] | COLUMNS[1] | ROWS[0])),
    -15: bitmask(~(COLUMNS[7] | ROWS[0] | ROWS[1])),
    -17: bitmask(~(COLUMNS[0] | ROWS[0] | ROWS[1])),
}

#---------------------#
#     COMPUTATIONS    #
#---------------------#

def _compute_diagonal(bb) :
    mask = bb
    nw = bb
    se = bb
    
    while nw := north_one(west_one(nw)): # wow walrus operator!!
        mask |= nw 
    while se := south_one(east_one(se)):
        mask |= se

    return mask

def _compute_antidiagonal(bb) :
    mask = bb
    ne = bb
    sw = bb

    while ne := south_one(west_one(ne)): 
        mask |= ne
    while sw := north_one(east_one(sw)):
        mask |= sw

    return mask

def _compute_knight_move(bb) : 
    # https://www.chessprogramming.org/Knight_Pattern
    # https://stackoverflow.com/questions/72296626/chess-bitboard-move-generation#:~:text=When%20you%20generate%20moves%20you,later%20stages%20of%20your%20AI.
    moves = 0
    for offset, mask in KNIGHT_SETUP.items() : 
        if mask & bb :
            moves |= bitmask(bb << offset if offset > 0 else bb >> -offset)

    return moves

def _compute_king_move(bb) : 
    # https://www.chessprogramming.org/King_Pattern 
    horiz = east_one(bb) | west_one(bb)
    dr = horiz | bb

    return north_one(dr) | south_one(dr) | horiz

def _compute_pawn_move(bb, color) :
    move = north_one if color > 0 else south_one
    start_rank = ROWS[1] if color > 0 else ROWS[6]

    step = move(bb)
    two_step = move(step) if start_rank & bb else 0

    moves = step | two_step
    attacks = east_one(step) | west_one(step)

    return moves, attacks
        
def compute_tables(compute_move) :
    table = {}
    for i in range(64):
        pos = 1 << i
        moves = compute_move(pos)
        table[pos] = moves

    return table

def compute_pawn_tables(compute_move, color) :
    moves = {}
    attacks = {}

    for i in range(64):
        pos = 1 << i
        m, a = compute_move(pos, color)
        moves[pos] = m
        attacks[pos] = a

    return moves, attacks

#----------------------#
#     LOOKUP TABLES    #
#----------------------#

DIAGONALS = compute_tables(_compute_diagonal)
ANTI_DIAGONALS = compute_tables(_compute_antidiagonal)

KNIGHT_MOVES = compute_tables(_compute_knight_move)
KING_MOVES = compute_tables(_compute_king_move)
# BISHOP_MOVES = compute_tables(_compute_bishop_move)
# ROOK_MOVES = compute_tables(_compute_rook_move)
# QUEEN_MOVES = compute_tables(_compute_queen_move)

PAWN_BLACK_MOVES, PAWN_BLACK_ATTACKS = compute_pawn_tables(_compute_pawn_move, -1)
PAWN_WHITE_MOVES, PAWN_WHITE_ATTACKS = compute_pawn_tables(_compute_pawn_move, 1)

