from pybaseball import  playerid_lookup
from pybaseball import  statcast_pitcher
from pybaseball import statcast

import pandas as pd
from pybaseball import cache
from pathlib import Path

cache.enable()

"""
Index(['pitch_type', 'game_date', 'release_speed', 'release_pos_x',
       'release_pos_z', 'player_name', 'batter', 'pitcher', 'events',
       'description', 'spin_dir', 'spin_rate_deprecated',
       'break_angle_deprecated', 'break_length_deprecated', 'zone', 'des',
       'game_type', 'stand', 'p_throws', 'home_team', 'away_team', 'type',
       'hit_location', 'bb_type', 'balls', 'strikes', 'game_year', 'pfx_x',
       'pfx_z', 'plate_x', 'plate_z', 'on_3b', 'on_2b', 'on_1b',
       'outs_when_up', 'inning', 'inning_topbot', 'hc_x', 'hc_y',
       'tfs_deprecated', 'tfs_zulu_deprecated', 'fielder_2', 'umpire', 'sv_id',
       'vx0', 'vy0', 'vz0', 'ax', 'ay', 'az', 'sz_top', 'sz_bot',
       'hit_distance_sc', 'launch_speed', 'launch_angle', 'effective_speed',
       'release_spin_rate', 'release_extension', 'game_pk', 'pitcher.1',
       'fielder_2.1', 'fielder_3', 'fielder_4', 'fielder_5', 'fielder_6',
       'fielder_7', 'fielder_8', 'fielder_9', 'release_pos_y',
       'estimated_ba_using_speedangle', 'estimated_woba_using_speedangle',
       'woba_value', 'woba_denom', 'babip_value', 'iso_value',
       'launch_speed_angle', 'at_bat_number', 'pitch_number', 'pitch_name',
       'home_score', 'away_score', 'bat_score', 'fld_score', 'post_away_score',
       'post_home_score', 'post_bat_score', 'post_fld_score',
       'if_fielding_alignment', 'of_fielding_alignment', 'spin_axis',
       'delta_home_win_exp', 'delta_run_exp'],
      dtype='object')

      YYYY-MM-DD
"""

def get_player(first, last):
    return playerid_lookup(last, first)["key_mlbam"].iloc[0]


def get_pitcher_dataframe(first, last,start, end):
    pitcher = get_player(first, last)
    print(pitcher)
    pitcher_df = statcast_pitcher(start, end, pitcher)
    pitcher_df = pd.DataFrame(pitcher_df)

    return pitcher_df

filepath = Path("/home/max/programming/python/ML/rating/data/all_pitchers.parquet")

def get_all_pitchers():
    if  Path(filepath).is_file():
        return pd.read_parquet(filepath)
        
    all_pitchers = statcast(start_dt="2026-04-01",end_dt="2026-09-14")
    df = pd.DataFrame(all_pitchers)
    df.to_parquet(filepath)
    return df

df = get_pitcher_dataframe("Chris", "Sale", "2025-04-1", "2025-10-01")

"""     
    pitchers = (
            all_pitchers[["pitcher", "player_name"]]
            .dropna(subset=["pitcher"])
            .drop_duplicates(subset=["pitcher"])
            .reset_index(drop=True)
        )

"""

""" 
WOBA CONSTANTS
2026	.317												
2025	.313												
2024	.310												
2023	.318												
2022	.310												
2021	.314												
2020	.320												
2019	.320												
2018	.315												
2017	.321												
2016	.318												
2015	.313												
2014	.310												
2013	.314												
2012	.315												
2011	.316												
2010	.321												
2009	.329												
2008	.328												
2007	.331												
2006	.332												
2005	.326												
2004	.330												
2003	.328												
2002	.326												
2001	.327												
2000	.341												
1999	.341												
1998	.331												
1997	.332												
1996	.335												
1995	.333												
1994	.333												
1993	.327												
1992	.317												
1991	.318												
1990	.319												
1989	.313												
1988	.312												
1987	.326												
1986	.320												
1985	.317												
1984	.317												
1983	.319												
"""