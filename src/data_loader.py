from pybaseball import  playerid_lookup, statcast
import re
import pandas as pd
from pybaseball import cache
from pathlib import Path

cache.enable()

project_dir = Path(__file__).resolve().parent.parent
filepath = project_dir / "data"


def get_player(first, last):
    return playerid_lookup(last, first, fuzzy=True)["key_mlbam"].iloc[0]


def get_season_hitting(year):
    data = pd.read_csv(filepath/"pitching_data"/"stats.csv")
    return pd.DataFrame(data)


def get_all_pitchers():
    for year in range(2018, 2027):
        all_pitchers = statcast(start_dt=f'{year}-04-01',end_dt=f'{year}-10-01')
        df = pd.DataFrame(all_pitchers)
        df.to_parquet(filepath/f'{year}.parquet')
        
def get_season_pitching(year):
    return pd.read_parquet(filepath/"pitching_data"/f'{year}.parquet')

def get_command(year):
    y =  pd.read_csv(filepath/'pitching_data'/f'{year}command.csv')
    df = pd.DataFrame(y)
    return(df)

def get_fangraphs(year):
    return pd.DataFrame(pd.read_csv(\
        project_dir/'data'/'fangraphs'/f'fg_pitching_{year}.csv'))

def create_df(year):
    command = get_command(year)
    fangraphs = get_fangraphs(year)
