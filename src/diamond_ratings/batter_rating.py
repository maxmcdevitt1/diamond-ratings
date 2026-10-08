import pandas as pd
from . import batter_attributes as attr
from pybaseball import playerid_reverse_lookup
from . import data_loader
from statistics import NormalDist


class Player():

    def __init__(self, year, player_id):
        player = playerid_reverse_lookup([player_id])
        if player.empty:
            self.name = "unknown"

        else:
            self.name = (
                    f"{player['name_first'].iloc[0]} "
                    f"{player['name_last'].iloc[0]}"
                )
    

        self.year = year
        self.player_id = player_id
        self.df = data_loader.get_season_batting(year)


    def power(self):
        df = attr.get_power(self.df)

        df = df.loc[df['player_id'] == self.player_id]
        if df.empty:
            return None
        iso = df['iso_score'].iloc[0]

        barrel_pct = df['barrel%_score'].iloc[0]

        ev50 = df['ev50_score'].iloc[0]

        score = (iso + barrel_pct + ev50)/3
        
        return float((score * 100).round())

    def contact(self):
        df = attr.get_contact(self.df)

        df = df.loc[df['player_id'] == self.player_id, 'contact_score'].dropna()
        
        if df.empty:
            return None
        
        return round(float(df.iloc[0] * 100))
    
    def war(self):
        df = data_loader.get_war(self.year, is_pitcher=False, for_team=False)
        
        df = df.drop_duplicates(subset=['player_id'])
        percentile = df["WAR"].rank(pct=True).clip(0.001, 0.999)

        df = df[df['player_id'] == self.player_id]

        # Keeps '2TM and combined season war
        if df.empty:
            return None, None
        
        war = df['WAR'].iloc[0]

        normal = NormalDist()
        z = percentile.map(normal.inv_cdf, na_action="ignore")
        df["OVR"] = ((75 + 10 * z).clip(50, 99).round().astype("Int64"))
        ovr = df['OVR'].iloc[0]
        
        return float(war), float(ovr)

    def speed(self):
        speed = attr.get_speed(self.df)
        speed = speed.loc[speed['player_id'] == self.player_id, speed].dropna()
        if speed.empty:
            return None

        return float(round(speed.iloc[0] * 100))

    #def fielding(self):


    def ratings(self):
        war, ovr = self.war()

        data = {
            "year" : self.year,
            "player_id":self.player_id,
            "player_name":self.name,
            "Power": self.power(),
            "Contact": self.contact(),
            'OVR': ovr,
            'WAR':war,
            'speed':self.speed()
                }
        
        return pd.DataFrame([data])