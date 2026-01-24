import moves.move as m
import moves.move_tables as tb

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
        self.ep_sq = 0

        self.castle_rights = 15 #1111, w_oo, w_ooo, b_oo, b_ooo

        self.history = [] # holds (castling, eq, captures if any, moving piece)
    
    def white_occ(self) :
        return (self.pieces["WP"] | self.pieces["WN"] | self.pieces["WB"] |
                self.pieces["WR"] | self.pieces["WQ"] | self.pieces["WK"])

    def black_occ(self) :
        return (self.pieces["BP"] | self.pieces["BN"] | self.pieces["BB"] |
                self.pieces["BR"] | self.pieces["BQ"] | self.pieces["BK"])

    def all_occ(self) :
        return Board.white_occ(self) | Board.black_occ(self)
        
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
        
    def opp_piece(self, piece: chr) :
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K']
        if piece not in pieces:
            raise ValueError('Invalid piece')
        
        if self.color > 0:
            return self.pieces['B' + piece]
        else:
            return self.pieces['W' + piece]
    
    def same_piece(self, piece: chr) :
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K']
        if piece not in pieces:
            raise ValueError('Invalid piece')
        
        if self.color > 0:
            return self.pieces['W' + piece]
        else:
            return self.pieces['B' + piece]
             
    def piece_at(self, tile: int) :
        mask = 1 << tile
        for name, bb in self.pieces.items():
            if bb & mask:
                return name
        return None
    
    def _toggle_piece(self, name, sq_bit) :
        self.pieces[name] ^= sq_bit

    def _get_promo_piece(self, flag) :
        color_char = 'W' if self.color > 0 else 'B'
        if flag in (m.PROMOTE_Q, m.PROMOTE_Q_CAP): return color_char + 'Q'
        if flag in (m.PROMOTE_R, m.PROMOTE_R_CAP): return color_char + 'R'
        if flag in (m.PROMOTE_B, m.PROMOTE_B_CAP): return color_char + 'B'
        if flag in (m.PROMOTE_N, m.PROMOTE_N_CAP): return color_char + 'N'

    def make_move(self, move) :
        start = m.get_start(move)
        end = m.get_end(move)
        flag = m.get_flag(move)
        
        start_bit = 1 << start
        end_bit = 1 << end
        
        moving_piece = self.piece_at(start)
        captured_piece = self.piece_at(end)

        # print(start, ',', end, ',', flag, ',', moving_piece, ',', captured_piece)
        
        self.history.append((self.castle_rights, self.ep_sq, captured_piece, moving_piece))
        
        if captured_piece and flag != m.EP:
            self._toggle_piece(captured_piece, end_bit)
            
        if flag == m.QUIET or flag == m.CAPTURE:
            self._toggle_piece(moving_piece, start_bit)
            self._toggle_piece(moving_piece, end_bit)
            self.ep_sq = 0
            
        elif flag == m.DOUBLE_PUSH:
            self._toggle_piece(moving_piece, start_bit)
            self._toggle_piece(moving_piece, end_bit)

            # Set EP square to the square BEHIND the pawn
            self.ep_sq = 1 << (start + 8 if self.color > 0 else start - 8)
            
        elif flag in (m.OO, m.OOO):
            self._toggle_piece(moving_piece, start_bit)
            self._toggle_piece(moving_piece, end_bit)

            if flag == m.OO:
                r_start, r_end = (7, 5) if self.color > 0 else (63, 61)
            else:
                r_start, r_end = (0, 3) if self.color > 0 else (56, 59)

            r_name = "WR" if self.color > 0 else "BR"
            self._toggle_piece(r_name, 1 << r_start)
            self._toggle_piece(r_name, 1 << r_end)
            self.ep_sq = 0

        elif flag == m.EP:
            self._toggle_piece(moving_piece, start_bit)
            self._toggle_piece(moving_piece, end_bit)

            ep_cap = end - 8 if self.color > 0 else end + 8
            captured_pawn = "BP" if self.color > 0 else "WP"
            self._toggle_piece(captured_pawn, 1 << ep_cap)
            self.ep_sq = 0
        
        elif flag >= 6 and flag <= 13: # promotions
            self._toggle_piece(moving_piece, start_bit)
            promo_piece = self._get_promo_piece(flag)
            self._toggle_piece(promo_piece, end_bit)
            self.ep_sq = 0

        self.castle_rights &= tb.CASTLE_UPDATER[start]
        self.castle_rights &= tb.CASTLE_UPDATER[end]
        
        self.color *= -1

    def undo_move(self, move) :
        # print('undoing move')
        old_rights, old_ep, captured_piece, moving_piece = self.history.pop()
        self.color *= -1

        start = m.get_start(move)
        end = m.get_end(move)
        flag = m.get_flag(move)
        # print('undoing flag', flag)
        
        start_bit = 1 << start
        end_bit = 1 << end

        if flag in (m.OO, m.OOO):
            # print(moving_piece)
            self._toggle_piece(moving_piece, start_bit)
            self._toggle_piece(moving_piece, end_bit)

            if flag == m.OO:
                r_start, r_end = (7, 5) if self.color > 0 else (63, 61)
            else:
                r_start, r_end = (0, 3) if self.color > 0 else (56, 59)

            r_name = "WR" if self.color > 0 else "BR"
            self._toggle_piece(r_name, 1 << r_start)
            self._toggle_piece(r_name, 1 << r_end)

        elif flag == m.EP:
            self._toggle_piece(moving_piece, start_bit)
            self._toggle_piece(moving_piece, end_bit)

            ep_cap_sq = end - 8 if self.color > 0 else end + 8
            victim_pawn = "BP" if self.color > 0 else "WP"
            self._toggle_piece(victim_pawn, 1 << ep_cap_sq)

        elif flag >= 6 and flag <= 13: # promotions
            promo_piece = self._get_promo_piece(flag)
            self._toggle_piece(promo_piece, end_bit)

            pawn_name = "WP" if self.color > 0 else "BP"
            self._toggle_piece(pawn_name, start_bit)

            if captured_piece:
                self._toggle_piece(captured_piece, end_bit)

        else: # QUIET, CAPTURE, DOUBLE_PUSH
            self._toggle_piece(moving_piece, start_bit)
            self._toggle_piece(moving_piece, end_bit)
            if captured_piece:
                self._toggle_piece(captured_piece, end_bit)

        self.castle_rights = old_rights
        self.ep_sq = old_ep

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
            

            self.color = 1 if fields[1] == 'w' else -1 

            self.castle_rights = 0
            if fields[2] != '-':
                if 'K' in fields[2]: self.castle_rights |= 1
                if 'Q' in fields[2]: self.castle_rights |= 2
                if 'k' in fields[2]: self.castle_rights |= 4
                if 'q' in fields[2]: self.castle_rights |= 8

            if fields[3] != '-':
                col = ord(fields[3][0]) - ord('a')
                row = int(fields[3][1]) - 1
                self.ep_sq = 1 << (row * 8 + col)
            else:
                self.ep_sq = 0
            
 
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
    def print_bb(bb: int) :
        for r in range(7, -1, -1) :
            row = ' '.join('1' if bb & (1 << (r*8 + c)) else '0' for c in range(8))
            print(f"{r} | {row}")
        
        print("    --------------\n    a b c d e f g h")


    def copy(self) :
        b = Board()
        b.pieces = self.pieces.copy()
        b.color = self.color
        return b

    

