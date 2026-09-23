from pybaseball import playerid_reverse_lookup
import pandas as pd
from diamond_ratings import team_rating, data_loader


def main():
    df = team_rating.team(2026)
    data_loader.save_df(df[0], 'batter.parquet')
    data_loader.save_df(df[1], 'pitcher.parquet')
    return df[0], df[1]


if __name__ == "__main__":
    main()
