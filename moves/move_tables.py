from board import Board as b

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

KNIGHT_MOVES = {
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
# THESE SHOULD BE LOOKUP ONLY, IDEAA: NO BLOCKS, NO OTHER PIECES
# ---- should be handled in move.py

def compute_knight_move(bb) : 
    # https://www.chessprogramming.org/Knight_Pattern
    # https://stackoverflow.com/questions/72296626/chess-bitboard-move-generation#:~:text=When%20you%20generate%20moves%20you,later%20stages%20of%20your%20AI.
    moves = 0
    for offset, mask in KNIGHT_MOVES.items() : 
        if mask & bb :
            moves |= bitmask(bb << offset if offset > 0 else bb >> -offset)

    return moves

def compute_king_move(bb) : 
    # https://www.chessprogramming.org/King_Pattern 
    horiz = east_one(bb) | west_one(bb)
    dr = horiz | bb

    return north_one(dr) | south_one(dr) | horiz

def compute_pawn_move(bb, color) :
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
