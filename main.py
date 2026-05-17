from engine.board import Board
from engine.moves import move_tables as tb
from engine.moves import movegen as mg
import engine.search as srch
from ml.model import ChessNet
import torch


MODEL_NAME = 'alphav2_10mil.pth' 
SEARCH_DEPTH = 3

def init_engine():
  device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
  model = ChessNet().to(device)
  
  try:
      checkpoint = torch.load(f'ml/models/{MODEL_NAME}', map_location=device, weights_only=True)
      model.load_state_dict(checkpoint)
      print(f"--- loaded neural evaluator: {MODEL_NAME}")
  except FileNotFoundError:
      print(f"--- warning: {MODEL_NAME} not found. using random weights.")
      
  model.eval()
  return model, device

def play_eve(model, device) :
  board = Board()
  board.fen_to_board()

  print("game start!")

  while True:
    print(board.board_to_fen())

    if board.color == 1:
      print("\n--- engine turn (white) ---")
      score, best_move = srch.search(board, SEARCH_DEPTH, device, model)
      
      if best_move is None:
          print("BLACK WON. white engine has no moves left. game over.")
          break
          
      print(f"engine picked move: {best_move} (evaluation: {score})")
      board.make_move(best_move)
        
    else:
      print("\n--- engine turn (black) ---")
      score, best_move = srch.search(board, SEARCH_DEPTH, device, model)
      
      if best_move is None:
          print("WHITE WON. black engine has no moves left. game over.")
          break
          
      print(f"engine picked move: {best_move} (evaluation: {score})")
      board.make_move(best_move)
  
  return

def play_pve(model, device) :
  board = Board()
  board.fen_to_board()

  print("game start!")

  while True:
    print(board)

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
      score, best_move = srch.search(board, SEARCH_DEPTH, device, model)
      
      if best_move is None:
          print("engine has no moves left. game over.")
          break
          
      print(f"engine picked move: {best_move} (evaluation: {score})")
      board.make_move(best_move)
  
  return


if __name__ == '__main__':
  model, device = init_engine()
  play_eve(model, device)


