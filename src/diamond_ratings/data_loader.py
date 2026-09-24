from pybaseball import  playerid_lookup, statcast, playerid_reverse_lookup
import pandas as pd
from pybaseball import cache
from pathlib import Path
from mlbstatsapi import Mlb
import os

cache.enable()

root = Path(__file__).resolve().parents[2]
data_dir = root/'data'

if not data_dir.is_dir():
    raise FileNotFoundError(
        f"Data directory not found: {data_dir}"
    )
def get_all_players(year):
    players = Mlb().get_people(season=str(year))
    df = pd.DataFrame([dict(player) for player in players])
    df = df[['id', 'use_name', 'use_last_name']]
    return df

def get_team(team_id, year):
    mlb = Mlb()

    roster = mlb.get_team_roster(team_id, rosterType='40Man', season=year)

    df = pd.DataFrame([dict(player) for player in roster])

    df = df[['id', 'status', 'primary_position']]
    df = df.loc[df['status'].astype(str) == "code='A' description='Active'"]

    is_pitcher = (
        df["primary_position"].astype(str)
        == "code='1' name='Pitcher' type='Pitcher' abbreviation='P'"
    )
    pitchers = df.loc[is_pitcher, "id"].to_list()
    batters = df.loc[~is_pitcher, "id"].to_list()

    return pitchers, batters


def get_batting():
    data = pd.read_csv(data_dir/'batting_data'/'stats.csv', encoding="utf-8-sig")
    return pd.DataFrame(data)

def get_batting_war():
    data = pd.read_csv(data_dir/'batting_data'/'2026war.csv', encoding="utf-8-sig")
    return data.rename(columns={"   ": "year_ID"})
    #return pd.DataFrame(data)

    
def get_batting_year(year):
    data = pd.read_csv(data_dir/'batting_data'/f'{year}_batting.csv', encoding="utf-8-sig")
    return pd.DataFrame(data)


def get_player(first, last):
    return playerid_lookup(last, first, fuzzy=True)["key_mlbam"].iloc[0]

def get_player_name(player_id):
    return playerid_reverse_lookup(player_id)


def get_all_pitchers():
    for year in range(2021, 2027):
        if (data_dir/'pitching_data'/f'{year}.parquet').exists():
            continue
        else:
            all_pitchers = statcast(start_dt=f'{year}-03-27',end_dt=f'{year}-10-01')
            df = pd.DataFrame(all_pitchers)
            df.to_parquet(data_dir/'pitching_data'/f'{year}.parquet')
        
def get_season_pitching(year):
    return pd.read_parquet(data_dir/"pitching_data"/f'{year}.parquet')

def get_command(year):
    try:
        y =  pd.read_csv(data_dir/'pitching_data'/f'{year}command.csv', encoding="utf-8-sig")
        df = pd.DataFrame(y)
        return(df)
    except FileNotFoundError:
        return None

def get_fangraphs(year):
    return pd.DataFrame(pd.read_csv(data_dir/'fangraphs'/f'fg_pitching_{year}.csv', encoding="utf-8-sig"))

def save_df(df, filename):
    df.to_parquet(data_dir / filename)
