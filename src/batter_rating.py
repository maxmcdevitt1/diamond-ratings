import pandas as pd
from . import batter_attributes as attr
import numpy as np
from . import data_loader
from . import batter_attributes as attr


class Player():

    def __init__(self, first, last, year, id):
        self.name = f'{last}, {first}'
        
        self.year = year
        self.first = first
        self.last = last
        self.id = id

    def power(self):
        df = attr.get_power(self.year)
        df = df.loc[df['player_id'] == self.id]
        iso = df['iso_score'].iloc[0]

        barrel_pct = df['barrel%_score'].iloc[0]

        ev50 = df['ev50_score'].iloc[0]

        score = (iso + barrel_pct + ev50)/3

        return float((score*100).round())

    def contact(self):
        df = attr.get_contact(self.year)
        df = df.loc[df['player_id'] == self.id]

        return float(df['contact_score'].iloc[0]*100)