from flask import Flask, render_template, jsonify, request
from src.data.transfermarkt_client import TransferMarktClient, format_player_data
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  
import http.client
import json
import urllib.parse
import time 
from deep_translator import GoogleTranslator
from datetime import datetime
from groq import Groq


app = Flask(__name__)





transfermarkt_client = TransferMarktClient()  
groq_client = Groq(api_key="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")  


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search')
def search_players():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    try:
        if query.isdigit():
            player_data = transfermarkt_client.get_player_info(query)
            if player_data:
                return jsonify([{
                    "id": query,
                    "name": player_data["basic_info"]["data"]["player"]["name"]
                }])
        else:
            conn = http.client.HTTPSConnection("transfermarket.p.rapidapi.com")
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'x-rapidapi-key': "28b6a5c47dmshdf1a30051f36441p157d9djsn622a7422135c",
                'x-rapidapi-host': "transfermarket.p.rapidapi.com"
            }
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    conn.request("GET", f"/search/quick-search?query={query}&domain=de", headers=headers)
                    response = conn.getresponse()
                    data = response.read()
                    
                    if data:
                        search_data = json.loads(data.decode('utf-8'))
                        if search_data and 'players' in search_data:
                            player = search_data['players'][0]
                            return jsonify([{
                                "id": player['id'],
                                "name": player['name']
                            }])
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(1)
                    
    except Exception as e:
        print(f"Error in search: {e}")
    return jsonify([])

@app.route('/api/player/<player_id>')
def get_player(player_id):
    try:
        conn = http.client.HTTPSConnection("transfermarket.p.rapidapi.com")
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'x-rapidapi-key': "28b6a5c47dmshdf1a30051f36441p157d9djsn622a7422135c",
            'x-rapidapi-host': "transfermarket.p.rapidapi.com"
        }
        
        
        conn.request("GET", f"/players/get-profile?id={player_id}&domain=de", headers=headers)
        profile_data = json.loads(conn.getresponse().read().decode())
        profile = profile_data.get("playerProfile", {})
        
        
        conn.request("GET", f"/players/get-market-value?id={player_id}&domain=de", headers=headers)
        market_data = json.loads(conn.getresponse().read().decode())
        
        
        conn.request("GET", f"/players/get-performance-summary?id={player_id}&domain=de", headers=headers)
        performance_data = json.loads(conn.getresponse().read().decode())

        
        conn.request("GET", f"/players/get-transfer-history?id={player_id}&domain=de", headers=headers)
        transfer_history = json.loads(conn.getresponse().read().decode())

        
        conn.request("GET", f"/players/get-achievements?id={player_id}&domain=de", headers=headers)
        achievements_data = json.loads(conn.getresponse().read().decode())

        
        height_m = float(profile.get("height", "0").replace(",", "."))
        height_inches = height_m * 39.37
        feet = int(height_inches // 12)
        inches = round(height_inches % 12)
        height_imperial = f"{feet}'{inches}\""

        
        translator = GoogleTranslator(source='auto', target='en')
        foot = translator.translate(profile.get("foot", "Unknown"))
        position = translator.translate(profile.get("playerMainPosition", "Unknown"))
        birthplace = translator.translate(profile.get("birthplaceCountry", "Unknown"))
        agent = translator.translate(profile.get("agent", "Unknown"))

        
        plot_url = transfermarkt_client.plot_market_value_history(market_data)

        
        performance_stats = {}
        competition_info = "No competition data available"
        if performance_data and 'competitionPerformanceSummery' in performance_data:
            comp_data = performance_data['competitionPerformanceSummery'][0]
            perf = comp_data['performance']
            
            current_year = datetime.now().year
            season = f"{str(current_year-1)[2:]}/{str(current_year)[2:]}"
            
            competition_name = translator.translate(comp_data['competition']['name'])
            competition_info = f"{competition_name} - {season}"
            
            performance_stats = {
        'Appearances': perf.get('matches', '0'),
        'Goals': perf.get('goals', '0'),
        'Assists': perf.get('assists', '0'),
        'Minutes Played': perf.get('minutesPlayed', '0'),
        'Goals per Match': perf.get('goalsPerMatch', '0'),
        'Minutes per Goal': perf.get('minutesPerGoal', '0'),
        'Yellow Cards': perf.get('yellowCards', '0'),
        'Red Cards': perf.get('redCards', '0'),
        'Substituted On': perf.get('substitutedOn', '0'),
        'Substituted Off': perf.get('substitutedOff', '0'),
        'Penalties': perf.get('penalty', '0')
    }


        
        transfers = []
        if transfer_history.get('transfers'):
            for transfer in transfer_history['transfers']:
                transfers.append({
                    'date': transfer.get('date', ''),
                    'from': translator.translate(transfer.get('from', {}).get('name', '')),
                    'to': translator.translate(transfer.get('to', {}).get('name', '')),
                    'fee': transfer.get('fee', {}).get('amount', 'Free Transfer')
                })

        
        achievements = []
        if achievements_data.get('achievements'):
            for achievement in achievements_data['achievements']:
                translated_title = translator.translate(achievement.get('title', ''))
                translated_competition = translator.translate(achievement.get('competition', {}).get('name', ''))
                achievements.append({
                    'title': translated_title,
                    'season': achievement.get('season', ''),
                    'competition': translated_competition
                })

        return jsonify({
            "player_data": {
                "name": profile.get("playerName", "Unknown"),
                "club": profile.get("club", "Unknown"),
                "competition_info": competition_info,
                "age": f"{profile.get('age', 'Unknown')} years",
                "nationality": birthplace,
                "date_of_birth": profile.get("dateOfBirth", "Unknown"),
                "height": height_imperial,
                "foot": foot,
                "position": position,
                "shirt_number": profile.get("playerShirtNumber", "Unknown"),
                "contract_until": profile.get("contractExpiryDate", "Unknown"),
                "market_value": f"€{profile.get('marketValue', '0')}M",
                "agent": agent,
                "player_image": profile.get("playerImage", "")
            },
            "plot_url": plot_url,
            "stats": performance_stats,
            "transfer_history": transfers,
            "achievements": achievements
        })

    except Exception as e:
        print(f"Error fetching player: {e}")
        return jsonify({"error": "Failed to fetch player data"}), 500


@app.route('/api/predictions/<player_id>')
def get_predictions(player_id):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'x-rapidapi-key': "28b6a5c47dmshdf1a30051f36441p157d9djsn622a7422135c",
            'x-rapidapi-host': "transfermarket.p.rapidapi.com"
        }
        
        profile = fetch_api_data(f"/players/get-profile?id={player_id}&domain=de", headers)
        market_value = fetch_api_data(f"/players/get-market-value?id={player_id}&domain=de", headers)
        
        if not profile.get('playerProfile'):
            return jsonify({"error": "Player not found"}), 404

        prompt = f"""
        Analyze transfer possibilities only:
        Player: {profile['playerProfile']['playerName']}
        Age: {profile['playerProfile']['age']}
        Position: {profile['playerProfile']['playerMainPosition']}
        Current Club: {profile['playerProfile']['club']}
        Contract Until: {profile['playerProfile']['contractExpiryDate']}

        Provide exactly three transfer predictions in this format:
        - **[Club Name]** - [Probability]% ([Brief Reasoning])

        AND

        Contract Extension: [Probability]% ([Brief Reasoning])

        
        """

        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a football transfer expert. Provide only transfer predictions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )

        return jsonify({"predictions": completion.choices[0].message.content})
    except Exception as e:
       print(f"Error generating predictions: {e}")
       return jsonify({"error": "Failed to generate predictions"}), 500












        



        




































        

        



    
@app.route('/api/future-value/<player_id>')
def calculate_future_value(player_id):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'x-rapidapi-key': "28b6a5c47dmshdf1a30051f36441p157d9djsn622a7422135c",
            'x-rapidapi-host': "transfermarket.p.rapidapi.com"
        }
        
        
        profile = fetch_api_data(f"/players/get-profile?id={player_id}&domain=de", headers)
        market_value = fetch_api_data(f"/players/get-market-value?id={player_id}&domain=de", headers)
        performance = fetch_api_data(f"/players/get-performance-summary?id={player_id}&domain=de", headers)
        achievements = fetch_api_data(f"/players/get-achievements?id={player_id}&domain=de", headers)
        
        prompt = f"""
        Analyze the player's future market value progression:

        Current Profile:
        - Name: {profile['playerProfile'].get('playerName')}
        - Age: {profile['playerProfile'].get('age')}
        - Position: {profile['playerProfile'].get('playerMainPosition')}
        - Current Value: €{profile['playerProfile'].get('marketValue')}M

        Provide a year-by-year market value projection:

        Year 1 ({datetime.now().year + 1}):
        Value: €[X]M
        Key Factors: [Brief explanation]

        Year 2 ({datetime.now().year + 2}):
        Value: €[X]M
        Key Factors: [Brief explanation]

        Year 3 ({datetime.now().year + 3}):
        Value: €[X]M
        Key Factors: [Brief explanation]

        Year 4 ({datetime.now().year + 4}):
        Value: €[X]M
        Key Factors: [Brief explanation]

        Year 5 ({datetime.now().year + 5}):
        Value: €[X]M
        Key Factors: [Brief explanation]
        """

        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a professional football market analyst. Provide concise, data-driven predictions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )

        return jsonify({
            "future_values": completion.choices[0].message.content
        })

    except Exception as e:
        print(f"Error calculating future value: {str(e)}")
        return jsonify({"error": "Failed to calculate future value"}), 500

@app.route('/api/player/similar/<player_id>')
def get_similar_players(player_id):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'x-rapidapi-key': "28b6a5c47dmshdf1a30051f36441p157d9djsn622a7422135c",
            'x-rapidapi-host': "transfermarket.p.rapidapi.com"
        }
        
        
        profile = fetch_api_data(f"/players/get-profile?id={player_id}&domain=de", headers)
        performance = fetch_api_data(f"/players/get-performance-summary?id={player_id}&domain=de", headers)
        
        performance_metrics = {}
        if performance and 'competitionPerformanceSummery' in performance and performance['competitionPerformanceSummery']:
            performance_metrics = performance['competitionPerformanceSummery'][0]['performance']

        prompt = f"""
        Find 3 similar players to {profile['playerProfile']['playerName']} based on:
        - Playing style: {profile['playerProfile']['playerMainPosition']}
        - Age: {profile['playerProfile']['age']}
        - Performance metrics: {json.dumps(performance_metrics)}
        
        For each player provide:
        1. Name and current club
        2. Similarity score (0-100%)
        3. Key matching attributes
        4. Potential as replacement
        """
        
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a football scouting expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return jsonify({"similar_players": completion.choices[0].message.content})
    except Exception as e:
        print(f"Error in similar players: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/player/career-analysis/<player_id>')
def analyze_career_path(player_id):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'x-rapidapi-key': "28b6a5c47dmshdf1a30051f36441p157d9djsn622a7422135c",
            'x-rapidapi-host': "transfermarket.p.rapidapi.com"
        }
        
        profile = fetch_api_data(f"/players/get-profile?id={player_id}&domain=de", headers)
        performance = fetch_api_data(f"/players/get-performance-summary?id={player_id}&domain=de", headers)
        

        
        prompt = f"""
        Analyze optimal career progression for {profile['playerProfile']['playerName']}:
        1. Predict peak performance age range
        2. Suggest 3 ideal leagues for development
        3. Recommend optimal career moves for next 3 years
        4. Predict career longevity and potential retirement age
        
        Consider:
        - Current age: {profile['playerProfile']['age']}
        - Position: {profile['playerProfile']['playerMainPosition']}
        - Performance: {json.dumps(performance['competitionPerformanceSummery'][0]['performance'])}
        """
        
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a career development expert in football."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return jsonify({"career_analysis": completion.choices[0].message.content})
    except Exception as e:
        print(f"Error in career analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500


def fetch_api_data(endpoint, headers):
    conn = http.client.HTTPSConnection("transfermarket.p.rapidapi.com")
    conn.request("GET", endpoint, headers=headers)
    response = conn.getresponse()
    return json.loads(response.read().decode())
 

@app.route('/api/player/team-chemistry/<player_id>')
def analyze_team_chemistry(player_id):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'x-rapidapi-key': "28b6a5c47dmshdf1a30051f36441p157d9djsn622a7422135c",
            'x-rapidapi-host': "transfermarket.p.rapidapi.com"
        }
        
        profile = fetch_api_data(f"/players/get-profile?id={player_id}&domain=de", headers)
        performance = fetch_api_data(f"/players/get-performance-summary?id={player_id}&domain=de", headers)
        current_club = profile['playerProfile'].get('club', 'Unknown Club')
        
        # Check if performance data exists
        performance_metrics = {}
        if performance and 'competitionPerformanceSummery' in performance and performance['competitionPerformanceSummery']:
            performance_metrics = performance['competitionPerformanceSummery'][0]['performance']

        prompt = f"""
        Analyze team chemistry potential for {profile['playerProfile']['playerName']}:
        1. Playing style compatibility with current team
        2. Tactical flexibility and adaptability
        3. Leadership potential and locker room impact
        4. Communication and on-field synergy
        
        Consider:
        - Position: {profile['playerProfile']['playerMainPosition']}
        - Age: {profile['playerProfile']['age']}
        - Current club: {current_club}
        - Performance: {json.dumps(performance_metrics)}
        """
        
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a team dynamics and football tactics expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return jsonify({"team_chemistry": completion.choices[0].message.content})
    except Exception as e:
        print(f"Error in team chemistry analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("Server starting on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)
