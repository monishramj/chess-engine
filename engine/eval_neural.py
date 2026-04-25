import torch
from ml.model import ChessNet

class NeuralEval:

    def __init__(self, model_path = 'ml/models/new_model.pth') :
        
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.model = ChessNet().to(self.device) 
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=True) 

        self.model.load_state_dict(checkpoint)
        self.model.eval()

    def evaluate(self, board) :
        board_tensor = board.board_to_tensor().to(self.device).float().unsqueeze(0) 
        
        turn_layer = torch.full((1, 1, 8, 8), float(board.color), dtype=torch.float32).to(self.device)
        input_tensor = torch.cat([board_tensor, turn_layer], dim=1)

        with torch.no_grad():
            output = self.model(input_tensor)

        return output.item()