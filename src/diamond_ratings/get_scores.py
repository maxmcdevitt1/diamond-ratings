from diamond_ratings import data_loader as dl
from diamond_ratings import pitcher_attributes as pitcher

def build_season_ratings(year):
    season = dl.get_season_pitching(year)
    
    velo = pitcher.velocity(season)
    movement = pitcher.movement(season)
    whiff = pitcher.get_whif(season)
    woba = pitcher.calculate_woba(year)
    control = pitcher.get_control(season)
    