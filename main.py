from src import pitcher_rating as pitcher
from src import data_loader
from src import batter_rating as batter
from pybaseball import playerid_reverse_lookup
import pandas as pd
from src import team_rating

def main():
    df = team_rating.team(2026)
    data_loader.save_df(df[0])
    data_loader.save_df(df[1])
    return df[0], df[1]


if __name__ == "__main__":
    main()