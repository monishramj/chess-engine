import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from ml.model import ChessNet
from ml.dataset import ChessDataset

def train():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"training on: {device}")

    # batch_size=1024 is usually best for mps memory bandwidth
    batch_size = 1024
    learning_rate = 0.001
    epochs = 10

    # pin_memory=True speeds up the transfer from cpu ram to m4 unified memory
    dataset = ChessDataset("path/to/your/evals.csv")
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, pin_memory=True)

    model = ChessNet().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    model.train()

    for epoch in range(epochs):
        running_loss = 0.0
        
        for i, (inputs, labels) in enumerate(train_loader):
            # move data to m4 gpu
            inputs = inputs.to(device).float()
            labels = labels.to(device).float().unsqueeze(1)

            # the 5-step loop
            optimizer.zero_grad() 
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            
            if i % 100 == 99:
                print(f"[{epoch + 1}, {i + 1}] loss: {running_loss / 100:.5f}")
                running_loss = 0.0

    torch.save(model.state_dict(), "chess_model.pth")
    print("model saved to chess_model.pth")

if __name__ == "__main__":
    train()