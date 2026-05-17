from .board import Board
from engine.moves import movegen as mg

import torch
import numpy as np

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

def eval_position(board: Board, device, model) -> float:
  tensor = board.board_to_tensor().to(device)

  if tensor.dim() == 3:
        tensor = tensor.unsqueeze(0)

  turn_layer = torch.full((1, 1, 8, 8), float(board.color), dtype=torch.float32).to(device)
  input_tensor = torch.cat([tensor, turn_layer], dim=1)
  
  with torch.no_grad():
    return model(input_tensor).item()

def search(board: Board, depth: int, device, model) :
    return minimax(board, depth, board.color, device, model, -np.inf, np.inf)

def minimax(board: Board, depth: int, color: int, device, model, a, b) :
    if depth == 0:
      return eval_position(board, device, model), None
    
    legal_moves = mg.gen_legal_moves(board) # iterating thru twice, can fix that later
    if not legal_moves:
        if mg.in_check(board) :
            return (-np.inf if color == 1 else np.inf), None
        return 0.5, None

    best_move = None
    best = -np.inf if color == 1 else np.inf

    for move in legal_moves:
      board.make_move(move)
      score, unused = minimax(board, depth - 1, -color, device, model, a, b)
      board.undo_move(move)

      if color == 1: 
        if score > best:
          best = score
          best_move = move
        a = max(a, best)
        if b <= a :
          break
      else: 
        if score < best:
          best = score
          best_move = move
        b = min(b, best)
        if b <= a:
          break

    return best, best_move

