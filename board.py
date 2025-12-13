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
        self.board = np.zeros((64), dtype=int)
    
    def place_piece(self, tile='a1', val=0):
        if isinstance(tile, str):
            file = tile[0].lower()
            rank = int(tile[1])
            c = ord(file) - ord('a')
            r = 8 - rank
        else:
            r, c = tile

        self.board[r * 8 + c] = val

    def is_white(self, val):
        return val > 0

    def is_black(self, val):
        return val < 0

    def __str__(self) :
        def piece_to_str(val):
            if val == 0:
                return "   "
            return f" {Piece(val).name}"
    
        lines = []
        files = "    a   b   c   d   e   f   g   h"
        horizontal = "  +---+---+---+---+---+---+---+---+"

        lines.append(files)
        lines.append(horizontal)

        for r in range(8):
            row = []
            for c in range(8):
                val = self.board[r * 8 + c]
                row.append(piece_to_str(val))
            rank = 8 - r
            lines.append(f"{rank} |" + "|".join(row) + "|")
            lines.append(horizontal)

        return "\n".join(lines)



# test code
b = Board()
b.place_piece((0, 4), Piece.BK.value)
b.place_piece('c2', Piece.WP.value)
print(b)