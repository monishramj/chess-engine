from engine.board import Board
from engine.moves import move_tables as tb
from engine.moves import movegen as mg
import engine.search as srch
from ml.model import ChessNet
import os
import torch
import time

MODEL_NAME = 'alphav2_10mil.pth' 
SEARCH_DEPTH = 3

def init_engine(device):
  model = ChessNet().to(device)
  
  try:
      checkpoint = torch.load(f'ml/models/{MODEL_NAME}', map_location=device, weights_only=True)
      model.load_state_dict(checkpoint)
      print(f"--- loaded neural evaluator: {MODEL_NAME}")
  except FileNotFoundError:
      print(f"--- warning: {MODEL_NAME} not found. using random weights.")
      
  model.eval()
  return model

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
      for idx, move in enumerate(legal_moves):
          print(f"{idx}: {move}")
          
      try:
          choice = int(input("select move index: "))
          selected_move = legal_moves[choice]
      except (ValueError, IndexError):
          print("invalid input, pick 1st choice")
          selected_move = legal_moves[0]
          
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


if __name__ == '__main__':
  model = init_engine(srch.DEVICE)
  play_eve(model)


