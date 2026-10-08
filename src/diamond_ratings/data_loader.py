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

BREF_TEAM_IDS = {
    "ARI": 109, "ATL": 144, "BAL": 110, "BOS": 111,
    "CHC": 112, "CHW": 145, "CIN": 113, "CLE": 114,
    "COL": 115, "DET": 116, "HOU": 117, "KCR": 118,
    "LAA": 108, "LAD": 119, "MIA": 146, "MIL": 158,
    "MIN": 142, "NYM": 121, "NYY": 147, "PHI": 143,
    "PIT": 134, "SDP": 135, "SEA": 136, "SFG": 137,
    "STL": 138, "TBR": 139, "TEX": 140, "TOR": 141,
    "WSN": 120,
    "OAK": 133,  # Earlier seasons
    "ATH": 133,  # Same franchise ID
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
    
    df = df.loc[df['status'].astype(str) != "code='RM' description='Reassigned to Minors'"]
   
    is_pitcher = (
        df["primary_position"].astype(str)
        == "code='1' name='Pitcher' type='Pitcher' abbreviation='P'"
    )
    pitchers = df.loc[is_pitcher, "id"].to_list()
    batters = df.loc[~is_pitcher, "id"].to_list()

    return pitchers, batters


def get_season_batting(year):
    # STATCAST
    oaa = pd.read_csv(data_dir/'batting_data'/'outs_above_average.csv')
    batting = pd.read_csv(data_dir/'batting_data'/'stats.csv', encoding="utf-8-sig")
    batting = batting.drop(columns=["n_outs_above_average"])

    df = batting.merge(oaa[["player_id", "year", "outs_above_average"]], how = 'left', on=['player_id', 'year'], validate='1:1')
    return df


def get_all_pitchers():
    for year in range(2021, 2027):
        if (data_dir/'pitching_data'/f'{year}.parquet').exists():
            continue
        else:
            all_pitchers = statcast(start_dt=f'{year}-03-27',end_dt=f'{year}-10-01')
            df = pd.DataFrame(all_pitchers)
            df = df[df['game_type'] == 'R']
            df.to_parquet(data_dir/'pitching_data'/f'{year}.parquet')
        
def get_season_pitching(year):
    df = pd.read_parquet(data_dir/"pitching_data"/f'{year}.parquet')
    df = df[df['game_type'] == 'R']
    return df

def get_command(year):
    try:
        y =  pd.read_csv(data_dir/'pitching_data'/f'{year}command.csv', encoding="utf-8-sig")
        df = pd.DataFrame(y)
        
    except FileNotFoundError:
        raise FileNotFoundError

    return df


def get_war(year, is_pitcher, for_team):
    if is_pitcher:
        path = (
            data_dir / "pitching_data"
            / f"{year}_bref_pitching_war.csv"
        )
    else:
        path = (
            data_dir / "batting_data"
            / f"{year}_bref_hitting_war.csv"
        )

    df = pd.read_csv(path)

    bbref_ids = df["Player-additional"].dropna().unique().tolist()
    if for_team is False:
        df = df.drop_duplicates(subset=['Player-additional'])
    df["team_id"] = df["Team"].map(BREF_TEAM_IDS).astype("Int64")

    ids = playerid_reverse_lookup(
        bbref_ids,
        key_type="bbref",
    )

    ids = ids[["key_mlbam", "key_bbref"]].rename(
        columns={
            "key_mlbam": "player_id",
            "key_bbref": "bbref_id",
        }
    )

    df["player_name"] = normalize_name(df["Player"])
    df = df.drop(columns=["Player"])

    return df.merge(
        ids,
        left_on="Player-additional",
        right_on="bbref_id",
        how="left",
        validate="m:1"
    )


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

    ids = playerid_reverse_lookup(
        df["id"].tolist(),
        key_type="mlbam",
    )

    ids = ids[["key_mlbam", "key_bbref"]].rename(
        columns={
            "key_mlbam": "id",
            "key_bbref": "bbref_id",
        }
    )

    df = df.merge(
        ids,
        on="id",
        how="left",
        validate="one_to_one",
    )

    return df[["id", "bbref_id", "name"]].rename(
        columns={
            "id": "player_id",
            "name": "player_name",
        }
    )

def load_final_df():
    batter = pd.read_parquet(data_dir/'batter.parquet')
    pitcher = pd.read_parquet(data_dir/'pitcher.parquet')

    return batter, pitcher

def save_df(df, filename):
    df.to_parquet(data_dir / filename, index=False)