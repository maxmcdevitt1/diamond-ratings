from pybaseball import  playerid_lookup, statcast, playerid_reverse_lookup
import pandas as pd
from pybaseball import cache
from pathlib import Path
from mlbstatsapi import Mlb
import re


team_ids = {
    "Arizona Diamondbacks": 109,
    "Atlanta Braves": 144,
    "Athletics": 133,
    "Baltimore Orioles": 110,
    "Boston Red Sox": 111,
    "Chicago Cubs": 112,
    "Chicago White Sox": 145,
    "Cincinnati Reds": 113,
    "Cleveland Guardians": 114,
    "Colorado Rockies": 115,
    "Detroit Tigers": 116,
    "Houston Astros": 117,
    "Kansas City Royals": 118,
    "Los Angeles Angels": 108,
    "Los Angeles Dodgers": 119,
    "Miami Marlins": 146,
    "Milwaukee Brewers": 158,
    "Minnesota Twins": 142,
    "New York Mets": 121,
    "New York Yankees": 147,
    "Philadelphia Phillies": 143,
    "Pittsburgh Pirates": 134,
    "San Diego Padres": 135,
    "San Francisco Giants": 137,
    "Seattle Mariners": 136,
    "St. Louis Cardinals": 138,
    "Tampa Bay Rays": 139,
    "Texas Rangers": 140,
    "Toronto Blue Jays": 141,
    "Washington Nationals": 120,
}
cache.enable()

root = Path(__file__).resolve().parents[2]
data_dir = root/'data'

if not data_dir.is_dir():
    raise FileNotFoundError(f"Data directory not found: {data_dir}")


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
    # STATCAST

    data = pd.read_csv(data_dir/'batting_data'/'stats.csv', encoding="utf-8-sig")
    return pd.DataFrame(data)


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


def save_df(df, filename):
    df.to_parquet(data_dir / filename)


def get_war(year, is_pitcher):
    if is_pitcher:
        df = pd.read_csv(data_dir/'pitching_data'/f'{year}_bref_pitching_war.csv')
    else:
        df = pd.read_csv(data_dir/'batting_data'/f'{year}_bref_hitting_war.csv')
    
    df['player_name'] = normalize_name(df['Player'])
    df = df.drop(columns=['Player'])

    players = get_player_map(year)

    df = df.merge(players, on='player_name', how='left')
    return df


def normalize_name(s):
    return (
        s.astype(str)
         .str.replace(r"[*#]", "", regex=True)
         .str.replace(".", "", regex=False)
         .str.strip()
         .str.lower()
    )

def get_player_map(year):
    mlb = Mlb()
    players = mlb.get_people(season=str(year))

    df = pd.DataFrame([dict(p) for p in players])

    df["name"] = (
        df["use_name"].astype(str).str.strip()
        + " "
        + df["use_last_name"].astype(str).str.strip()
    )

    df["clean_name"] = normalize_name(df["name"])

    return df[["id", "clean_name"]].rename(
        columns={
            "id": "player_id",
            "clean_name": "player_name"
        }
    )
