import pandas as pd
import numpy as np
from .woba_weights import WOBA_WEIGHTS
from . import data_loader as load



def velocity(season):
    fastballs = ('SI', 'FF', 'FC')
    fb = season[season['pitch_type'].isin(fastballs)]
    fb["category"] = "fastball"
    fb["Leage_AVG_Velo"] = fb.groupby("category")["release_speed"].transform("median").round(4)

    fb["avg velo"] = fb.groupby(["pitcher", "category"])["release_speed"].transform("median").round(4)
    fb["differential"] = (fb["avg velo"] - fb["Leage_AVG_Velo"]).round(4)
    fb["count"] = fb.groupby("player_name")["avg velo"].transform("count")
    minimum = fb.groupby("player_name")["count"].transform("min")
    #fb=fb[minimum>100]
    
    fb = fb[["player_name", "pitch_type", "Leage_AVG_Velo", "avg velo", "differential"]]
    fb=fb.drop_duplicates(subset=["player_name"])

    return fb

def movement(season):
    df = season.copy()

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


    df["induced_magnitude"] = (np.hypot(df["pfx_x"], df["pfx_z"]) * 12).round(4)

    df["mean_movement"] = df.groupby(["pitcher", "pitch_category"])["induced_magnitude"].transform("median").round(4)

    df["league_avg_movement"] = df.groupby("pitch_category")["induced_magnitude"].transform("median").round(4)

    df["count"] = df.groupby(["player_name", "pitch_type"])["induced_magnitude"].transform("count")
    minimum = df.groupby("player_name")["count"].transform("min")
    #df=df[minimum>50]
    df = df[["player_name", "pitch_category", "pitch_type", "induced_magnitude", "mean_movement", "league_avg_movement"]]
    df["differential"] = (df["mean_movement"] - df["league_avg_movement"]).round(4)
    return df



def create_woba(season):
    df = season

    count = df.groupby('player_name').size()
    df["total_pitches"] = df["player_name"].map(count)

    df = df[df['total_pitches'] > 200]


    #####   BB AND IBB
    bb = df[df['events'].isin(["intent_walk", "walk"])]
    bb[['events', 'player_name']]
    bb = (
    bb.groupby(["player_name", "events"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["walk", "intent_walk"], fill_value=0)
        .rename(columns={"walk": "BB", "intent_walk": "IBB"})
        .reset_index()
    )
    bb["bb"] = bb["BB"] + bb["IBB"]
    df["bb"] = (
        df["player_name"]
        .map(bb.set_index("player_name")["bb"])
        .fillna(0)
        .astype(int)
    )
    df["ibb"] = df["player_name"].map(bb.set_index("player_name")['IBB']).fillna(0).astype(int)

    ####    HIT BY PITCH
    hbp_df = df[df["events"] == 'hit_by_pitch']
    hbp_df = hbp_df.groupby(["player_name", "events"]).size().unstack(fill_value=0).reindex(columns=["hit_by_pitch"]).reset_index()
    
    df['hbp'] = (df["player_name"]
                 .map(hbp_df.set_index("player_name")["hit_by_pitch"])
                 .fillna(0).
                 astype(int))
    
    ####    SINGLE
    
    sdf = df[df["events"] == 'single']
    sdf = sdf.groupby(['player_name', 'events']).size().unstack(fill_value=0).reindex(columns=['single']).reset_index()
    df['1b'] = df['player_name'].map(sdf.set_index('player_name')['single']).fillna(0).astype(int)

    ####    DOUBLE
    
    ddf = df[df["events"] == 'double']
    ddf = ddf.groupby(['player_name', 'events']).size().unstack(fill_value=0).reindex(columns=['double']).reset_index()
    df['2b'] = df['player_name'].map(ddf.set_index('player_name')['double']).fillna(0).astype(int)

    ####    TRIPLE
    
    tdf = df[df["events"] == 'triple']
    tdf = tdf.groupby(['player_name', 'events']).size().unstack(fill_value=0).reindex(columns=['triple']).reset_index()
    df['3b'] = df['player_name'].map(tdf.set_index('player_name')['triple']).fillna(0).astype(int)

    ####    HR
    
    hrdf = df[df["events"] == 'home_run']
    hrdf = hrdf.groupby(['player_name', 'events']).size().unstack(fill_value=0).reindex(columns=['home_run']).reset_index()
    df['hr'] = df['player_name'].map(hrdf.set_index('player_name')['home_run']).fillna(0).astype(int)


    ####    AB
    
    ab_events = [
        "single", "double", "triple", "home_run",
        "field_out", "strikeout", "strikeout_double_play",
        "force_out", "grounded_into_double_play",
        "field_error", "fielders_choice", "fielders_choice_out",
        "double_play", "triple_play",
    ]
    abdf = df[df['events'].isin(ab_events)].groupby('player_name').size()
    df['ab'] = df['player_name'].map(abdf).fillna(0).astype(int)

    ####    SF
    
    sfdb = df[df['events'].isin(["sac_fly", "sac_fly_double_play"])].groupby('player_name').size()

    df["sf"] = (
        df["player_name"].map(sfdb).fillna(0).astype(int)
    )

    df = df.drop_duplicates(subset=["player_name"])
    df = df[["player_name", "game_date", "hbp", 'bb', 'ibb', '1b', '2b', '3b', 'hr', 'ab', 'sf']]
    return df

def calculate_woba(year, season):
    #wOBA = ((0.697 * non intentional BB) + (0.727 * HBP) + (0.855 * 1B) + (1.248 * 2B) + (1.575 * 3B) + (2.014 * HR)/ AB + BB - IBB + SF + HBP)

    df = create_woba(season).copy()
    #df=df[df['player_name'] == name]
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

def get_whif(season):
    df = season.copy()
    
    swings = ('foul_tip', 'hit_into_play', 
              'foul', 'swinging_strike_blocked',
              'swinging_strike', 'bunt_foul_tip',
              'foul_bunt','missed_bunt')

    misses = ('swinging_strike_blocked',
              'swinging_strike','missed_bunt', 'foul_tip')

    swing = df[df['description'].isin(swings)].groupby('player_name').size()
    miss = df[df['description'].isin(misses)].groupby('player_name').size()

    df['swings'] = df['player_name'].map(swing)
    df['misses'] = df['player_name'].map(miss)

    df['whiff_rate'] = (df['misses'] / df['swings'])
    whiff = df[['player_name', 'whiff_rate']].drop_duplicates().dropna()

    return whiff

def get_control(first, last, season):
    df = season.copy()
    df = df[(df["pitch_type"] == "ALL") &(df["n"] >= 200)].copy()

    df['score'] = (df['inferred_in'].rank(pct=True)*100).round(3)

    df = df[['pitcher', 'score', 'n']]

    return df

def get_war(playerid, year):
    df = load.get_fangraphs(year)
    df = df[df["xMLBAMID"] == playerid]
    war = df["WAR"].iloc[0]
    war_score = (df[df['WAR']].rank(pct=True)*100).round(3)
    return war_score