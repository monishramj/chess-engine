import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ml.model import ChessNet
from engine.board import Board

def validate():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"validating on: {device}")

    model = ChessNet().to(device)
    model.load_state_dict(torch.load("ml/models/model_5mil.pth", map_location=device))
    model.eval()

    print("loading unseen validation data...")
    df = pd.read_csv("data/chessData.csv", skiprows=10000000, nrows=1000, names=["FEN", "Eval"])

    actuals = []
    predictions = []

    print("running inference...")
    with torch.no_grad():
        for _, row in df.iterrows():
            fen = str(row['FEN'])
            raw_eval = str(row['Eval'])
            
            if '#' in raw_eval:
                target = 1.0 if '-' not in raw_eval else -1.0
            else:
                target = np.tanh(float(raw_eval) / 400.0)

            b = Board(fen)
            board_tensor = b.board_to_tensor().to(device).float().unsqueeze(0)
            
            
            turn_layer = torch.full((1, 1, 8, 8), float(b.color), dtype=torch.float32).to(device)
            
            input_tensor = torch.cat([board_tensor, turn_layer], dim=1)
            
            pred = model(input_tensor).item()

            actuals.append(target)
            predictions.append(pred)

    # 3. graphing
    plt.figure(figsize=(10, 6))
    plt.scatter(actuals, predictions, alpha=0.3, color='blue')
    plt.plot([-1, 1], [-1, 1], color='red', linestyle='--')
    plt.xlabel("actual stockfish eval (normalized)")
    plt.ylabel("model prediction (normalized)")
    plt.title("model accuracy: actual vs predicted (5 mil)")
    plt.grid(True)
    plt.savefig("tests/results/neural_acc_5mil.png")
    plt.show()
    
    mae = np.mean(np.abs(np.array(actuals) - np.array(predictions)))
    print(f"validation complete. mean absolute error: {mae:.4f}")

if __name__ == "__main__":
    validate()