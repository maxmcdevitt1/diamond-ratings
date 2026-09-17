from pybaseball import  playerid_lookup
from pybaseball import  statcast_pitcher
from pybaseball import statcast

import pandas as pd
from pybaseball import cache
from pathlib import Path

cache.enable()

project_dir = Path(__file__).resolve().parent.parent
filepath = project_dir / "data"
def get_player(first, last):
    return playerid_lookup(last, first)["key_mlbam"].iloc[0]


def get_pitcher_dataframe(first, last,start, end):
    pitcher = get_player(first, last)
    print(pitcher)
    pitcher_df = statcast_pitcher(start, end, pitcher)
    pitcher_df = pd.DataFrame(pitcher_df)
    return pitcher_df

def get_all_pitchers():
    for year in range(2018, 2027):
        all_pitchers = statcast(start_dt=f'{year}-04-01',end_dt=f'{year}-10-01')
        df = pd.DataFrame(all_pitchers)
        df.to_parquet(filepath/f'{year}.parquet')
        
def get_year(year):
    return pd.read_parquet(filepath/f'{year}.parquet')

def get_command(year):
    y =  pd.read_csv(filepath/f'{year}command.csv')
    df = pd.DataFrame(y)
    return(df)