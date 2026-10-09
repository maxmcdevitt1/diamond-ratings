import pandas as pd

from . import data_loader
from .scale import to_rating


def team(year, team_id, batters, pitchers):
    """Filter the league-wide rating frames down to one team's roster."""
    pitcher_ids, batter_ids = data_loader.get_team(team_id, year)

    return (
        batters[batters['player_id'].isin(batter_ids)],
        pitchers[pitchers['player_id'].isin(pitcher_ids)],
    )

def team_ratings(batter_war, pitcher_war):
    """Total WAR per team and its 50-99 rating against the other teams."""
    war = (
        pd.concat([batter_war, pitcher_war])
        .groupby('team_id')['WAR']
        .sum()
        .round(2)
        .reset_index()
    )
    war['rating'] = to_rating(war['WAR'])
    return war
