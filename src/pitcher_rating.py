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

class Player():

    def __init__(self, first, last, dataframe, year):
        self.name = f'{last}, {first}'
        self.player_id = data_loader.get_player(first, last)
        self.year = year
        self.first = first
        self.last = last

        try:
                self.df = data_loader.get_season_pitching(year)
        except FileNotFoundError:
            print(f"{year}: No pitching data file")
            return
        if self.df.empty or not self.df["player_name"].eq(self.name).any():
            print(f"{year}: No data for {first} {last}")
            return

    def velocity(self):
        vdf = attr.velocity(self.df)
        vdf["velo_percentile"] = vdf["differential"].rank(pct=True) * 100
        velocity = vdf.loc[vdf["player_name"] == self.name,"velo_percentile"].iloc[0].round()
        velocity = 50+(velocity/2)

    def movement(self):
        mdf = attr.movement(self.df)
        # Get average break of all pitch categories

        movement = mdf[[
            "player_name","pitch_category",
            "mean_movement","league_avg_movement",
            "differential"]].drop_duplicates(subset=['player_name', 'pitch_category'])

        movement['movement_percentile'] = (
            movement.groupby('pitch_category')['differential'].rank(pct=True) * 100)

        movement = movement[movement['player_name'] == (self.name)]
        # Get differential of movement from league average movement

        breaking = movement.loc[movement["pitch_category"].eq("breaking"),
                "movement_percentile"].iloc[0]
        offspeed = movement.loc[movement["pitch_category"].eq("offspeed"),
                "movement_percentile"].iloc[0]
        fastball = movement.loc[movement["pitch_category"].eq("fastball"),
                "movement_percentile"].iloc[0]
            
        movement_score = (
            breaking * 0.50
            + offspeed * 0.30
            + fastball * 0.20
            ).round()
        
        return movement_score

    def control(self):
        control = attr.get_control(data_loader.get_command(self.year))
        control = control[control["pitcher"] == f'{self.first} {self.last}']

    def war(self):
        return attr.get_war(self.player_id, self.year)

    def woba(self):
        woba = attr.calculate_woba(self.year, self.df)
        player = woba[woba['player_name'] == self.name]['wOBA_score'].iloc[0]
        return player



def get_player(first, last, year):
    
    
    
    # whiff


    

    wOBA = attr.calculate_woba(first, last, year, season)
    

    wOBA_diff = (average_woba[year] - wOBA).round(4)
    
    #TODO: STANDARDIZE THESE FORMULAS
    #woba_score = np.clip(50 + 500 * wOBA_diff, 0, 100)
    
    
    #TODO: Get final score from war.
    
    war = attr.get_war(player_id, year)
    
    #player_score = round(whiff_score * 0.50 + woba_score * 0.50, 1)


    # Takes the percentile movement_score and creates a 50-100 final movement_score like video game ratings.
    #player_score = 50+(player_score/2)
    movement_score = 50+(movement_score/2)

    print(year)
    print("Velocity: ", velocity)
    print("Movement: ", movement_score)
    print("Whiff : ", whiff)
    print("Avg Whiff : ", average_whiff_rate)
    #print("wOBA : ", round(woba_score, 1))
    #print("Player : ", player_score)
    print("Command : ",control)
    print("AVG Command: ", control_avg)
    print("WAR: ", war)

def whiff(df,first, last):

    whiff_dataframe = attr.get_whif(df)
    

    whiff_dataframe["whiff_score"] = whiff_dataframe['whiff_rate'].rank(pct=True)*100

    whiff = ((whiff_dataframe[whiff_dataframe['player_name'].eq(f'{last}, {first}')]
             ['whiff_score']).iloc[0]).round(4)
    return whiff