from email.header import Header
from http.client import responses

import requests

API_TOKEN = "6cb67a9a-eabd-4a19-896c-554f4c9df6f7"
BASE_URL = "https://koodipahkina.monad.fi/api"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def create_game():
    response = requests.post(f"{BASE_URL}/game", headers = HEADERS)
    if response.status_code == 200:
        game_data = response.json()
        print(f"Game created: {game_data['gameID']}")
        return game_data["gameID"], game_data["status"]
    else:
        raise Exception(f"Failed to create a new game {response.json}")