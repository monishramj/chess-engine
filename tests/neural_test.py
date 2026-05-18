import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import r2_score
from scipy.stats import pearsonr

from ml.model import ChessNet
from engine.board import Board

MODEL_NAME = 'alphav2_10mil.pth' 

def validate():
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"validating on: {device}")
    
    model = ChessNet().to(device)
    model.load_state_dict(torch.load(f"ml/models/{MODEL_NAME}", map_location=device))
    model.eval()

    print("loading unseen validation data...")
    df = pd.read_csv("data/chessData.csv", skiprows=10000000, nrows=10000, names=["FEN", "Eval"])

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
    plt.title(f"{MODEL_NAME} acc: actual vs predicted (10 mil, 5 epochs, 10k samples)")
    plt.grid(True)
    # plt.savefig(f"tests/results/{MODEL_NAME}_acc.png")
    plt.show()
    
    mae = np.mean(np.abs(np.array(actuals) - np.array(predictions)))
    print(f"validation complete. mean absolute error: {mae:.4f}")
    actuals_np = np.array(actuals)
    preds_np = np.array(predictions)

    mae = np.mean(np.abs(actuals_np - preds_np))
    r2 = r2_score(actuals_np, preds_np)
    corr, _ = pearsonr(actuals_np, preds_np)

    print(f"--- validation complete ---")
    print(f"mae: {mae:.4f}")
    print(f"r2 score: {r2:.4f}")
    print(f"correlation: {corr:.4f}")

    bins = np.linspace(-1, 1, 5)
    for i in range(len(bins)-1):
        mask = (actuals_np >= bins[i]) & (actuals_np < bins[i+1])
        if np.any(mask):
            bin_mae = np.mean(np.abs(actuals_np[mask] - preds_np[mask]))
            bin_bias = np.mean(preds_np[mask] - actuals_np[mask])
            print(f"  zone [{bins[i]:.1f} to {bins[i+1]:.1f}]: mae={bin_mae:.4f}, bias={bin_bias:.4f}")

if __name__ == "__main__":
    validate()