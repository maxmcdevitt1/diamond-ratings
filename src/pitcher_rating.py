import pandas as pd
from . import pitcher_attributes as attr
import numpy as np
from . import data_loader

average_whiff_rate = {
    2016: 0.236,
    2017: 0.243,
    2018: 0.249,
    2019: 0.257,
    2020: 0.267,
    2021: 0.260,
    2022: 0.256,
    2023: 0.258,
    2024: 0.253,
    2025: 0.253,
    2026: 0.245
}
average_woba = {
    2016: 0.318,
    2017: 0.321,
    2018: 0.315,
    2019: 0.320,
    2020: 0.320,
    2021: 0.314,
    2022: 0.310,
    2023: 0.318,
    2024: 0.310,
    2025: 0.313,
    2026:0.317
}


def get_player(first, last, year):
    player_id = data_loader.get_player(first, last)
    
    player_name = f"{last}, {first}"

    try:
        season = data_loader.get_season_pitching(year)
        
    except FileNotFoundError:
        print(f"{year}: No pitching data file")
        return

    if season.empty or not season["player_name"].eq(player_name).any():
        print(f"{year}: No data for {first} {last}")
        return

    vdf = attr.velocity(season)
    mdf = attr.movement(season)
    whiff_dataframe = attr.get_whif(first, last, season)
    
    # whiff
    


    # Get average break of all pitch categories
    
    breaking_break = mdf[mdf["pitch_category"]=="breaking"]
    breaking_break["movement_percentile"] = breaking_break['differential'].rank(pct=True)*100
    
    velo_break = mdf[mdf["pitch_category"]=="fastball"]
    velo_break["movement_percentile"] = velo_break['differential'].rank(pct=True)*100
    
    offspeed_break = mdf[mdf["pitch_category"]=="offspeed"]
    offspeed_break["movement_percentile"] = offspeed_break['differential'].rank(pct=True)*100
    

    # Get differential of movement from league average movement
    breaking_break_diff = breaking_break.loc[breaking_break["player_name"] == f"{last}, {first}","movement_percentile"].iloc[0]
    fb_break_diff = velo_break.loc[velo_break["player_name"] == f"{last}, {first}","movement_percentile"].iloc[0]
    offspeed_break_diff = offspeed_break.loc[offspeed_break["player_name"] == f"{last}, {first}","movement_percentile"].iloc[0]


    movement_score = (
    breaking_break_diff * 0.50
    + offspeed_break_diff * 0.30
    + fb_break_diff * 0.20
    ).round()

    vdf["velo_percentile"] = vdf["differential"].rank(pct=True) * 100
    velocity = vdf.loc[vdf["player_name"] == f"{last}, {first}","velo_percentile"].iloc[0].round()


    # TODO: CREATE CONTROL SCORE
    
    control = attr.get_control(first, last, data_loader.get_command(year))[0].round(4)
    control_avg = attr.get_control(first, last, data_loader.get_command(year))[1].round(4)
    control_diff = control - control_avg

    wOBA = attr.calculate_woba(first, last, year, season)
    
    #avg_whiff = (attr.get_whif(first, last, season)[1])

    #whiff_diff = (whiff - avg_whiff)
    wOBA_diff = (average_woba[year] - wOBA).round(4)
    
    #TODO: STANDARDIZE THESE FORMULAS
    
    #whiff_score = np.clip(50 + 250 * whiff_diff, 0, 100)
    #woba_score = np.clip(50 + 500 * wOBA_diff, 0, 100)
    
    
    #TODO: Get final score from war.
    
    war = attr.get_war(player_id, year)
    
    #player_score = round(whiff_score * 0.50 + woba_score * 0.50, 1)


    # Takes the percentile movement_score and creates a 50-100 final movement_score like video game ratings.
    player_score = 50+(player_score/2)
    velocity = 50+(velocity/2)
    movement_score = 50+(movement_score/2)

    print(year)
    print("Velocity: ", velocity)
    print("Movement: ", movement_score)
    print("Whiff : ", whiff)
    print("Avg Whiff : ", avg_whiff)
    print("wOBA : ", round(woba_score, 1))
    print("Player : ", player_score)
    print("Command : ",control)
    print("AVG Command: ", control_avg)
    print("WAR: ", war)