import requests

# API Token
API_TOKEN = "6cb67a9a-eabd-4a19-896c-554f4c9df6f7"

BASE_URL = "https://koodipahkina.monad.fi/api"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

if __name__ == "__main__":
    num_games = 100
    results = []

    for i in range(num_games):
        print(f"Starting game {i + 1}...")
        try:
            game_id, status = create_game()
            play_game_improved()
            print(f"Game {i + 1} finished!\n")
        except Exception as e:
            print(f"Game {i + 1} encountered an error: {e}")
def create_game():
    """Luo uuden pelin"""
    response = requests.post(f"{BASE_URL}/game", headers=HEADERS)
    if response.status_code == 200:
        game_data = response.json()
        print(f"Game created: {game_data['gameId']}")
        return game_data["gameId"], game_data["status"]
    else:
        raise Exception(f"Failed to create a new game: {response.json()}")


def take_action(game_id, take_card):
    """Suorittaa toiminnon pelissä"""
    action_payload = {"takeCard": take_card}
    response = requests.post(
        f"{BASE_URL}/game/{game_id}/action",
        headers=HEADERS,
        json=action_payload,
    )
    if response.status_code == 200:
        return response.json()["status"]
    else:
        raise Exception(f"Action failed: {response.json()}")


def calculate_points(player):
    """Laskee pelaajan pisteet"""
    points = 0
    for series in player["cards"]:
        points += min(series) if series else 0
    return points - player["money"]


def decide_action(status):
    """Päättää seuraavan siirron"""
    current_card = status["card"]
    current_money = status["money"]
    player = status["players"][0]

    # Ota kortti jos kolikoita ei ole
    if player["money"] == 0:
        return True

    # Panosta jos kortti täydentää kättä
    for series in player["cards"]:
        if current_card - 1 in series or current_card + 1 in series:
            return False

    # Ota kortti jos kolikoita on kertynyt paljon
    return current_money > 3


def play_game():
    """Pelaa pelin loppuun asti."""
    game_id, status = create_game()
    print(f"Game {game_id} started!")

    while not status.get("finished", True):  # Varmistaa että peli on loppunut
        current_card = status.get("card")
        current_money = status.get("money")

        if current_card is None or current_money is None:
            print("Unexpected status format:", status)
            break

        take_card = decide_action(status)
        status = take_action(game_id, take_card)
        print(f"Turn played. Current card: {current_card}, Coins on card: {current_money}")

    # Laske lopulliset pisteet
    if "players" in status:
        final_scores = [
            {"name": player["name"], "score": calculate_points(player)}
            for player in status["players"]
        ]
        final_scores.sort(key=lambda x: x["score"])
        print("\nGame finished! Final scores:")
        for score in final_scores:
            print(f"{score['name']}: {score['score']} points")
    else:
        print("Unexpected end of game status:", status)


if __name__ == "__main__":
    play_game()
