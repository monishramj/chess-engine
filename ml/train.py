import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from ml.model import ChessNet
from ml.dataset import ChessDataset

def train():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f'---------training on: {device}')

    # batch_size=1024 is usually best for mps memory bandwidth
    batch_size = 1024
    learning_rate = 0.001
    epochs = 10
    num_rows = 1000000
    model_name = 'model_1mil.pth'

    dataset = ChessDataset("data/chessData.csv", num_rows)
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, pin_memory=False)
    print(f'---------total positions in training set: {len(dataset):,}')

    model = ChessNet().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    print(f'---------starting training for 10 epochs...')
    print("-" * 40)

    model.train()

    for epoch in range(epochs):
        running_loss = 0.0
        
        for i, (inputs, labels) in enumerate(train_loader):
            inputs = inputs.to(device).float()
            labels = labels.to(device).float().unsqueeze(1)

            optimizer.zero_grad() 
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            
            if i % 100 == 99:
                print(f"[{epoch + 1}, {i + 1}] loss: {running_loss / 100:.5f}")
                running_loss = 0.0

    torch.save(model.state_dict(), f'ml/models/{model_name}')
    print("-" * 40)
    print(f'---------model saved as {model_name}')

if __name__ == "__main__":
    train()