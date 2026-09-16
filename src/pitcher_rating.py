import pandas as pd
import pitcher_attributes as attr
import numpy as np

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
    vdf = attr.velocity()
    mdf = attr.movement()



    breaking_break = mdf[mdf["pitch_category"]=="breaking"]
    breaking_break["movement_percentile"] = breaking_break['differential'].rank(pct=True)*100
    velo_break = mdf[mdf["pitch_category"]=="fastball"]
    velo_break["movement_percentile"] = velo_break['differential'].rank(pct=True)*100
    offspeed_break = mdf[mdf["pitch_category"]=="offspeed"]
    offspeed_break["movement_percentile"] = offspeed_break['differential'].rank(pct=True)*100

    breaking_break_diff = breaking_break.loc[breaking_break["player_name"] == f"{last}, {first}","movement_percentile"].iloc[0]
    fb_break_diff = velo_break.loc[velo_break["player_name"] == f"{last}, {first}","movement_percentile"].iloc[0]
    offspeed_break_diff = offspeed_break.loc[offspeed_break["player_name"] == f"{last}, {first}","movement_percentile"].iloc[0]

    score = (
    breaking_break_diff * 0.50
    + offspeed_break_diff * 0.30
    + fb_break_diff * 0.20
    ).round()
    vdf["velo_percentile"]=vdf["differential"].rank(pct=True) * 100
    velocity = vdf.loc[vdf["player_name"] == f"{last}, {first}","velo_percentile"].iloc[0].round()
    wOBA = attr.calculate_woba(first, last, year)
    whiff = attr.get_whif(first, last)/100

    whiff_diff = (whiff - (average_whiff_rate[year])).round(4)
    wOBA_diff = (average_woba[year] - wOBA).round(4)
    whiff_score = np.clip(50 + 250 * whiff_diff, 0, 100)
    woba_score = np.clip(50 + 500 * wOBA_diff, 0, 100)
    player_score = round(
    whiff_score * 0.50 + woba_score * 0.50,
    1)
    


    print("Velocity:", velocity)
    print("Movement:", score)
    print("Whiff score:", round(whiff_score, 1))
    print("wOBA score:", round(woba_score, 1))
    print("Player score:", player_score)

    """ 
    Have the velo of break scores now need to create a 0-100 score system with the isolated era
    """
    print()
    return 0




get_player("Chris", "Sale", 2026)