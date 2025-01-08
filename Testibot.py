import requests

# API Token
API_TOKEN = "6cb67a9a-eabd-4a19-896c-554f4c9df6f7"
BASE_URL = "https://koodipahkina.monad.fi/api"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}


def create_game():
    """Luo uuden pelin"""
    response = requests.post(f"{BASE_URL}/game", headers=HEADERS)
    if response.status_code == 200:
        game_data = response.json()
        return game_data["gameId"], game_data["status"]
    else:
        raise Exception(f"Failed to create a new game: {response.json()}")


def take_action(game_id, take_card):
    """Suorittaa toiminnon pelissä ja palauttaa päivitetyn tilan"""
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


def analyze_opponents(status):
    """Analysoi vastustajien mahdolliset pisteet ja kolikkotilanteen"""
    opponents = status["players"][1:]
    scores = []

    for opponent in opponents:
        opponent_score = calculate_points(opponent)
        scores.append({
            "name": opponent["name"],
            "score": opponent_score,
            "money": opponent["money"]
        })

    return sorted(scores, key=lambda x: x["score"])


def decide_action_improved(status):
    """Päätöksenteko huomioiden vastustajien tilanne"""
    current_card = status["card"]
    current_money = status["money"]
    player = status["players"][0]
    opponents = analyze_opponents(status)

    # Vastustajien keskimääräinen pistemäärä
    avg_opponent_score = sum(o["score"] for o in opponents) / len(opponents)
    bot_score = calculate_points(player)

    # Ota kortti jos kolikoita ei ole
    if player["money"] == 0:
        return True

    # Jos ero vastustajiin on jo pieni älä käytä kolikoita
    if bot_score - avg_opponent_score < 24:
        if current_card + current_money > 10:
            return True
        else:
            return False

    #panostus jos kortti täydentää sarjaa
    for series in player["cards"]:
        if current_card - 1 in series or current_card + 1 in series:
            return False

    # Otetaan kortti jos se haittaa vastustajia enemmän kuin meitä
    if any(current_card - 1 in opp["score"] or current_card + 1 in opp["score"] for opp in opponents):
        return True

    #  Panostetaan jos kolikoita on riittävästi
    return current_money > 3


def play_game_improved(results):
    """Pelaa pelin ja tallenna tulokset."""
    game_id, status = create_game()
    print(f"Game {game_id} started!")

    while not status.get("finished", True):  # Varmista että peli on loppu
        current_card = status.get("card")
        current_money = status.get("money")

        if current_card is None or current_money is None:
            print("Unexpected status format:", status)
            break

        take_card = decide_action_improved(status)
        status = take_action(game_id, take_card)
        print(f"Turn played. Current card: {current_card}, Coins on card: {current_money}")

    # Peli päättynyt laskee lopulliset pisteet
    if "players" in status:
        final_scores = [
            {"name": player["name"], "score": calculate_points(player)}
            for player in status["players"]
        ]
        final_scores.sort(key=lambda x: x["score"])
        print("\nGame finished! Final scores:")
        for score in final_scores:
            print(f"{score['name']}: {score['score']} points")

        # Tulosten tallennus
        bot_score = next(score["score"] for score in final_scores if score["name"] == "github_user_1")
        avg_opponent_score = sum(score["score"] for score in final_scores if score["name"] != "github_user_1") / (len(final_scores) - 1)
        results.append({"game_id": game_id, "bot_score": bot_score, "avg_opponent_score": avg_opponent_score})
    else:
        print("Unexpected end of game status:", status)


def analyze_results(results):
    """Analysoi useiden pelien tulokset."""
    total_bot_score = sum(result["bot_score"] for result in results)
    total_avg_opponent_score = sum(result["avg_opponent_score"] for result in results)
    print("\nResults after playing games:")
    print(f"Bot's Average Score: {total_bot_score / len(results):.2f}")
    print(f"Opponents' Average Score: {total_avg_opponent_score / len(results):.2f}")
    print(f"Average Score Difference: {(total_bot_score / len(results)) - (total_avg_opponent_score / len(results)):.2f}")


if __name__ == "__main__":
    num_games = 100  # Kuinka monta peliä pelataan
    results = []

    for i in range(num_games):
        print(f"Starting game {i + 1}...")
        try:
            play_game_improved(results)
            print(f"Game {i + 1} finished!\n")
        except Exception as e:
            print(f"Game {i + 1} encountered an error: {e}")

    analyze_results(results)
