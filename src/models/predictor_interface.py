# src/models/predictor_interface.py
from .market_predictor import PlayerFuturePredictor
from ..data.transfermarkt_client import TransferMarktClient

class PlayerPredictionInterface:
    def __init__(self):
        self.predictor = PlayerFuturePredictor()
        self.client = TransferMarktClient()
        
    def get_predictions(self, player_name):
        
            # Search for player ID using TransferMarkt API
            search_results = self.client.search_player(player_name)
            if not search_results:
                return "Player not found"
                
            player_id = search_results['data'][0]['id']  # Get first match
            
            # Get predictions
            predictions = self.predictor.predict_future(player_id)
            
            # Format output
            return self._format_predictions(predictions)
            
    def _format_predictions(self, predictions):
        output = []
        
        # Market Value Prediction
        output.append("## Future Market Value Prediction")
        output.append(f"Current Value: €{predictions['predicted_value'][0]:,.2f}M")
        output.append(f"Predicted Value (2025): €{predictions['predicted_value'][1]:,.2f}M")
        
        # Transfer Predictions
        output.append("\n## Transfer Predictions")
        for club in predictions['potential_clubs']:
            output.append(f"\nPotential Destination: {club['club']}")
            output.append(f"Transfer Probability: {club['probability']*100:.1f}%")
            output.append(f"Estimated Fee: {club['estimated_fee']}")
            output.append(f"Likely Window: {club['transfer_window']}")
            
        return "\n".join(output)

# Usage example
if __name__ == "__main__":
    predictor = PlayerPredictionInterface()
    
    while True:
        player_name = input("\nEnter player name (or 'quit' to exit): ")
        if player_name.lower() == 'quit':
            break
            
        predictions = predictor.get_predictions(player_name)
        print(predictions)
