from functools import reduce

import pandas as pd

from . import data_loader as dl
from . import pitcher_attributes as pitcher
from . import batter_attributes as batter
from .scale import to_rating

# OVR weights. 'WAR' is the player's WAR rated 50-99 within the same pool.
PITCHER_WEIGHTS = {
    'woba': 0.25,
    'whiff': 0.20,
    'WAR': 0.20,
    'control': 0.15,
    'movement': 0.10,
    'velocity': 0.10,
}
BATTER_WEIGHTS = {
    'contact': 0.30,
    'power': 0.30,
    'WAR': 0.30,
    'speed': 0.10,
}

def pitcher_ratings(year):
    """One row per pitcher. Each attribute is 50-99 against that attribute's pool."""
    season = dl.get_season_pitching(year)

    names = season.groupby('pitcher', as_index=False)['player_name'].first()
    velo = pitcher.velocity(season)[['pitcher', 'differential']]
    move = pitcher.movement(season)[['pitcher', 'scores']]
    whiff = pitcher.get_whif(season)
    woba = pitcher.calculate_woba(year, season)[['pitcher', 'wOBA']]

    try:
        control = (
            pitcher.get_control(dl.get_command(year))
            .rename(columns={'pitcher_id': 'pitcher'})[['pitcher', 'score']]
        )
    except FileNotFoundError:
        print(f"{year}: no command file, control will be missing")
        control = pd.DataFrame({'pitcher': pd.Series(dtype='int64'),
                                'score': pd.Series(dtype='float64')})

    score = reduce(
        lambda a, b: a.merge(b, on='pitcher', how='outer', validate='1:1'),
        [velo, move, whiff, woba, control],
    )
    score = score.merge(names, on='pitcher', how='left', validate='1:1')

    out = pd.DataFrame({
        'player_id': score['pitcher'],
        'name': score['player_name'],
        'year': year,
        'velocity': to_rating(score['differential']),
        'movement': to_rating(score['scores']),
        'whiff': to_rating(score['whiff_rate']),
        'woba': to_rating(score['wOBA'], higher_is_better=False),  # lower wOBA allowed is better
        'control': to_rating(score['score']),                       # already inverted in get_control
    })

    war = dl.get_war(year, is_pitcher=True, for_team=False)
    out = out.merge(_war_by_id(war), on='player_id', how='left', validate='1:1')
    out['OVR'] = overall(out, PITCHER_WEIGHTS)

    return out


def batter_ratings(year):
    """One row per batter over the PA minimum, each attribute 50-99."""
    season = dl.get_season_batting(year)

    contact = batter.get_contact(season)[['player_id', 'last_name, first_name', 'contact_score']]
    power = batter.get_power(season)[['player_id', 'power_score']]
    speed = batter.get_speed(season)[['player_id', 'speed']]

    score = reduce(
        lambda a, b: a.merge(b, on='player_id', how='outer', validate='1:1'),
        [contact, power, speed],
    )

    out = pd.DataFrame({
        'player_id': score['player_id'],
        'name': score['last_name, first_name'],
        'year': year,
        'contact': score['contact_score'],
        'power': score['power_score'],
        'speed': score['speed'],
    })

    out = out.merge(_war_by_id(batter.war(year)), on='player_id', how='left', validate='1:1')
    out['OVR'] = overall(out, BATTER_WEIGHTS)

    return out


def overall(df, weights):
    """Weighted average of the ratings a player has, put back on the 50-99 scale."""
    weights = pd.Series(weights)
    parts = df[weights.index].assign(WAR=to_rating(df['WAR'])).astype('float64')

    # a missing rating drops out and the remaining weights are rescaled
    total = parts.mul(weights).sum(axis=1)
    available = parts.notna().mul(weights).sum(axis=1)

    return to_rating(total / available)


def _war_by_id(war):
    # players the id lookup missed have no player_id and can't be matched
    war = war.dropna(subset=['player_id']).drop_duplicates(subset=['player_id'])
    return war.assign(player_id=war['player_id'].astype('int64'))[['player_id', 'WAR']]
