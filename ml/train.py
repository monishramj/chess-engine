import os
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from ml.model import ChessNet
from ml.dataset import ChessDataset, ShardDataset

def train():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f'---------training on: {device}')

    # increased batch size for preprocessed shard data
    batch_size = 4096
    learning_rate = 0.001
    epochs = 5
    num_rows = 10000000
    model_name = 'model_10mil.pth'

    shard_dir = "data/shards/"
    shard_files = [os.path.join(shard_dir, f) for f in os.listdir(shard_dir) if f.endswith('.pt')]

    model = ChessNet().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    print(f'---------starting training for {epochs} epochs...')
    print("-" * 40)

    model.train()

    for epoch in range(epochs):
        random.shuffle(shard_files)
        running_loss = 0.0
        
        for shard_idx, shard_path in enumerate(shard_files):
            print(f"--- epoch {epoch+1} | loading shard {shard_idx+1}/{len(shard_files)}: {shard_path}")
            
            dataset = ShardDataset(shard_path)
            train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

            running_loss = 0.0
            for i, (inputs, labels) in enumerate(train_loader):
                inputs = inputs.to(device)
                labels = labels.to(device).view(-1, 1)

                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item()
                if i % 100 == 99:
                    print(f"[{epoch+1}, shard {shard_idx+1}, batch {i+1}] loss: {running_loss / 100:.5f}")
                    running_loss = 0.0
            
            del dataset
            del train_loader

    torch.save(model.state_dict(), f'ml/models/{model_name}')
    print("-" * 40)
    print(f'---------model saved as {model_name}')

if __name__ == "__main__":
    train()