import pandas as pd
from . import batter_attributes as attr
from . import batter_attributes as attr
from pybaseball import playerid_reverse_lookup

class Player():

    def __init__(self, year, id):
        self.name = playerid_reverse_lookup([id])
        
        self.year = year
        self.id = id


    def power(self):
        df = attr.get_power(self.year)

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
        
        df = attr.get_war(self.year)

        df = df[df['year '] == self.year]
        
        war = df[['mlb_ID']=='player_id', 'WAR']
        
        if df.empty:
            return None
        if war.empty:
            return None
        
        return float(((df['war_score'].iloc[0]) * 100).round(2))

    def ratings(self):
        data = {
            "year":self.year,
            "player_name":self.name,
            "batter":self.id,
            "Power": self.power(),
            "Contact": self.contact(),
            'WAR': self.war()
                }
        
        return pd.DataFrame([data])