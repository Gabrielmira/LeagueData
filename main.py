import requests
import pandas as pd
import time

apikey = 'RGAPI-249878fc-fb6c-4856-8b58-ee9076868d6a'

match_cache = {}

def get_id_by_name(user_name, tag_line, apikey):
    player_id = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{user_name}/{tag_line}?api_key={apikey}")
    return player_id.json()["puuid"]

def get_matches(player_id, apikey):
    matches = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{player_id}/ids?type=ranked&start=0&count=20&api_key={apikey}")
    return matches.json()

def get_match_by_id(match_id, apikey):
    if match_id in match_cache:
        return match_cache[match_id]
    match_by_id = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={apikey}")
    match_data = match_by_id.json()
    if "info" in match_data and match_data["info"].get("queueId") == 420:
        match_cache[match_id] = match_data
        return match_data
    return None

def save_data_to_csv(players_data):
    df = pd.DataFrame(players_data)
    df.to_csv("matchDataIron.csv", mode='a', header=not pd.io.common.file_exists('matchDataIron.csv'), index=False)

def run_process(user_name, tag_line, max_players=2000, elo="Emerald"):
    player_id = get_id_by_name(user_name, tag_line, apikey)
    matches = get_matches(player_id, apikey)
    all_players = set()
    all_players.add(player_id)
    all_matches = set()
    players_data = []
    queue = [player_id]

    requests_made = 0
    start_time = time.time()

    while queue and len(all_players) < max_players:
        if requests_made >= 20:
            elapsed = time.time() - start_time
            if elapsed < 1:
                time.sleep(1 - elapsed)
            start_time = time.time()
            requests_made = 0

        current_player = queue.pop(0)
        matches = get_matches(current_player, apikey)
        requests_made += 1

        for match_id in matches:
            if match_id in all_matches:
                continue
            all_matches.add(match_id)
            match_data = get_match_by_id(match_id, apikey)

            if match_data is None:
                continue

            if "info" not in match_data:
                continue

            for participant in match_data["info"]["participants"]:
                challenges = participant.get("challenges", {})
                player_info = {
                    "MatchId": match_id,
                    "Lane": participant.get("lane", None),
                    "DamageDealtToObjectives": participant.get("damageDealtToObjectives", None),
                    "Deaths": participant.get("deaths", None),
                    "DetectorWardsPlaced": participant.get("detectorWardsPlaced", None),
                    "DoubleKills": participant.get("doubleKills", None),
                    "GoldEarned": participant.get("goldEarned", None),
                    "GoldSpent": participant.get("goldSpent", None),
                    "Kills": participant.get("kills", None),
                    "ItemsPurchased": participant.get("itemsPurchased", None),
                    "LongestTimeSpentLiving": participant.get("longestTimeSpentLiving", None),
                    "ObjectivesStolen": participant.get("objectivesStolen", None),
                    "TeamEarlySurrendered": participant.get("teamEarlySurrendered", None),
                    "TotalDamageDealtToChampions": participant.get("totalDamageDealtToChampions", None),
                    "TotalMinionsKilled": participant.get("totalMinionsKilled", None),
                    "TotalTimeSpentDead": participant.get("totalTimeSpentDead", None),
                    "TurretKills": participant.get("turretKills", None),
                    "VisionScore": participant.get("visionScore", None),
                    "VisionWardsBoughtInGame": participant.get("visionWardsBoughtInGame", None),
                    "WardsKilled": participant.get("wardsKilled", None),
                    "WardsPlaced": participant.get("wardsPlaced", None),
                    "Win": participant.get("win", None),
                    "FirstTurretKilledTime": challenges.get("firstTurretKilledTime", None),
                    "GoldPerMinute": challenges.get("goldPerMinute", None),
                    "LaneMinionsFirst10Minutes": challenges.get("laneMinionsFirst10Minutes", None),
                    "TurretPlatesTaken": challenges.get("turretPlatesTaken", None),
                    "TotalDamageDealt": participant.get("totalDamageDealt", None),
                    "TotalHeal": participant.get("totalHeal", None),
                    "AllInPings": participant.get("allInPings", None),
                    "OnMyWayPings": participant.get("onMyWayPings", None),
                    "EnemyVisionPings": participant.get("enemyVisionPings", None),
                    "AssistMePings": participant.get("assistMePings", None),
                    "CommandPings": participant.get("commandPings", None),
                    "KillsNearEnemyTurret": challenges.get("killsNearEnemyTurret", None),
                    "MaxCsAdvantageOnLaneOpponent": challenges.get("maxCsAdvantageOnLaneOpponent", None),
                    "KillsOnOtherLanesEarlyJungleAsLaner": challenges.get("killsOnOtherLanesEarlyJungleAsLaner", None),
                    "ChampLevel": participant.get("champLevel", None),
                    "PhysicalDamageDealtToChampions": participant.get("physicalDamageDealtToChampions", None),
                    "MagicDamageDealtToChampions": participant.get("magicDamageDealtToChampions", None),
                    "TrueDamageDealtToChampions": participant.get("trueDamageDealtToChampions", None),
                    "Elo": elo
                }
                players_data.append(player_info)

                if participant["puuid"] not in all_players:
                    all_players.add(participant["puuid"])
                    queue.append(participant["puuid"])

    save_data_to_csv(players_data)

user_name = "Pomba"
tag_line = "1010"
run_process(user_name, tag_line, max_players=1000, elo="Emerald")
