from . import data_loader
from . import pitcher_rating as pitcher
from . import batter_rating as batter
import pandas as pd
from mlbstatsapi import Mlb
from pybaseball import playerid_reverse_lookup



def team(year, team_id):
    pitcher_ids, batter_ids = data_loader.get_team(team_id, year)

    pitchers = []
    batters = []

    for player_id in pitcher_ids:

        data = pitcher.Player(player_id, year)
        ratings = data.ratings()

        pitchers.append(ratings)

    for player_id in batter_ids:
        data = batter.Player(year, player_id)
        ratings = data.ratings()

        batters.append(ratings)

    return (
        pd.concat(batters, ignore_index=True),
        pd.concat(pitchers, ignore_index=True),
    )
