import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Fallback to hardcoded if .env fails
HENRIK_KEY = os.getenv("HENRIK_API_KEY") or "HDEV-2a59985a-9737-4ca2-af68-cec7d0cf4742"

def get_matches(username, tagline, region="ap"):
    url = f"https://api.henrikdev.xyz/valorant/v3/matches/{region}/{username}/{tagline}"
    headers = {"Authorization": HENRIK_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

def analyze_player(username, tagline):
    print(f"\nAnalyzing {username}#{tagline}...\n")
    
    matches = get_matches(username, tagline)
    total_kills = 0
    total_deaths = 0
    total_assists = 0
    total_matches = 0

    for match in matches.get("data", []):
        for player in match["players"]["all_players"]:
            if player["name"].lower() == username.lower() and player["tag"].lower() == tagline.lower():
                stats = player["stats"]
                total_kills += stats["kills"]
                total_deaths += stats["deaths"]
                total_assists += stats["assists"]
                total_matches += 1
                print(f"Match {total_matches}: {stats['kills']}K / {stats['deaths']}D / {stats['assists']}A | Agent: {player['character']}")

    kd_ratio = round(total_kills / max(total_deaths, 1), 2)
    print(f"\n--- Overall Stats ({total_matches} matches) ---")
    print(f"Kills:   {total_kills}")
    print(f"Deaths:  {total_deaths}")
    print(f"Assists: {total_assists}")
    print(f"K/D:     {kd_ratio}")

analyze_player("Yoomi", "inn")