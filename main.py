from pybaseball import playerid_reverse_lookup
import pandas as pd
from diamond_ratings import team_rating, data_loader


def main():
    
    scores = {}
    for i,j in data_loader.team_ids.items():
        batters, pitchers = team_rating.team(2026, j)
        rating = team_rating.team_rating(pitchers, batters)
        scores[i]=rating
    #data_loader.save_df(batters, 'batter.parquet')
    #data_loader.save_df(pitchers, 'pitcher.parquet')
    
    #return batters, pitchers, rating
    print(scores)


if __name__ == "__main__":
    main()
