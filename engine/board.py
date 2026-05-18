from .moves import move as m
from .moves import move_tables as tb
from .moves import movegen as mg

import numpy as np
import torch
from typing import Any, Optional

class Board :
    def __init__(self, fen: Optional[str] = None) :
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

        # keep track of pieces, so we don't have to do piece_at loop which saves so much
        self.mailbox: list[Optional[str]] = [None] * 64 

        self.color = 1
        self.ep_sq = 0

        self.castle_rights = 15 #1111, w_oo, w_ooo, b_oo, b_ooo

        self.history = [] # holds (castling, eq, captures if any, moving piece)

        if fen is not None:
            self.fen_to_board(fen)
        

    def white_occ(self) :
        return (self.pieces["WP"] | self.pieces["WN"] | self.pieces["WB"] |
                self.pieces["WR"] | self.pieces["WQ"] | self.pieces["WK"])

    def black_occ(self) :
        return (self.pieces["BP"] | self.pieces["BN"] | self.pieces["BB"] |
                self.pieces["BR"] | self.pieces["BQ"] | self.pieces["BK"])

    def all_occ(self) :
        return self.white_occ() | self.black_occ()

    def same_occ(self) :
        if self.color > 0:
            return self.white_occ()
        else:
            return self.black_occ()

    def opp_occ(self) :
        if self.color > 0:
            return self.black_occ()
        else:
            return self.white_occ()

    def opp_piece(self, piece: str) :
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K']
        if piece not in pieces:
            raise ValueError('Invalid piece')

        if self.color > 0:
            return self.pieces['B' + piece]
        else:
            return self.pieces['W' + piece]

    def same_piece(self, piece: str) :
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K']
        if piece not in pieces:
            raise ValueError('Invalid piece')

        if self.color > 0:
            return self.pieces['W' + piece]
        else:
            return self.pieces['B' + piece]

    def _toggle_piece(self, name, sq_idx) :
        sq_bit = 1 << sq_idx
        self.pieces[name] ^= sq_bit
        if self.pieces[name] & sq_bit:
            self.mailbox[sq_idx] = name
        else:
            self.mailbox[sq_idx] = None

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

        moving_piece = self.mailbox[start]
        captured_piece = self.mailbox[end]

        self.history.append((self.castle_rights, self.ep_sq, captured_piece, moving_piece))

        if captured_piece and flag != m.EP:
            self._toggle_piece(captured_piece, end)

        if flag == m.QUIET or flag == m.CAPTURE:
            self._toggle_piece(moving_piece, start)
            self._toggle_piece(moving_piece, end)
            self.ep_sq = 0

        elif flag == m.DOUBLE_PUSH:
            self._toggle_piece(moving_piece, start)
            self._toggle_piece(moving_piece, end)

            # Set EP square to the square BEHIND the pawn
            self.ep_sq = 1 << (start + 8 if self.color > 0 else start - 8)

        elif flag in (m.OO, m.OOO):
            self._toggle_piece(moving_piece, start)
            self._toggle_piece(moving_piece, end)

            if flag == m.OO:
                r_start, r_end = (7, 5) if self.color > 0 else (63, 61)
            else:
                r_start, r_end = (0, 3) if self.color > 0 else (56, 59)

            r_name = "WR" if self.color > 0 else "BR"
            self._toggle_piece(r_name, r_start)
            self._toggle_piece(r_name, r_end)
            self.ep_sq = 0

        elif flag == m.EP:
            self._toggle_piece(moving_piece, start)
            self._toggle_piece(moving_piece, end)

            ep_cap = end - 8 if self.color > 0 else end + 8
            captured_pawn = "BP" if self.color > 0 else "WP"
            self._toggle_piece(captured_pawn, ep_cap)
            self.ep_sq = 0

        elif flag >= 6 and flag <= 13: # promotions
            self._toggle_piece(moving_piece, start)
            promo_piece = self._get_promo_piece(flag)
            self._toggle_piece(promo_piece, end)
            self.ep_sq = 0

        self.castle_rights &= tb.CASTLE_UPDATER[start]
        self.castle_rights &= tb.CASTLE_UPDATER[end]

        self.color *= -1

    def undo_move(self, move) :
        old_rights, old_ep, captured_piece, moving_piece = self.history.pop()
        self.color *= -1

        start = m.get_start(move)
        end = m.get_end(move)
        flag = m.get_flag(move)


        if flag in (m.OO, m.OOO):
            self._toggle_piece(moving_piece, start)
            self._toggle_piece(moving_piece, end)

            if flag == m.OO:
                r_start, r_end = (7, 5) if self.color > 0 else (63, 61)
            else:
                r_start, r_end = (0, 3) if self.color > 0 else (56, 59)

            r_name = "WR" if self.color > 0 else "BR"
            self._toggle_piece(r_name, r_start)
            self._toggle_piece(r_name, r_end)

        elif flag == m.EP:
            self._toggle_piece(moving_piece, start)
            self._toggle_piece(moving_piece, end)

            ep_cap_sq = end - 8 if self.color > 0 else end + 8
            victim_pawn = "BP" if self.color > 0 else "WP"
            self._toggle_piece(victim_pawn, ep_cap_sq)

        elif flag >= 6 and flag <= 13: # promotions
            promo_piece = self._get_promo_piece(flag)
            self._toggle_piece(promo_piece, end)

            pawn_name = "WP" if self.color > 0 else "BP"
            self._toggle_piece(pawn_name, start)

            if captured_piece:
                self._toggle_piece(captured_piece, end)

        else: # QUIET, CAPTURE, DOUBLE_PUSH
            self._toggle_piece(moving_piece, start)
            self._toggle_piece(moving_piece, end)
            if captured_piece:
                self._toggle_piece(captured_piece, end)

        self.castle_rights = old_rights
        self.ep_sq = old_ep
        
    
    def board_to_tensor(self) :
        tensor = torch.zeros((12, 8, 8), dtype=torch.float32)

        # ensure order in case i change self.pieces later
        piece_order = ["WP", "WN", "WB", "WR", "WQ", "WK", 
                       "BP", "BN", "BB", "BR", "BQ", "BK"]

        for idx, piece in enumerate(piece_order):
            bb = self.pieces[piece]

            while bb:
                least = mg.lssb(bb)
                i = mg.lssb_sq(least)
                bb = mg.pop_lssb(bb)
            
                row = i // 8
                col = i % 8
            
                tensor[idx][row][col] = 1.0
        
        
        return tensor

    #? https://www.chess.com/analysis
    def fen_to_board(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1') :
        fen_pieces = {
            'P' : "WP", 'N' : "WN", 'B' : "WB", 'R' : "WR", 'Q' : "WQ", 'K' : "WK",
            'p' : "BP", 'n' : "BN", 'b' : "BB", 'r' : "BR", 'q' : "BQ", 'k' : "BK",
        }
        self.mailbox = [None] * 64

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
                        piece_name = fen_pieces[c]
                        self.pieces[piece_name] |= mask
                        self.mailbox[i] = piece_name
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
    
    def board_to_fen(self) :
        piece_to_fen = {
            "WP": 'P', "WN": 'N', "WB": 'B', "WR": 'R', "WQ": 'Q', "WK": 'K',
            "BP": 'p', "BN": 'n', "BB": 'b', "BR": 'r', "BQ": 'q', "BK": 'k'
        }

        rows = []
        for r in range(7, -1, -1):
            empty = 0
            row = ''
            for c in range(8):
                piece = self.mailbox[r * 8 + c]
                if piece:
                    if empty: row += str(empty); empty = 0
                    row += piece_to_fen[piece]
                else:
                    empty += 1
            if empty: row += str(empty)
            rows.append(row)

        color = 'w' if self.color > 0 else 'b'

        castle = ''
        if self.castle_rights & 1: castle += 'K'
        if self.castle_rights & 2: castle += 'Q'
        if self.castle_rights & 4: castle += 'k'
        if self.castle_rights & 8: castle += 'q'
        if not castle: castle = '-'

        if self.ep_sq:
            ep_idx = mg.lssb_sq(self.ep_sq)
            ep = "abcdefgh"[ep_idx % 8] + str(ep_idx // 8 + 1)
        else:
            ep = '-'

        return f"{'/'.join(rows)} {color} {castle} {ep} 0 1"

    def __str__(self) :
        lines = []
        files = "    a   b   c   d   e   f   g   h"
        horizontal = "  +---+---+---+---+---+---+---+---+"

        lines.append(horizontal)

        for r in range(7, -1, -1) :
            row = f"{r + 1} |"
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

    def copy(self):
        b = Board()
        b.pieces = self.pieces.copy()
        b.mailbox = self.mailbox.copy()
        b.color = self.color
        b.ep_sq = self.ep_sq
        b.castle_rights = self.castle_rights
        b.history = self.history.copy()
        return b
