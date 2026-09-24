from . import data_loader
from . import pitcher_rating as pitcher
from . import batter_rating as batter
import pandas as pd
from mlbstatsapi import Mlb



def team(year, team_id):
    data_loader.get_all_pitchers()

    batters = []
    pitchers = []

    mlb = Mlb()

    team = data_loader.get_team(team_id, year)

    for i in team[0]:
        player = data_loader.get_player_name([i])
        if player.empty:
            print(f"No name found for batter ID {i}")
            continue
        first = player['name_first'].iloc[0]
        last = player['name_last'].iloc[0]

        data = pitcher.Player(i, first.capitalize(), last.capitalize(), year)
        pitchers.append(data.ratings())


    for i in team[1]:
        player = data_loader.get_player_name([i])
        if player.empty:
            print(f"No name found for batter ID {i}")
            continue
        first = player['name_first'].iloc[0]
        last = player['name_last'].iloc[0]

        player = batter.Player(first.capitalize(), last.capitalize(), year, i)

        batters.append(player.ratings())

    return pd.concat(batters, ignore_index=True), pd.concat(pitchers, ignore_index=True)

def team_rating(pitchers, batters):
    pitchers_score = pitchers['war'].median()
    batters_score = batters['WAR'].median()

    score = (pitchers_score+batters_score)/2
    return score