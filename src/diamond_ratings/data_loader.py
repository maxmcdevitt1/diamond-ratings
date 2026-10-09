from datetime import date, timedelta

from pybaseball import statcast, playerid_reverse_lookup
import pandas as pd
from pybaseball import cache
from pathlib import Path
from mlbstatsapi import Mlb


team_ids = {
    "Arizona Diamondbacks": 109,
    "Atlanta Braves": 144,
    "Oakland Athletics": 133,
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

FIRST_SEASON = 2021

root = Path(__file__).resolve().parents[2]
data_dir = root/'data'

if not data_dir.is_dir():
    raise FileNotFoundError(f"Data directory not found: {data_dir}")


def get_team(team_id, year):
    mlb = Mlb()

    roster = mlb.get_team_roster(team_id, rosterType='40Man', season=year)

    pitchers, batters = [], []
    for player in roster:
        if player.status.code == 'RM':  # reassigned to minors
            continue
        position = player.primary_position.code
        # two-way players ('Y') pitch and hit, so they go in both lists
        if position in ('1', 'Y'):
            pitchers.append(player.id)
        if position != '1':
            batters.append(player.id)

    return pitchers, batters


def get_season_batting(year):
    # STATCAST
    oaa = pd.read_csv(data_dir/'batting_data'/'outs_above_average.csv')
    batting = pd.read_csv(data_dir/'batting_data'/'stats.csv', encoding="utf-8-sig")
    batting = batting.drop(columns=["n_outs_above_average"])

    df = batting.merge(oaa[["player_id", "year", "outs_above_average"]], how = 'left', on=['player_id', 'year'], validate='1:1')
    df = df[df['year'] == year]
    return df


def download_statcast(start, end):
    df = statcast(start_dt=str(start), end_dt=str(end))
    if df.empty:
        return df
    return df[df['game_type'] == 'R']


def get_all_pitchers(years=None):
    """Download each Statcast season, or the days an existing file is missing."""
    mlb = Mlb()
    yesterday = date.today() - timedelta(days=1)  # today's games may still be in progress
    if years is None:
        years = range(FIRST_SEASON, date.today().year + 1)

    for year in years:
        path = data_dir/'pitching_data'/f'{year}.parquet'
        season = mlb.get_season(year)
        start = date.fromisoformat(season.regular_season_start_date)
        end = min(date.fromisoformat(season.regular_season_end_date), yesterday)

        if not path.exists():
            if start <= end:
                download_statcast(start, end).to_parquet(path)
            continue

        have = pd.to_datetime(pd.read_parquet(path, columns=['game_date'])['game_date']).dt.date
        gaps = [
            (start, have.min() - timedelta(days=1)),
            (have.max() + timedelta(days=1), end),
        ]
        new = [download_statcast(first, last) for first, last in gaps if first <= last]
        new = [df for df in new if not df.empty]
        if not new:
            continue

        df = pd.concat([pd.read_parquet(path), *new], ignore_index=True)
        df = df.sort_values(
            ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'], ascending=False
        )
        df.to_parquet(path, index=False)


def get_season_pitching(year):
    df = pd.read_parquet(data_dir/"pitching_data"/f'{year}.parquet')
    df = df[df['game_type'] == 'R']
    return df

def get_command(year):
    return pd.read_csv(data_dir/'pitching_data'/f'{year}command.csv', encoding="utf-8-sig")


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

    return df.merge(
        ids,
        left_on="Player-additional",
        right_on="bbref_id",
        how="left",
        validate="m:1"
    )


def save_df(df, filename):
    df.to_parquet(data_dir / filename, index=False)