from board import Board as b
import moves.movegen as mg

import time

def perft(board, depth) :
    legal_moves = mg.gen_legal_moves(board)
    if depth == 1:
        return len(legal_moves)
    
    nodes = 0
    for move in legal_moves:
        board.make_move(move)
        nodes += perft(board, depth - 1)
        board.undo_move(move)

    return nodes

def perft_test(depth, fen):
    board = b()
    if fen:
        board.fen_to_board(fen)
    else:
        board.fen_to_board()
    
    print(f"\ntesting FEN: {fen if fen else 'starting position'}")
    print(board)

    for i in range(1, depth+1) :
        start_time = time.time()

        nodes = perft(board, i)

        end_time = time.time()
        duration = end_time - start_time

        nps = int(nodes / duration) if duration > 0 else 0
        print(f"depth {i}: {nodes} nodes | time: {duration:.3f}s | NPS: {nps:,}")

perft_test(4, 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -')
perft_test(4, '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1')
perft_test(4, 'r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1')
perft_test(4, 'rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8')
perft_test(4, 'r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10')