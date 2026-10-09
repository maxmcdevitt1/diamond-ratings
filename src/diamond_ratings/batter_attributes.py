import pandas as pd
import numpy as np
from .woba_weights import WOBA_WEIGHTS
from . import data_loader as load
from statistics import NormalDist

def get_power(df):
    # EV50
    # Barrel%
    # ISO
    df = df[df['pa'] > 200]

    df = df.rename(columns={"avg_best_speed": "ev50", "barrel_batted_rate":"barrel%", "isolated_power":'iso'})

    df = df[['last_name, first_name', 'player_id', 'year', 'ev50', 'iso', 'barrel%']]


    df['iso'] = normalize(df['iso'])
    df['barrel%'] = normalize(df['barrel%'])
    df['ev50'] = normalize(df['ev50'])

    power = (df['iso'] + df['barrel%'] + df['ev50']) / 3

    df['power_score'] = power.rank(pct=True).round(2)

    return df

def get_contact(df):

    df = df[df['pa'] > 200]

    contact = 100 - df['whiff_percent']
    
    df['contact%'] = normalize(contact)
    df['contact%_percentile'] = df['contact%'].rank(pct=True) * 100

    performance = (df['batting_avg'] + df['xba']) / 2

    df['contact_performance'] = normalize(performance)
    
    df['performance_percentile'] = (df['contact_performance'].rank(pct=True) * 100)

    df['contact'] = (
        0.75 * df['contact_performance']
        + 0.25 * df['contact%'])

    df['contact_score'] = df['contact'].rank(pct=True).round(2)

    return df[[
        'last_name, first_name', 'year', 'player_id',
         'batting_avg', 'contact_performance',
        'performance_percentile', 'contact%', 'contact%_percentile','contact','contact_score']]

def get_speed(df):
    df['speed'] = df['sprint_speed'].rank(pct=True)
    return df

def war(year):
    df = load.get_war(year, is_pitcher=False, for_team=False)
    
    df = df.drop_duplicates(subset=['player_id'])
    percentile = df["WAR"].rank(pct=True).clip(0.001, 0.999)
    
    normal = NormalDist()
    z = percentile.map(normal.inv_cdf, na_action="ignore")
    df["OVR"] = ((75 + 10 * z).clip(50, 99).round().astype("Int64"))


def normalize(values):
    spread = values.max() - values.min()

    return (values - values.min()) / spread