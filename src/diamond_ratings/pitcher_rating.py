import pandas as pd
from . import pitcher_attributes as attr
import numpy as np
from . import data_loader
from pybaseball import playerid_reverse_lookup
from statistics import NormalDist


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
    def __init__(self, player_id, year):
        self.player_id = player_id

        self.year = year
        player = playerid_reverse_lookup([player_id])

        if player.empty:
            self.name = "unknown"
        else:
            self.name = (
                f"{player['name_first'].iloc[0]} "
                f"{player['name_last'].iloc[0]}"
            )
        self.df = data_loader.get_season_pitching(year)


        if not self.df["pitcher"].eq(self.player_id).any():
            print((f"{year}: No data for {self.name}"))
            return None

    def velocity(self):
        vdf = attr.velocity(self.df)
        
        percentile = (vdf["differential"].rank(pct=True) * 100).clip(0.0001, 0.999)
        
        velocity = vdf.loc[vdf["pitcher"] == self.player_id].dropna()
        
        if velocity.empty:
            return None
        
        
        normal = NormalDist()
        z = percentile.map(normal.inv_cdf, na_action="ignore")
        vdf["velo_score"] = ((75 + 10 * z).clip(50, 99).round().astype("Int64"))
        
        return float(round(velocity.iloc[0] * 100))

    def movement(self):
        mdf = attr.movement(self.df)
        # Get average break of all pitch categories
        # Count measured pitches per player and category.

        mdf["pitch_count"] = (
            mdf.groupby(["pitcher", "pitch_category"])
            ["induced_magnitude"]
            .transform("count")
        )

        movement = (
            mdf.loc[
                mdf["pitch_count"] > 50,
                ["pitcher", "pitch_category", "mean_movement"],
            ]
            .drop_duplicates(["pitcher", "pitch_category"])
            .copy()
        )

        movement['movement_percentile'] = (
            movement.groupby('pitch_category')['mean_movement'].rank(pct=True) * 100)

        movement = movement[movement['pitcher'] == (self.player_id)]
        # Get differential of movement from league average movement
        
        weights = {
            "breaking": 0.50,
            "offspeed": 0.30,
            "fastball": 0.20,
        }

        weighted_total = 0.0
        total_weight = 0.0

        for category, weight in weights.items():
            scores = movement.loc[
                movement["pitch_category"] == category,
                "movement_percentile",
            ].dropna()

            if not scores.empty:
                weighted_total += float(scores.iloc[0]) * weight
                total_weight += weight

        if total_weight == 0:
            return None

        movement_score = round(weighted_total / total_weight)
        return float(movement_score)

    def control(self):
        control = attr.get_control(data_loader.get_command(self.year))
        if control is None:
            return
        control = control[control["pitcher_id"] == self.player_id]
        if control.empty:
            return None
        # Returns percentile

        return float(control['score'].iloc[0])
    
    def war(self):
        df = data_loader.get_war(self.year, is_pitcher=True, for_team=False)
        percentile = (df['WAR'].rank(pct=True) * 100).clip(0.001, 0.999)
        
        df = df.drop_duplicates(subset=['player_id'])

        df = df[df['player_id'] == self.player_id]

        # Keeps '2TM and combined season war
        if df.empty:
            return None, None
        
        normal = NormalDist()
        z = percentile.map(normal.inv_cdf, na_action="ignore")
        df["OVR"] = ((75 + 10 * z).clip(50, 99).round().astype("Int64"))

        war = df['WAR'].iloc[0]
        ovr = df['OVR'].iloc[0]
        return float(war), float(ovr)

    def woba(self):
        woba = attr.calculate_woba(self.year, self.df)
        scores = woba.loc[woba['pitcher'] == self.player_id, 'wOBA_score'].dropna()

        if scores.empty:
            return None
        return float(scores.iloc[0].round(2))

    def get_whiff(self):
        whiff = attr.get_whif(self.df)
        whiff['score'] = whiff['whiff_rate'].rank(pct=True)
        score = (whiff[whiff['pitcher'] == self.player_id]['score'])

        if score.empty:
            return None
        
        score = (score.iloc[0] * 100).round(4)
        return float(score)
    
    def ratings(self):
        war, ovr = self.war()

        data = {
            "year": self.year,
            "player_id":self.player_id,
            "player_name":self.name,
            "movement": self.movement(),
            "velocity": self.velocity(),
            "control": self.control(),
            'OVR':ovr,
            'WAR':war,
            "woba": self.woba(),
            "whiff": self.get_whiff(),
        }
        return pd.DataFrame([data])