from board import Board as b

def bitmask(num) :
    return num & ((1 << 64) - 1)



#--------------#
#     SETUP    #
#--------------#
# https://josherv.in/2021/03/19/chess-1/


COLUMNS = [0x0101010101010101 << i for i in range(8)]
ROWS = [0xFF << (i*8) for i in range(8)]
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



def compute_knight_move(bb) : 
    # https://www.chessprogramming.org/Knight_Pattern
    # https://stackoverflow.com/questions/72296626/chess-bitboard-move-generation#:~:text=When%20you%20generate%20moves%20you,later%20stages%20of%20your%20AI.
    moves = 0
    for offset, mask in KNIGHT_MOVES.items() : 
        if mask & bb :
            moves |= bitmask(bb << offset if offset > 0 else bb >> -offset)

    return moves

    # for move in moves:
    #     b.print_bb(move)
    #     print('---------')
    
    # print(moves)

def compute_king_move(bb) : 
    # https://www.chessprogramming.org/King_Pattern
    right = bitmask(bb << 1) & ~COLUMNS[0]         
    left = bitmask(bb >> 1) & ~COLUMNS[7]    
    horiz = right | left

    moves = horiz | bb
    up = bitmask(moves << 8)
    down = bitmask(moves >> 8)

    return up | down | left | right

def compute_tables(compute_move) :
    table = {}
    for i in range(64):
        pos = 1 << i
        moves = compute_move(pos)
        table[pos] = moves

    return table
