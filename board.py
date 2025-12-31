from enum import Enum



# WE'RE GOING TO TRY A BITBOARD BASED SYSTEM
class Board:
    def __init__(self) :
        self.pieces = {
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
        return (board.board["WP"] | board.board["WN"] | board.board["WB"] |
                board.board["WR"] | board.board["WQ"] | board.board["WK"])

    @staticmethod
    def black_occ(board) :
        return (board.board["BP"] | board.board["BN"] | board.board["BB"] |
                board.board["BR"] | board.board["BQ"] | board.board["BK"])

    @staticmethod
    def all_occ(board) :
        return Board.white_occ(board) | Board.black_occ(board)
        
    # https://www.365chess.com/board_editor.php
    def fen_to_board(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1') :
        fen_pieces = {
            'P': "WP", 'N': "WN", 'B': "WB", 'R': "WR", 'Q': "WQ", 'K': "WK",

            'p': "BP", 'n': "BN", 'b': "BB", 'r': "BR", 'q': "BQ", 'k': "BK",
        }

        for key in self.pieces:
            self.pieces[key] = 0

        try:
            fields = fen.split()
            rows = fields[0].split('/')
            if len(rows) != 8:
                raise ValueError("Invalid FEN, must have 8 ranks")

            i = 56
            for row in rows:
                j = 0
                for c in row:
                    if c.isdigit():
                        i += int(c)
                        j += int(c)
                    else:
                        mask = 1 << i
                        if c not in fen_pieces:
                            raise ValueError(f"Invalid FEN, invalid char: {c}")
                        self.pieces[fen_pieces[c]] |= mask
                        i += 1
                i -= 16
            
            self.color = 1 if fields[1]=='w' else -1 
        except Exception as e:
            raise ValueError(f"Invalid FEN, error: {e}")

    def __str__(self) :
        lines = []
        files = "    0   1   2   3   4   5   6   7"
        horizontal = "  +---+---+---+---+---+---+---+---+"

        lines.append(files)
        lines.append(horizontal)

        for r in range(8):
            row = f"{r} |"
            for c in range(8):
                sq = r * 8 + c
                piece_char = "   " 

                for name, bb in self.pieces.items():
                    if bb & (1 << sq):
                        piece_char = f"{name} "
                        break
                row += piece_char + "|"
            lines.append(row)
            lines.append(horizontal)


        return "\n".join(lines)
    




    

