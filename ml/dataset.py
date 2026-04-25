from engine.board import Board
import numpy as np
import pandas as pd
import torch

class ChessDataset(torch.utils.data.Dataset):

    # https://www.kaggle.com/datasets/ronakbadhe/chess-evaluations
    def __init__(self, file) :
        self.data = pd.read_csv(file, nrows=100000)

    def __len__(self) :
        return len(self.data)
    
    def __getitem__(self, idx) :
        fen = self.data.iloc[idx, 0]
        raw_score = str(self.data.iloc[idx, 1])
        b = Board(str(fen))

        label = 0
        if '#' in raw_score :
            label = 1.0 if '-' not in raw_score else -1.0
        else :
            label = torch.tanh(torch.tensor(float(raw_score) / 400.0))

        base_tensor = b.board_to_tensor()
        turn = np.full((1, 8, 8), b.color, dtype=np.float32)
        final_tensor = np.concatenate([base_tensor, turn], axis=0)


        return final_tensor, label