from engine.board import Board
from engine.moves import movegen as mg
from engine.moves import move as mv
import engine.search as srch
from ml.model import ChessNet

import argparse
import os
import torch
import time


MODEL_NAME = 'alphav2_10mil' 
SEARCH_DEPTH = 3

# i can't lie Claude made this SQ_TO_IDX
SQ_TO_IDX = {f"{c}{r}": (int(r)-1)*8 + ord(c)-ord('a') for c in 'abcdefgh' for r in '12345678'}

def init_engine(device):
  model = ChessNet().to(device)
  
  try:
      checkpoint = torch.load(f'ml/models/{MODEL_NAME}.pth', map_location=device, weights_only=True)
      model.load_state_dict(checkpoint)
      print(f"--- loaded neural evaluator: {MODEL_NAME}")
  except FileNotFoundError:
      print(f"--- warning: {MODEL_NAME} not found. using random weights.")
      
  model.eval()
  return model

def get_human_move(legal_moves):
  PROMO_FLAGS = {
    'q': (mv.PROMOTE_Q, mv.PROMOTE_Q_CAP),
    'r': (mv.PROMOTE_R, mv.PROMOTE_R_CAP),
    'b': (mv.PROMOTE_B, mv.PROMOTE_B_CAP),
    'n': (mv.PROMOTE_N, mv.PROMOTE_N_CAP),
  }

  while True:
    raw = input("type your move (e.g. e2e4): ").strip().lower()
    if len(raw) < 4 or raw[:2] not in SQ_TO_IDX or raw[2:4] not in SQ_TO_IDX:
      print("invalid, try again.")
      continue

    start = SQ_TO_IDX[raw[:2]]
    end = SQ_TO_IDX[raw[2:4]]
    promo = raw[4] if len(raw) == 5 else None

    candidates = [move for move in legal_moves if mv.get_start(move) == start and mv.get_end(move) == end]

    if not candidates:
      print("illegal move, try again")
      continue

    if len(candidates) > 1:
      promo = input("promote to? (q/r/b/n): ").strip().lower()
      valid_flags = PROMO_FLAGS.get(promo, ())
      candidates = [move for move in candidates if mv.get_flag(move) in valid_flags]
      if not candidates:
        print("invalid promotion, try again")
        continue

    return candidates[0]

def play_eve(model) :
  board = Board()
  board.fen_to_board()

  print("game start!")
  print(board)
  game_fen = [board.board_to_fen()]

  turns = 0
  while turns < 200:
    if board.color == 1:
      print("\n--- engine turn (white) ---")
      score, best_move = srch.search(board, SEARCH_DEPTH, model)
      
      if best_move is None:
        print("BLACK WON. white engine has no moves left. game over.")
        break
          
      print(f"engine picked move: {best_move} (evaluation: {score})")
      board.make_move(best_move)
        
    else:
      print("\n--- engine turn (black) ---")
      score, best_move = srch.search(board, SEARCH_DEPTH, model)
      
      if best_move is None:
        print("WHITE WON. black engine has no moves left. game over.")
        break
          
      print(f"engine picked move: {best_move} (evaluation: {score})")
      board.make_move(best_move)
  
    print(board)
    game_fen.append(board.board_to_fen())
    turns += 1
  
  if turns >= 200:
     print('game exceeds 200 turns, terminated')

  timestamp = time.strftime("%Y%m%d_%H%M%S")
  path = f"tests/games/game_{timestamp}.txt"
  os.makedirs("tests/games", exist_ok=True)
  with open(path, 'w') as f:
    f.write('\n'.join(game_fen))
  print(f"game saved to {path}")

  return

def play_pve(model) :
  board = Board()
  board.fen_to_board()

  print("game start!")
  print(board)
  game_fen = [board.board_to_fen()]

  while True:

    if board.color == 1:
      legal_moves = mg.gen_legal_moves(board)
      if not legal_moves:
        print("checkmate or stalemate! game over.") #should probs check for this
        break
    
      print("\n--- your turn (white) ---")
      selected_move = get_human_move(legal_moves)          
      board.make_move(selected_move)
        
    # (engine)
    else:
      print("\n--- engine turn (black) ---")
      score, best_move = srch.search(board, SEARCH_DEPTH, model)
      
      if best_move is None:
        print("engine has no moves left. game over.")
        break
          
      print(f"engine picked move: {best_move} (evaluation: {score})")
      board.make_move(best_move)

    print(board)
    game_fen.append(board.board_to_fen())

  timestamp = time.strftime("%Y%m%d_%H%M%S")
  path = f"tests/games/game_{timestamp}.txt"
  os.makedirs("tests/games", exist_ok=True)
  with open(path, 'w') as f:
    f.write('\n'.join(game_fen))
  print(f"game saved to {path}")
  
  return

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mode', choices=['pve', 'eve'], help='pve: play against engine, eve: watch engine play itself')
    parser.add_argument('--model', type=str, default=MODEL_NAME, help='name of neural model (default: alphav2_10mil)')
    parser.add_argument('--depth', type=int, default=SEARCH_DEPTH, help='search depth (default: 3)')
    args = parser.parse_args()

    MODEL_NAME = args.model
    SEARCH_DEPTH = args.depth
    model = init_engine(srch.DEVICE)

    if args.mode == 'pve':
        play_pve(model)
    elif args.mode == 'eve':
        play_eve(model)


