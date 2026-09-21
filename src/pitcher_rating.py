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

        return velocity

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
        movement_score = 50+(movement_score/2)

        return movement_score

    def control(self):
        control = attr.get_control(self.first, self.last,data_loader.get_command(self.year))
        control = control[control["pitcher"] == f'{self.first} {self.last}']
        # Returns percentile

        return 50 + (control['score'].iloc[0]/2)
    
    def war(self):
        # Returns percentile
        
        return 50+( attr.get_war(self.player_id, self.year)/2 )

    def woba(self):
        woba = attr.calculate_woba(self.year, self.df)
        player = woba[woba['player_name'] == self.name]['wOBA_score'].iloc[0]
        return 50 + (player/2)

    def get_whiff(self):
        whiff = attr.get_whif(self.df)
        whiff['score'] = whiff['whiff_rate'].rank(pct=True)
        score =  (whiff[whiff['player_name'] == self.name]['score']).iloc[0]
        score = (score * 100).round(4)
        return 50 + (score/2)
    
    def ratings(self):
        return {
            "Year": self.year,
            "movement": self.movement(),
            "velocity": self.velocity(),
            "control": self.control(),
            "war": self.war(),
            "woba": self.woba(),
            "whiff": self.get_whiff(),
        }