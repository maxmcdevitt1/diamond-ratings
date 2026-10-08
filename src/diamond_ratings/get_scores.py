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
    speed = batter.get_speed()
    
    
    contact = [['player_id', 'last_name, first_name', 'contact_score']]
    
    power = [[]]
    
    
    score = pd.merge(contact, power, how)