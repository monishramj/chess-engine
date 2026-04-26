import numpy as np
import pandas as pd
import torch
import os
import math
from multiprocessing import Pool, cpu_count

from engine.board import Board

def process_row(row_data):
    fen, raw_score = row_data
    raw_score = str(raw_score).strip()
    b = Board(str(fen))

    val = 0
    if '#' in raw_score :
        val = 1.0 if '-' not in raw_score else -1.0
    else :
        try:
            val = math.tanh(float(raw_score) / 400.0)
        except ValueError:
            val = 0.0

    label = torch.tensor([val], dtype=torch.float32)
    base_tensor = b.board_to_tensor()
    turn = torch.full((1, 8, 8), float(b.color), dtype=torch.float32)
    final_tensor = torch.cat((base_tensor, turn), dim=0)

    return final_tensor, label

def preprocess(csv_path, output_dir, rows_per_shard=1000000, total_rows=None):
    
    print(f"--- starting parallel pre-processing: {csv_path}")
    os.makedirs(output_dir, exist_ok=True)

    num_workers = 10 
    print(f"--- using {num_workers} cpu workers")
    limit_display = f"{total_rows:,}" if total_rows is not None else "all"

    chunk_size = 50000
    shard_count = 0
    current_inputs = []
    current_labels = []
    rows_processed = 0

    with Pool(num_workers) as pool:
        reader = pd.read_csv(csv_path, chunksize=chunk_size, nrows=total_rows)
        
        for chunk in reader:
            data = list(zip(chunk['FEN'], chunk['Evaluation']))
            
            for result in pool.imap(process_row, data, chunksize=1000):
                
                board_tensor, label = result
                current_inputs.append(board_tensor)
                current_labels.append(label)
                rows_processed += 1

                if len(current_inputs) >= rows_per_shard:
                    save_shard(output_dir, shard_count, current_inputs, current_labels)
                    shard_count += 1
                    current_inputs = []
                    current_labels = []
                    print(f"--- status: {rows_processed:,} / {limit_display} rows complete")

        if current_inputs:
            save_shard(output_dir, shard_count, current_inputs, current_labels)

    limit = total_rows if total_rows else "all"
    print(f"--- status: {rows_processed:,} / {limit} positions complete")

def save_shard(shard_dir, count, inputs, labels):
    path = os.path.join(shard_dir, f"shard_{count}.pt")
    torch.save({
        'inputs': torch.stack(inputs),
        'labels': torch.stack(labels)
    }, path)
    print(f"--- [shard {count}] saved {len(inputs):,}.pt")

if __name__ == "__main__":
    preprocess("data/chessData.csv", "data/shards/")