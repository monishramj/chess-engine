from board import Board as b

def bitmask(num) :
    return num & ((1 << 64) - 1)

#--------------#
#     SETUP    #
#--------------#
COLUMNS = [0x0101010101010101 << i for i in range(8)]
ROWS = [0xFF << (i*8) for i in range(8)]
KNIGHT_MASKS = {
        6: bitmask(~(COLUMNS[0] | COLUMNS[1] | ROWS[7])),
        10: bitmask(~(COLUMNS[6] | COLUMNS[7] | ROWS[7])),
        15: bitmask(~(COLUMNS[0] | ROWS[6] | ROWS[7])),
        17: bitmask(~(COLUMNS[7] | ROWS[6] | ROWS[7])),
        -6: bitmask(~(COLUMNS[6] | COLUMNS[7] | ROWS[0])),
        -10: bitmask(~(COLUMNS[0] | COLUMNS[1] | ROWS[0])),
        -15: bitmask(~(COLUMNS[7] | ROWS[0] | ROWS[1])),
        -17: bitmask(~(COLUMNS[0] | ROWS[0] | ROWS[1])),
    }



def knight_moves(bb) : 
    # https://www.chessprogramming.org/Knight_Pattern
    # https://stackoverflow.com/questions/72296626/chess-bitboard-move-generation#:~:text=When%20you%20generate%20moves%20you,later%20stages%20of%20your%20AI.
    offsets = [6, 15, 17, 10]
    moves = []
    for offset in offsets : 
        if KNIGHT_MASKS[offset] & bb:
            moves.append(bb << offset)
        if KNIGHT_MASKS[-offset] & bb:
            moves.append(bb >> offset)

    return moves

    # for move in moves:
    #     b.print_bb(move)
    #     print('---------')
    
    # print(moves)

def compute_knight_tables() :
    table = {}
    for i in range(64):
        pos = 1 << i
        moves = knight_moves(pos)
        table[pos] = moves

    return table
