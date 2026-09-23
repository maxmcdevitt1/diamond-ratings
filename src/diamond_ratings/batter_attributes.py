import pandas as pd
import numpy as np
from . import data_loader
from .woba_weights import WOBA_WEIGHTS

def get_power(year):
    # EV50
    # Barrel%
    # ISO
    df = data_loader.get_batting()
    df = df.loc[df['year'] == year].copy()
    
    df = df.rename(columns={"avg_best_speed": "ev50", "barrel_batted_rate":"barrel%", "isolated_power":'iso'})

    df = df[['last_name, first_name', 'player_id', 'year', 'ev50', 'iso', 'barrel%']]

    df['ev50_score'] = (df['ev50'].rank(pct=True)).round(3)
    df['barrel%_score'] = (df['barrel%'].rank(pct=True)).round(3)
    df['iso_score'] = (df['iso'].rank(pct=True)).round(3)

    return df

def get_contact(year):
    df = data_loader.get_batting()
    df = df.loc[df['year'] == year].copy()
    df['contact_product'] = (df['iz_contact_percent'] * df['oz_contact_percent'])

    df['hit_measure'] = (df['batting_avg'] + df['xba']) / 2
    df['hit_score'] = df['hit_measure'].rank(pct=True) * 100

    df['bat_control_score'] = (df['contact_product'].rank(pct=True) * 100)

    df['contact'] = (0.75 * df['hit_score'] + 0.25 * df['bat_control_score']).round(2)

    df['contact_score'] = df['contact'].rank(pct=True).round(2)

    df = df[['last_name, first_name', 'year', 'player_id', 'contact_score', 
             'batting_avg', 'bat_control_score', 'hit_score', 'hit_measure']]

    return df


def get_war():
    df = data_loader.get_batting_war().copy()

    df["year_ID"] = pd.to_numeric(df["year_ID"], errors="coerce")
    df["WAR"] = pd.to_numeric(df["WAR"], errors="coerce")

    df = df.loc[df["year_ID"] > 2016].copy()
    df["war_score"] = df.groupby("year_ID")["WAR"].rank(pct=True)

    return df
