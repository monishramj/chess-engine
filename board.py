from enum import Enum
import numpy as np


class Piece(Enum):
    EMPTY = 0

    # white
    WP = 1 # pawn
    WN = 2 # knight
    WB = 3 # bishop
    WR = 4 # rook
    WQ = 5 # queen
    WK = 6 # king

    # black
    BP = -1
    BN = -2
    BB = -3
    BR = -4
    BQ = -5
    BK = -6


class Board:
    def __init__(self) :
        self.board = np.zeros((8,8), dtype=int)

    def __str__(self) :
        def piece_to_str(val) :
            for piece in Piece:
                if piece.value == val:
                    if piece.value == 0:
                        return '.'
                    return piece.name
            return '.'
    
        rows = []
        for row in self.board:
            row_str = ' '.join(f'{piece_to_str(val):>3}' for val in row)
            rows.append(row_str)
        return '---------------------------------\n|' + '|\n|                               |\n|'.join(rows) + '|\n---------------------------------'


b = Board()
b.board[6][0] = Piece.WP.value
b.board[0][4] = Piece.BK.value
print(b)