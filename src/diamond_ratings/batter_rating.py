import pandas as pd
from . import batter_attributes as attr
from . import batter_attributes as attr
from pybaseball import playerid_reverse_lookup
from . import data_loader

class Player():

    def __init__(self, year, id):
        self.name = playerid_reverse_lookup([id])
        
        self.year = year
        self.id = id
        self.df = data_loader.get_batting()
        self.df = self.df.loc[self.df['year'] == year]


    def power(self):
        df = attr.get_power(self, self.year, self.df)

        df = df.loc[df['player_id'] == self.id]
        if df.empty:
            return None
        iso = df['iso_score'].iloc[0]

        barrel_pct = df['barrel%_score'].iloc[0]

        ev50 = df['ev50_score'].iloc[0]

        score = (iso + barrel_pct + ev50)/3
        
        return float((score * 100).round())

    def contact(self):
        df = attr.get_contact(self.year)

        df = df.loc[df['player_id'] == self.id]
        if df.empty:
            return None
        
        return float(df['contact_score'].iloc[0] * 100)

    def war(self):
        df = data_loader.get_war(self.year, is_pitcher=False)
        df = df[df['player_id'] == self.player_id]

        # Keeps '2TM and combined season war
        
        df = df.drop_duplicates(subset=['player_id'])

        if df.empty:
            return None
        war = df['WAR'].iloc[0]
        return float(war)        

    def ratings(self):
        data = {
            "year":self.year,
            "player_name":self.name,
            "batter":self.id,
            "Power": self.power(),
            "Contact": self.contact(),
            'OVR': self.war()
                }
        
        return pd.DataFrame([data])