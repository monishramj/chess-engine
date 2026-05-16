from engine.board import Board
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

class ShardDataset(Dataset) :
    def __init__(self, shard_path):
        data = torch.load(shard_path, weights_only=True)
        self.inputs = data['inputs']
        self.labels = data['labels']

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        # no more board parsing! js return the pre-calculated tensors
        return self.inputs[idx], self.labels[idx]

class ChessDataset(Dataset) :
    # https://www.kaggle.com/datasets/ronakbadhe/chess-evaluations
    def __init__(self, num_rows, file) :
        self.data = pd.read_csv(file, nrows=num_rows)
        print('---------dataset loaded:\n', self.data.head())

    def __len__(self) :
        return len(self.data)
    
    def __getitem__(self, idx) :
        fen = self.data.iloc[idx, 0]
        raw_score = str(self.data.iloc[idx, 1])
        b = Board(str(fen))

        val = 0
        if '#' in raw_score :
            val = 1.0 if '-' not in raw_score else -1.0
        else :
            val = np.tanh(float(raw_score) / 400.0)

        label = torch.tensor(val, dtype=torch.float32)
        base_tensor = b.board_to_tensor()
        turn = torch.full((1, 8, 8), float(b.color), dtype=torch.float32)
        final_tensor = torch.cat((base_tensor, turn), dim=0)


        return final_tensor, label