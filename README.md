# chess-engine
 
A bitboard-based chess engine written in Python, with a planned rewrite in C.
 
- **Bitboard representation** — 64-bit integers for compact board state
- **Move generation** — ray attacks for sliding pieces, precomputed lookup tables for knights and kings, full pawn logic (double pushes, en passant, promotions)
- **Move encoding** — compact 16-bit move format with flag bits for move type
- **Legality checking** — full check detection and pseudo-legal move filtering
- **FEN parsing** — load any board position via FEN string
- **Perft testing** — correctness validation across standard test positions
 
## Roadmap
 
- [x] Bitboard infrastructure & mailbox
- [x] Pseudo-legal & legal move generation
- [x] Perft testing validation
- [ ] Positional evaluation (PST, mobility, etc.)
- [ ] Search improvements (transposition tables, iterative deepening)
- [ ] UCI protocol support / GUI implementation
 
## How to Run
 
Run the perft tests to verify move generation:
 
```bash
python3 moves/perft_test.py
```
