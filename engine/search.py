from .board import Board
from engine.moves import movegen as mg

import torch
import numpy as np

DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

PIECE_VALUES = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0 }

def neural_eval_pos(board: Board, model) -> float :
  tensor = board.board_to_tensor().to(DEVICE)

  if tensor.dim() == 3:
        tensor = tensor.unsqueeze(0)

  turn_layer = torch.full((1, 1, 8, 8), float(board.color), dtype=torch.float32).to(DEVICE)
  input_tensor = torch.cat([tensor, turn_layer], dim=1)
  
  with torch.no_grad():
    return model(input_tensor).item()
  
# basic eval to fix material eval issues for V1 push
def material_eval_pos(board: Board) -> float :
  score = 0
  for name, bb in board.pieces.items():
    color = 1 if name[0] == 'W' else -1
    piece = name[1]
    count = bin(bb).count('1')
    score += PIECE_VALUES[piece] * count * color
  return np.tanh(score / 10)
  
def eval_pos(board: Board, model) :
  neural_weight = .7 # arbitrary 
  material_weight = .3

  neural = neural_eval_pos(board, model) * neural_weight
  material = material_eval_pos(board) * material_weight

  return neural + material

def search(board: Board, depth: int, model) :
    return minimax(board, depth, board.color,  model, -np.inf, np.inf)

def minimax(board: Board, depth: int, color: int, model, a, b) :
    if depth == 0:
      return eval_pos(board, model), None
    
    legal_moves = mg.gen_legal_moves(board) # iterating thru twice, can fix that later
    if not legal_moves:
        if mg.in_check(board) :
            return (-np.inf if color == 1 else np.inf), None
        return 0.0, None

    best_move = None
    best = -np.inf if color == 1 else np.inf

    for move in legal_moves:
      board.make_move(move)
      score, unused = minimax(board, depth - 1, -color, model, a, b)
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

