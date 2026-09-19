import pandas as pd
from . import batter_attributes as attr
import numpy as np
from . import data_loader


def get_player(first, last, year):
    try:
        season = data_loader.get_season_hitting(year)
    except FileNotFoundError:
        print(f"{year}: No batting data file")
        return
    player_name = f"{last}, {first}"
    
