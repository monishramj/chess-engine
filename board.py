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
    def __init__(self, color=1) :
        self.board = np.zeros((64), dtype=int)
        self.color = 1 # white

    # https://www.365chess.com/board_editor.php
    def fen_to_board(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1') :
        try:
            fields = fen.split()
            rows = fields[0].split('/')
            i = 0
            for row in rows:
                for c in row:
                    if c.isdigit():
                        i += int(c)
                    else:
                        piece = Board.ascii_to_piece(c)
                        self.set_piece(tile=(i//8, i%8), val=piece)
                        i += 1
            
            if fields[1] == 'w': #2nd place thing shows turn
                self.color = 1
            else:
                self.color = -1 
        except :
            raise ValueError("Invalid FEN, error in fen_to_board")

    @staticmethod
    def ascii_to_piece(c) :
        match ord(c):
            # black
            case 114: # rook
                return Piece.BR.value
            case 110: # knight
                return Piece.BN.value
            case 98: # bishop
                return Piece.BB.value
            case 113: # queen
                return Piece.BQ.value
            case 107: # king
                return Piece.BK.value
            case 112: # pawn
                return Piece.BP.value

            # white
            case 82:
                return Piece.WR.value
            case 78:
                return Piece.WN.value
            case 66:
                return Piece.WB.value
            case 81:
                return Piece.WQ.value
            case 75:
                return Piece.WK.value
            case 80:
                return Piece.WP.value  
        return 0

    @staticmethod
    def is_white(val):
        return val > 0

    @staticmethod
    def is_black(val):
        return val < 0

    def set_piece(self, tile=(0,0), val=Piece.EMPTY.value):
        r, c = tile
        self.board[r * 8 + c] = val
    
    def get_piece(self, tile=(0,0)) :
        r, c = tile
        return self.board[r * 8 + c]


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

