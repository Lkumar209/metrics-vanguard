import requests
from config.api_config import APIConfig

class FootballAPIClient:
    def __init__(self):
        self.base_url = APIConfig.API_BASE_URL
        self.headers = APIConfig.API_HEADERS

    def get_player_data(self, player_id, season):
        endpoint = f"/players"
        params = {
            "id": player_id,
            "season": season
        }
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            params=params
        )
        return response.json()

    def get_transfers(self, player_id):
        endpoint = f"/transfers"
        params = {"player": player_id}
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            params=params
        )
        return response.json()

    def get_player_statistics(self, player_id, season, league_id):
        endpoint = f"/players"
        params = {
            "id": player_id,
            "season": season,
            "league": league_id
        }
        response = requests.get(
            f"{self.base_url}{endpoint}",
            headers=self.headers,
            params=params
        )
        return response.json()
