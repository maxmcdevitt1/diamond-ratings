# batter_attributes.py
import pandas as pd
from . import data_loader as load
from .scale import to_rating

MIN_PA = 200


def normalize(values):
    spread = values.max() - values.min()
    if pd.isna(spread) or spread == 0:
        return values * 0.0
    return (values - values.min()) / spread


def get_power(df):
    df = df[df['pa'] > MIN_PA].rename(columns={
        "avg_best_speed": "ev50",
        "barrel_batted_rate": "barrel%",
        "isolated_power": "iso",
    })[['last_name, first_name', 'player_id', 'year', 'ev50', 'iso', 'barrel%']].copy()

    parts = ['iso', 'barrel%', 'ev50']
    for col in parts:
        df[col] = normalize(df[col])

    power = df[parts].mean(axis=1, skipna=False)
    df['power_score'] = to_rating(power)
    return df


def get_contact(df):
    df = df[df['pa'] > MIN_PA].copy()

    df['contact%'] = normalize(100 - df['whiff_percent'])
    df['contact%_percentile'] = df['contact%'].rank(pct=True) * 100

    df['contact_performance'] = normalize((df['batting_avg'] + df['xba']) / 2)
    df['performance_percentile'] = df['contact_performance'].rank(pct=True) * 100

    df['contact'] = 0.75 * df['contact_performance'] + 0.25 * df['contact%']
    df['contact_score'] = to_rating(df['contact'])

    return df[[
        'last_name, first_name', 'year', 'player_id',
        'batting_avg', 'contact_performance', 'performance_percentile',
        'contact%', 'contact%_percentile', 'contact', 'contact_score',
    ]]


def get_speed(df):
    df = df[df['pa'] > MIN_PA].copy()
    df['speed'] = to_rating(df['sprint_speed'])
    return df


def war(year):
    df = load.get_war(year, is_pitcher=False, for_team=False)
    return df.drop_duplicates(subset=['player_id']).copy()