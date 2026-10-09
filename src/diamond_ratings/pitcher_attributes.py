import pandas as pd
import numpy as np
from .woba_weights import WOBA_WEIGHTS

def velocity(season):
    fastballs = ('SI', 'FF', 'FC')
    fb = season[season['pitch_type'].isin(fastballs)].copy()
    
    fb["category"] = "fastball"
    fb["Leage_AVG_Velo"] = fb.groupby("category")["release_speed"].transform("median").round(4)

    fb["avg velo"] = fb.groupby(["pitcher", "category"])["release_speed"].transform("median").round(4)
    fb["differential"] = (fb["avg velo"] - fb["Leage_AVG_Velo"]).round(4)
    fb["count"] = fb.groupby("pitcher")["avg velo"].transform("count")
    minimum = fb.groupby("pitcher")["count"].transform("min")
    fb=fb[minimum>100]
    
    fb = fb[["pitcher", "player_name", "pitch_type", "Leage_AVG_Velo", "avg velo", "differential"]]
    fb=fb.drop_duplicates(subset=["pitcher"])

    return fb

def movement(df):
    df = df[['pitch_type', 'game_date', 'release_speed', 
    'player_name', 'pitcher', 'pfx_x', 'pfx_z']].copy()
    
    categories = {
        "fastball": ["FF", "SI", "FC"],
        "offspeed": ["CH", "FS", "FO", "SC"],
        "breaking": ["CU", "KC", "CS", "SL", "ST", "SV"],
        "knuckle": ["KN"],
    }
    pitch_to_cat = {
        pitch: category
        for category, pitches in categories.items()
        for pitch in pitches
    }
    df["pitch_category"] = df["pitch_type"].map(pitch_to_cat)

    df["induced_magnitude"] = (np.hypot(df["pfx_x"], df["pfx_z"]) * 12)

    df["type_baseline"] = (
        df.groupby("pitch_type")["induced_magnitude"]
        .transform("mean")
    )

    df["movement_above_average"] = (
        df["induced_magnitude"] - df["type_baseline"]
    )

    df["pitch_count"] = (
        df.groupby(["pitcher"])
        ["induced_magnitude"]
        .transform("count")
    )

    df = (df.loc[df["pitch_count"] > 350])

    df = df.groupby(['pitcher', 'pitch_category'], as_index=False).agg(
        player_name=('player_name', 'first'),
        avg_movement = ('movement_above_average', 'mean')
        )

    weights = {
        "breaking": 0.60,
        "offspeed": 0.60,
        "fastball": 0.10,
        "knuckle" : 0.80
    }

    df['weights'] = df['pitch_category'].map(weights)
    df = df.dropna(subset=['avg_movement', 'weights'])

    df['movement'] = df['avg_movement'] * df['weights']
    
    df = df.groupby(['pitcher'], as_index=False).agg(
        player_name=('player_name', 'first'),
        weighted_total=('movement', 'sum'),
        total_weight=('weights', 'sum'))
    
    df['scores'] = df['weighted_total'] / df['total_weight']
    df['score_percentile'] = ((df['scores'].rank(pct=True) * 100).round())

    return df[['player_name', 'pitcher','scores', 'score_percentile']]



WOBA_EVENTS = {
    "bb": ["walk", "intent_walk"],
    "ibb": ["intent_walk"],
    "hbp": ["hit_by_pitch"],
    "1b": ["single"],
    "2b": ["double"],
    "3b": ["triple"],
    "hr": ["home_run"],
    "ab": [
        "single", "double", "triple", "home_run",
        "field_out", "strikeout", "strikeout_double_play",
        "force_out", "grounded_into_double_play",
        "field_error", "fielders_choice", "fielders_choice_out",
        "double_play", "triple_play",
    ],
    "sf": ["sac_fly", "sac_fly_double_play"],
}


def create_woba(season):
    df = season[["pitcher", "events", "game_date"]].copy()
    df["total_pitches"] = df["pitcher"].map(df.groupby("pitcher").size())
    df = df[df["total_pitches"] > 200]

    out = df.drop_duplicates(subset=["pitcher"]).copy()
    for col, events in WOBA_EVENTS.items():
        counts = df.loc[df["events"].isin(events), "pitcher"].value_counts()
        out[col] = out["pitcher"].map(counts).fillna(0).astype(int)

    return out[["pitcher", "game_date", "hbp", 'bb', 'ibb', '1b', '2b', '3b', 'hr', 'ab', 'sf', 'total_pitches']]

def calculate_woba(year, season):
    #wOBA = ((0.697 * non intentional BB) + (0.727 * HBP) + (0.855 * 1B) + (1.248 * 2B) + (1.575 * 3B) + (2.014 * HR)/ AB + BB - IBB + SF + HBP)

    df = create_woba(season).copy()
    hbp = df['hbp']
    bb = df['bb']
    ibb = df['ibb']
    single = df['1b']
    double = df['2b']
    triple = df['3b']
    hr = df['hr']
    ab = df['ab']
    sf = df['sf']
    
    weights = WOBA_WEIGHTS[year]

    df['wOBA'] = (
        ((weights['nibb']*(bb-ibb)) + (weights['hbp']*hbp) + (weights['1b']*single) +
        (weights['2b']*double) + (weights['3b']*triple) + (weights['hr']*hr)) /
        (ab + (bb - ibb)+sf+hbp)
    )
    df['wOBA_score'] = (df['wOBA'].rank(pct=True, ascending=False)*100)

    return df

def get_whif(season, min_swings=100):
    swings = ('foul_tip', 'hit_into_play',
              'foul', 'swinging_strike_blocked',
              'swinging_strike', 'bunt_foul_tip',
              'foul_bunt', 'missed_bunt')

    misses = ('swinging_strike_blocked',
              'swinging_strike', 'missed_bunt', 'foul_tip')

    counts = pd.DataFrame({
        'pitcher': season['pitcher'],
        'swings': season['description'].isin(swings),
        'misses': season['description'].isin(misses),
    }).groupby('pitcher').sum()

    counts = counts[counts['swings'] >= min_swings]
    counts['whiff_rate'] = counts['misses'] / counts['swings']

    return counts[['whiff_rate']].reset_index()

def get_control(season):
    df = season.copy()
    df = df[(df["pitch_type"] == "ALL")].copy()
    df = df.loc[df['n'] > 200]

    df['score'] = (df['inferred_in'].rank(pct=True, ascending=False)*100).round(3)

    df = df[['pitcher_id', 'score', 'n']]

    return df