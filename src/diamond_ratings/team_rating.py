from . import data_loader
from . import pitcher_rating as pitcher
from . import batter_rating as batter
import pandas as pd
from mlbstatsapi import Mlb



def team(year, team_id):
    pitcher_ids, batter_ids = data_loader.get_team(team_id, year)

    pitchers = []
    batters = []

    for player_id in pitcher_ids:
        player = data_loader.get_player_name([player_id])

        if player.empty:
            print(f"No name found for pitcher ID {player_id}")
            continue

        first = player["name_first"].iloc[0]
        last = player["name_last"].iloc[0]

        data = pitcher.Player(player_id, year)
        ratings = data.ratings()
        ratings["player_name"] = f"{first} {last}"

        pitchers.append(ratings)

    for player_id in batter_ids:
        player = data_loader.get_player_name([player_id])

        if player.empty:
            print(f"No name found for batter ID {player_id}")
            continue

        first = player["name_first"].iloc[0]
        last = player["name_last"].iloc[0]

        data = batter.Player(year, player_id)
        ratings = data.ratings()
        ratings["player_name"] = f"{first} {last}"

        batters.append(ratings)

    return (
        pd.concat(batters, ignore_index=True),
        pd.concat(pitchers, ignore_index=True),
    )
def team_rating(pitchers, batters):
    pitchers_score = pitchers['war'].median()
    batters_score = batters['WAR'].median()

    score = (pitchers_score+batters_score)/2
    return score