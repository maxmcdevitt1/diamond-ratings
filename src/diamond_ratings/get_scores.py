import pandas as pd

from diamond_ratings import data_loader as dl
from diamond_ratings import pitcher_attributes as pitcher
from diamond_ratings import batter_attributes as batter

def pitcher_ratings(year):
    season = dl.get_season_pitching(year)
    
    velo = pitcher.velocity(season)
    movement = pitcher.movement(season)
    whiff = pitcher.get_whif(season)
    woba = pitcher.calculate_woba(year)
    control = pitcher.get_control(season)
    
def batter_ratings(year):
    season = dl.get_season_batting(year)
    
    contact = batter.get_contact(season)
    power = batter.get_power(season)
    speed = batter.get_speed(season)
    speed = speed[['player_id', 'speed', 'year']]    
    
    score = pd.merge(left=contact, right=power, how='outer', on=['player_id', 'year', 'last_name, first_name'], validate='1:1')
    score = score.merge(speed, how='right', on=['player_id', 'year'], validate='1:1')
    score.rename(columns={'last_name, first_name':'name', 'contact_score':'contact', 'score':'power', 'contact_product' : ''})

    return score.dropna()
    
    
    #score = score.merge(speed, how='left')