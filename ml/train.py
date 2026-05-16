import os
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torch.nn.functional as F
from ml.model import ChessNet
from ml.dataset import ChessDataset, ShardDataset

def weighted_mse_loss(inputs, targets) :
    weights = 1.0 + torch.abs(targets) * 2.0 
    loss = (inputs - targets) ** 2
    return torch.mean(weights * loss)

def train() :
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f'---------training on: {device}')

    # increased batch size for preprocessed shard data
    batch_size = 256
    learning_rate = 0.00001
    epochs = 5

    # alpha: added weighted mse loss 
    model_name = 'alphav2_10mil.pth'

    shard_dir = "data/shards/"
    shard_files = [os.path.join(shard_dir, f) for f in os.listdir(shard_dir) if f.endswith('.pt')]

    random.shuffle(shard_files)
    train_shards = shard_files[:10]
    validate_shards = shard_files[10:]

    model = ChessNet().to(device)
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    print(f'---------starting training for {epochs} epochs...')
    print("-" * 40)

    model.train()

    
    max_loss = float('inf')

    for epoch in range(epochs) :
        
        running_loss = 0.0

        for shard_idx, shard_path in enumerate(train_shards):
            print(f"--- epoch {epoch+1} | loading shard {shard_idx+1}/{len(train_shards)}: {shard_path}")
            
            dataset = ShardDataset(shard_path)
            train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=2)

            running_loss = 0.0
            for i, (inputs, labels) in enumerate(train_loader):
                inputs = inputs.to(device)
                labels = labels.to(device).view(-1, 1)

                optimizer.zero_grad(set_to_none=False)
                outputs = model(inputs)
                loss = F.mse_loss(outputs, labels)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
                optimizer.step()

                running_loss += loss.item()
                # if i % 50 == 0:
                #     time.sleep(0.02)
                if i % 100 == 99:
                    print(f"[{epoch+1}, shard {shard_idx+1}, batch {i+1}] loss: {running_loss / 100:.5f}")
                    running_loss = 0.0
            
            
            del dataset, train_loader
        
        model.eval()

        val_loss = 0.0
        val_batches = 0

        with torch.no_grad():
            for shard_path in validate_shards:
                dataset = ShardDataset(shard_path)
                val_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=2)
                
                for inputs, labels in val_loader:
                    inputs = inputs.to(device)
                    labels = labels.to(device).view(-1, 1)
                    outputs = model(inputs)
                    loss = F.mse_loss(outputs, labels)
                    val_loss += loss.item()
                    val_batches += 1
                
                del dataset, val_loader

        avg_val_loss = val_loss / val_batches
        print(f"--- epoch {epoch+1} val loss: {avg_val_loss:.5f}")

        if avg_val_loss < max_loss:
            max_loss = avg_val_loss
            torch.save(model.state_dict(), f'ml/models/{model_name}')
            print(f"--- new best model saved")

        scheduler.step()
        model.train()

    print("-" * 40)
    print(f'---------model saved as {model_name}')

if __name__ == "__main__":
    train()