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

        data = pitcher.Player(player_id, year)
        ratings = data.ratings()

        pitchers.append(ratings)

    for player_id in batter_ids:
        player = data_loader.get_player_name([player_id])

        if player.empty:
            print(f"No name found for batter ID {player_id}")
            continue


        data = batter.Player(year, player_id)
        ratings = data.ratings()

        batters.append(ratings)

    return (
        pd.concat(batters, ignore_index=True),
        pd.concat(pitchers, ignore_index=True),
    )
def team_rating(pitchers, batters):
    pitchers_score = pitchers['WAR'].sum()
    batters_score = batters['WAR'].sum()

    score = pitchers_score + batters_score
    return score