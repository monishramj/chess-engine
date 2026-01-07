class Board :
    def __init__(self) :
        self.pieces = {
            "WP" : 0,
            "WN" : 0,
            "WB" : 0,
            "WR" : 0,
            "WQ" : 0,
            "WK" : 0,
            "BP" : 0,
            "BN" : 0,
            "BB" : 0,
            "BR" : 0,
            "BQ" : 0,
            "BK" : 0
        }
        self.color = 1
        
        # TODO: implement rest of fields
        
    @staticmethod
    def sq(r, c) :
        return r * 8 + c
    
    @staticmethod
    def place(s) :
        return 1 << s
    
    def white_occ(self) :
        return (self.pieces["WP"] | self.pieces["WN"] | self.pieces["WB"] |
                self.pieces["WR"] | self.pieces["WQ"] | self.pieces["WK"])

    def black_occ(self) :
        return (self.pieces["BP"] | self.pieces["BN"] | self.pieces["BB"] |
                self.pieces["BR"] | self.pieces["BQ"] | self.pieces["BK"])

    def all_occ(self) :
        return Board.white_occ(self) | Board.black_occ(self)
        
    def is_occ(self, tile) :
        return ((1 << tile) & Board.all_occ(self)) != 0
    
    def is_white(self, tile) :
        return ((1 << tile) & Board.white_occ(self)) != 0
    
    def is_black(self, tile) :
        return ((1 << tile) & Board.black_occ(self)) != 0
    
    def same_occ(self) :
        if self.color > 0:
            return Board.white_occ(self)
        else:
            return Board.black_occ(self)
        
    def opp_occ(self) :
        if self.color > 0:
            return Board.black_occ(self)
        else:
            return Board.white_occ(self)
    
    def piece_at(self, tile) :
        mask = 1 << tile
        for name, bb in self.pieces.items():
            if bb & mask:
                return name
        return None
    
    def move(self, start, end) :
        if not self.is_occ(start):
            return None
        
        start_tile = 1 << start
        end_tile = 1 << end

        piece = self.piece_at(start) 
        if piece:
            output = self.copy()
            output.pieces[piece] = (output.pieces[piece] ^ start_tile) | end_tile
            output.color *= -1

            #! remove existing piece there, don't forget to check for checks and same piece later  :Sob :
            for other, o_bb in output.pieces.items():
                if end_tile & o_bb and other != piece:
                    output.pieces[other] ^= end_tile

            return output
            
        raise ValueError(f'Invalid move.')


    #? https ://www.chess.com/analysis
    def fen_to_board(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1') :
        fen_pieces = {
            'P' : "WP", 'N' : "WN", 'B' : "WB", 'R' : "WR", 'Q' : "WQ", 'K' : "WK",

            'p' : "BP", 'n' : "BN", 'b' : "BB", 'r' : "BR", 'q' : "BQ", 'k' : "BK",
        }

        for key in self.pieces :
            self.pieces[key] = 0

        try :
            fields = fen.split()
            rows = fields[0].split('/')
            if len(rows) != 8 :
                raise ValueError("Invalid FEN, must have 8 ranks")

            i = 56
            for row in rows :
                j = 0
                for c in row :
                    if c.isdigit() :
                        i += int(c)
                        j += int(c)
                    else :
                        mask = 1 << i
                        if c not in fen_pieces :
                            raise ValueError(f"Invalid FEN, invalid char : {c}")
                        self.pieces[fen_pieces[c]] |= mask
                        i += 1
                i -= 16
            
            self.color = 1 if fields[1]=='w' else -1 
        except Exception as e :
            raise ValueError(f"Invalid FEN, error : {e}")

    def __str__(self) :
        lines = []
        files = "    a   b   c   d   e   f   g   h"
        horizontal = "  +---+---+---+---+---+---+---+---+"

        lines.append(horizontal)

        for r in range(7, -1, -1) :
            row = f"{r} |"
            for c in range(8):
                sq = r * 8 + c
                piece_char = "   " 

                for name, bb in self.pieces.items() :
                    if bb & (1 << sq) :
                        piece_char = f"{name} "
                        break
                row += piece_char + "|"
            lines.append(row)
            lines.append(horizontal)
        
        lines.append(files)
        return "\n".join(lines) + '\n'
    
    @staticmethod
    def print_bb(bb) :
        for r in range(7, -1, -1) :
            row = ' '.join('1' if bb & (1 << (r*8 + c)) else '0' for c in range(8))
            print(f"{r} | {row}")
        
        print("    --------------\n    a b c d e f g h")


    def copy(self) :
        b = Board()
        b.pieces = self.pieces.copy()
        b.color = self.color
        return b

    

