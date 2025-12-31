from enum import Enum

# WE'RE GOING TO TRY A BITBOARD BASED SYSTEM
class Board:
    def __init__(self) :
        self.board = {
            "WP": 0,
            "WN": 0,
            "WB": 0,
            "WR": 0,
            "WQ": 0,
            "WK": 0,
            "BP": 0,
            "BN": 0,
            "BB": 0,
            "BR": 0,
            "BQ": 0,
            "BK": 0
        }

        self.color = 1
        
    @staticmethod
    def sq(r, c) :
        return r * 8 + c
    
    @staticmethod
    def place(s):
        return 1 << s
    
    @staticmethod
    def white_occ(board) :
        return (board.pieces["WP"] | board.pieces["WN"] | board.pieces["WB"] |
                board.pieces["WR"] | board.pieces["WQ"] | board.pieces["WK"])

    @staticmethod
    def black_occ(board) :
        return (board.pieces["BP"] | board.pieces["BN"] | board.pieces["BB"] |
                board.pieces["BR"] | board.pieces["BQ"] | board.pieces["BK"])

    @staticmethod
    def all_occ(board) :
        return Board.white_occ(board) | Board.black_occ(board)
        
    def __str__(self) :
        lines = []
        files = "    0   1   2   3   4   5   6   7"
        horizontal = "  +---+---+---+---+---+---+---+---+"

        lines.append(files)
        lines.append(horizontal)

        for r in range(8):
            row_str = f"{r} |"
            for c in range(8):
                sq = r * 8 + c
                piece_char = "   " 

                for name, bb in self.pieces.items():
                    if bb & (1 << sq):
                        piece_char = f" {name} "
                        break
                row_str += piece_char + "|"
            lines.append(row_str)
            lines.append(horizontal)


        return "\n".join(lines)
    




    

