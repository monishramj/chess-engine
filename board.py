from enum import Enum
import numpy as np


class Piece(Enum):
    EMPTY = 0
    AM = 7 # available move


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
    
    # def decode_tile(self, tile='a1') :
    #     if isinstance(tile, str):
    #         file = tile[0].lower()
    #         rank = int(tile[1])
    #         c = ord(file) - ord('a')
    #         r = 8 - rank
    #     else:
    #         r, c = tile
        
    #     return r, c
    
    def set_piece(self, tile=(0,0), val=Piece.EMPTY.value):
        r, c = tile
        self.board[r * 8 + c] = val
    
    def get_piece(self, tile=(0,0)) :
        r, c = tile
        return self.board[r * 8 + c]


    def is_white(val):
        return val > 0

    def is_black(val):
        return val < 0


    def __str__(self) :
        def piece_to_str(val):
            if val == 0:
                return "   "
            if val == 7:
                return " ⊙ "
            return f" {Piece(val).name}"
    
        lines = []
        files = "    0   1   2   3   4   5   6   7"
        horizontal = "  +---+---+---+---+---+---+---+---+"

        lines.append(files)
        lines.append(horizontal)

        for r in range(8):
            row = []
            for c in range(8):
                val = self.board[r * 8 + c]
                row.append(piece_to_str(val))
            rank = r
            lines.append(f"{rank} |" + "|".join(row) + "|")
            lines.append(horizontal)

        return "\n".join(lines)
    
