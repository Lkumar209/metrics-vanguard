# # main.py
# from src.data.groq_client import SportsDataClient
# from src.data.data_processor import DataProcessor
# from src.models.value_predictor import MarketValuePredictor

# # main.py
# from src.data.groq_client import SportsDataClient, format_player_data

# # main.py
# from src.data.groq_client import SportsDataClient, format_player_data

# from src.data.transfermarkt_client import TransferMarktClient, format_player_data

# def main():
#     try:
#         # Initialize the client
#         client = TransferMarktClient()
        
#         # Get player data
#         while True:
#             try:
#                 player_name = input("Enter player name (or 'quit' to exit): ")
#                 if player_name.lower() == 'quit':
#                     break
                    
#                 # Example player IDs:
#                 # Erling Haaland: 418560
#                 # Kylian Mbappé: 342229
#                 # Jude Bellingham: 581678
#                 player_id = input("Enter player ID from transfermarkt: ")
                
#                 # Fetch comprehensive player data
#                 player_data = client.get_player_info(player_id)
                
#                 if player_data:
#                     # Format and print the data
#                     formatted_output = format_player_data(player_data)
#                     print("\n" + formatted_output)
#                 else:
#                     print("Error: Unable to fetch player data")
                    
#             except ValueError as e:
#                 print(f"Invalid input: {e}")
                
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         print("\nThank you for using the Player Analytics tool!")

# if __name__ == "__main__":
#     print("Welcome to Player Analytics!")
#     print("This tool fetches player data from TransferMarkt")
#     print("You'll need the player's TransferMarkt ID (found in their profile URL)")
#     main()


from src.data.transfermarkt_client import TransferMarktClient, format_player_data
import urllib.parse
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import numpy as np
from groq import Groq
import http.client
import json

class MarketValuePredictor:
    def __init__(self):
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.gb_model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def _calculate_age(self, date_of_birth):
        """Calculate player's age from date of birth"""
        if not date_of_birth:
            return 0
        birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
        today = datetime.now()
        return today.year - birth_date.year
        
    def _get_league_level(self, player_data):
        """Get league level from player data"""
        try:
            return player_data['basic_info']['data']['club']['mainCompetition']['leagueLevel'] or 1
        except:
            return 1
            
    def _get_performance_stats(self, player_data):
        """Extract performance statistics"""
        try:
            stats = []
            for comp in player_data['performance']['competitionPerformanceSummery']:
                perf = comp['performance']
                stats.extend([
                    float(perf['goals']) / max(1, float(perf['matches'])),
                    float(perf['assists']) / max(1, float(perf['matches'])),
                    float(perf['minutesPlayed']) / max(1, float(perf['matches']))
                ])
            return sum(stats) / len(stats) if stats else 0
        except:
            return 0
            
    def _analyze_transfer_pattern(self, player_data):
        """Analyze transfer history and patterns"""
        try:
            transfers = player_data['transfer_history']['transferHistory']
            if not transfers:
                return 0
                
            total_fees = sum(
                float(t['transferFeeValue'].replace(',', '')) 
                for t in transfers 
                if t['transferFeeValue'].replace(',', '').isdigit()
            )
            avg_fee = total_fees / len(transfers) if transfers else 0
            return avg_fee / 1_000_000  # Convert to millions
        except:
            return 0
            
    def _get_contract_info(self, player_data):
        """Get contract duration and analyze terms"""
        try:
            contract_end = datetime.strptime(
                player_data['basic_info']['data']['player']['contract']['until'],
                '%Y-%m-%d'
            )
            today = datetime.now()
            years_remaining = (contract_end - today).days / 365
            return max(0, years_remaining)
        except:
            return 0
            
    def prepare_features(self, player_data):
        """Extract and prepare features for prediction"""
        raw_features = np.array([[
            self._calculate_age(player_data['basic_info']['data']['player']['dateOfBirth']),
            float(player_data['basic_info']['data']['player']['marketValue']['value']),
            self._get_league_level(player_data),
            self._get_performance_stats(player_data),
            self._analyze_transfer_pattern(player_data),
            self._get_contract_info(player_data)
        ]])
        
        # Create target values for training
        target = np.array([float(player_data['basic_info']['data']['player']['marketValue']['value'])])
        
        # Fit the models with current data
        scaled_features = self.scaler.fit_transform(raw_features)
        self.rf_model.fit(scaled_features, target)
        self.gb_model.fit(scaled_features, target)
        
        return scaled_features
    
    def _extract_extension_probability(self, ai_response):
        """Extract contract extension probability from AI response"""
        try:
            if "contract extension:" in ai_response.lower():
                prob_line = [l for l in ai_response.split('\n') if 'contract extension:' in l.lower()][0]
                return float(prob_line.split(':')[1].strip().replace('%', '')) / 100
            return 0.0
        except:
            return 0.0

        
    def predict_future_value(self, player_features, years_ahead=2):
        """Predict future market values using ensemble method"""
        scaled_features = self.scaler.transform(player_features)
        future_values = []
        
        for year in range(1, years_ahead + 1):
            # Update age for each year
            scaled_features[0][0] += 1
            
            rf_pred = self.rf_model.predict(scaled_features)
            gb_pred = self.gb_model.predict(scaled_features)
            
            # Weighted average of predictions
            ensemble_pred = (0.6 * rf_pred + 0.4 * gb_pred)
            
            # Adjust for contract length impact
            contract_remaining = scaled_features[0][5] - year
            if contract_remaining < 1:
                ensemble_pred *= 0.9  # Value drops as contract nears end
                
            future_values.append(ensemble_pred[0])
            
        return future_values


class TransferPredictor:
    def __init__(self):
        self.headers = {
            'x-rapidapi-key': "ba5997973emsh7386d0e51acaf8bp1c3576jsn827eefb5994b",
            'x-rapidapi-host': "transfermarket.p.rapidapi.com"
        }
        self.groq_client = Groq(api_key="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")
        self.model = "llama3-70b-8192"

    def get_player_data(self, player_id):
        """Gather comprehensive player data from multiple endpoints"""
        conn = http.client.HTTPSConnection("transfermarket.p.rapidapi.com")
        
        # Collect data from multiple endpoints
        endpoints = {
            'profile': f"/players/get-profile?id={player_id}&domain=de",
            'market_value': f"/players/get-market-value?id={player_id}&domain=de",
            'performance': f"/players/get-performance-summary?id={player_id}&domain=de",
            'transfer_history': f"/players/get-transfer-history?id={player_id}&domain=de",
            'achievements': f"/players/get-achievements?id={player_id}&domain=de"
        }
        
        data = {}
        for key, endpoint in endpoints.items():
            conn.request("GET", endpoint, headers=self.headers)
            response = conn.getresponse()
            data[key] = json.loads(response.read().decode("utf-8"))
            
        return data

    def get_market_context(self):
        """Get market context data"""
        conn = http.client.HTTPSConnection("transfermarket.p.rapidapi.com")
        
        # Get market context
        endpoints = {
            'valuable_clubs': "/statistic/list-most-valuable-clubs?domain=de",
            'valuable_competitions': "/statistic/list-most-valuable-competitions?domain=de",
            'transfer_rumors': "/transfers/list-rumors?competitionIds=IT1%2CGB1&sort=date_desc&domain=de",
            'market_values': "/transfers/list-market-value?offset=0&competitionIds=IT1%2CGB1&orderByLatestUpdate=true&domain=de"
        }
        
        context = {}
        for key, endpoint in endpoints.items():
            conn.request("GET", endpoint, headers=self.headers)
            response = conn.getresponse()
            context[key] = json.loads(response.read().decode("utf-8"))
            
        return context

    def create_analysis_prompt(self, player_data, market_context):
        """Create detailed prompt for Groq analysis"""
        return f"""
        Analyze potential transfer destinations for this player:
        
        Player Profile:
        {json.dumps(player_data['profile'], indent=2)}
        
        Performance:
        {json.dumps(player_data['performance'], indent=2)}
        
        Transfer History:
        {json.dumps(player_data['transfer_history'], indent=2)}
        
        Market Context:
        - Valuable Clubs: {json.dumps(market_context['valuable_clubs'], indent=2)}
        - Market Values: {json.dumps(market_context['market_values'], indent=2)}
        - Transfer Rumors: {json.dumps(market_context['transfer_rumors'], indent=2)}
        
        Provide analysis in this format:
        1. [Club Name] - [Probability]% chance, €[Fee]M, Window: [Transfer Window]
        2. [Club Name] - [Probability]% chance, €[Fee]M, Window: [Transfer Window]
        3. [Club Name] - [Probability]% chance, €[Fee]M, Window: [Transfer Window]
        
        Consider:
        - Club finances and transfer budget
        - Squad needs and playing style
        - Player's career trajectory
        - Contract situation
        - Competition level
        """

    def predict_transfer(self, player_data):
        """Predict player's next club using both TransferMarkt data and AI analysis"""
        try:
            # Extract player ID correctly
            player_id = player_data['basic_info']['data']['player']['id']
            
            # Extract relevant player information
            player_info = self._get_player_info(player_data)
            market_data = self._get_market_data(player_data)
            
            # Create prompt for Groq
            prompt = f"""
            Analyze the following player's potential transfer destinations based on this data:
            
            Player: {player_info['name']}
            Current Club: {player_info['current_club']}
            Age: {player_info['age']}
            Market Value: €{player_info['market_value']}
            Contract Until: {player_info['contract_until']}
            
            Recent Performance:
            {player_data['performance']['competitionPerformanceSummery'][0]['performance']}
            
            Market Value History:
            {market_data['market_value_history'][:5]}
            
            Transfer History:
            {market_data['transfer_history']}
            
            Based on this data, provide exactly three potential transfer destinations in this format:
            1. [Club Name] - [Probability]% chance, €[Fee]M, Window: [Transfer Window]
            2. [Club Name] - [Probability]% chance, €[Fee]M, Window: [Transfer Window]
            3. [Club Name] - [Probability]% chance, €[Fee]M, Window: [Transfer Window]
            
            Also provide: Contract Extension Probability: [X]%
            """
            
            # Get AI prediction
            completion = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a football transfer market expert analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            return self._parse_predictions(completion.choices[0].message.content)
            
        except Exception as e:
            print(f"Error in predict_transfer: {str(e)}")
            return {'potential_clubs': []}


    # def predict_transfer(self, player_id):
    #     """Predict transfers using TransferMarkt data and Groq analysis"""
    #     try:
    #         # Gather comprehensive data
    #         player_data = self.get_player_data(player_id)
    #         market_context = self.get_market_context()
            
    #         # Create analysis prompt
    #         prompt = self.create_analysis_prompt(player_data, market_context)
            
    #         # Get AI prediction
    #         completion = self.groq_client.chat.completions.create(
    #             model=self.model,
    #             messages=[
    #                 {"role": "system", "content": "You are a football transfer market expert analyst."},
    #                 {"role": "user", "content": prompt}
    #             ],
    #             temperature=0.1,
    #             max_tokens=1000
    #         )
            
    #         return self._parse_predictions(completion.choices[0].message.content)
            
    #     except Exception as e:
    #         print(f"Error in predict_transfer: {str(e)}")
    #         return {'potential_clubs': []}


def main():
    try:
        # Initialize clients
        client = TransferMarktClient()
        value_predictor = MarketValuePredictor()
        transfer_predictor = TransferPredictor()
        
        print("Welcome to Player Analytics!")
        print("This tool fetches player data from TransferMarkt and predicts transfers")
        print("\nExample player IDs:")
        print("Erling Haaland: 418560")
        print("Kylian Mbappé: 342229")
        print("Jude Bellingham: 581678")
        
        while True:
            try:
                player_name = input("\nEnter player name (or 'quit' to exit): ")
                if player_name.lower() == 'quit':
                    break
                    
                player_id = input("Enter player ID from transfermarkt: ")
                print("getting..")
                
                # Fetch comprehensive player data
                player_data = client.get_player_info(player_id)
                
                if player_data:
                    # Display current player data
                    formatted_output = format_player_data(player_data)
                    print("\n" + formatted_output)
                    
                    # Ask about predictions
                    predict = input("\nWould you like to see additional data and predictions? (y/n): ")
                    if predict.lower() == 'y':
                        # Get market value prediction
                        features = value_predictor.prepare_features(player_data)
                        future_value = value_predictor.predict_future_value(features)
                        
                        # Get transfer predictions using Groq
                        transfer_prediction = transfer_predictor.predict_transfer(player_data)
                        
                        # Print predictions
                        print("\n## Future Predictions")
                        print(f"Predicted Value 2025: €{future_value[0]:,.2f}M")
                        print("\nPotential Transfer Destinations:")
                        
                        if transfer_prediction and transfer_prediction.get('potential_clubs'):
                            for club in transfer_prediction['potential_clubs']:
                                print(f"- {club['club']}: {club['probability']*100:.1f}% probability")
                                print(f"  Estimated Fee: {club['estimated_fee']}")
                                print(f"  Likely Window: {club['transfer_window']}")
                                
                            if 'contract_extension_probability' in transfer_prediction:
                                prob = transfer_prediction['contract_extension_probability']
                                print(f"\nContract Extension Probability: {prob*100:.1f}%")
                        else:
                            print("No potential transfers predicted at this time")
                else:
                    print("Error: Unable to fetch player data")
                    
            except ValueError as e:
                print(f"Invalid input: {e}")
                
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("\nThank you for using the Player Analytics tool!")

if __name__ == "__main__":
    main()
