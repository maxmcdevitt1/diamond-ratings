from pybaseball import  playerid_lookup, statcast
import pandas as pd
from pybaseball import cache
from pathlib import Path
from mlbstatsapi import Mlb


cache.enable()

players = Mlb().get_people()


project_dir = Path(__file__).resolve().parent.parent
filepath = project_dir / "data"

def get_batting():
    data = pd.read_csv(filepath/'batting_data'/'stats.csv', encoding="utf-8-sig")
    return pd.DataFrame(data)

def get_player(first, last):
    return playerid_lookup(last, first, fuzzy=True)["key_mlbam"].iloc[0]


def get_all_pitchers():
    for year in range(2021, 2027):
        if (filepath/'pitching_data'/f'{year}.parquet').exists():
            continue
        else:
            all_pitchers = statcast(start_dt=f'{year}-03-27',end_dt=f'{year}-10-01')
            df = pd.DataFrame(all_pitchers)
            df.to_parquet(filepath/'pitching_data'/f'{year}.parquet')
        
def get_season_pitching(year):
    return pd.read_parquet(filepath/"pitching_data"/f'{year}.parquet')

def get_command(year):
    try:
        y =  pd.read_csv(filepath/'pitching_data'/f'{year}command.csv', encoding="utf-8-sig")
        df = pd.DataFrame(y)
        return(df)
    except FileNotFoundError:
        return None

def get_fangraphs(year):
    return pd.DataFrame(pd.read_csv(filepath/'fangraphs'/f'fg_pitching_{year}.csv', encoding="utf-8-sig"))
