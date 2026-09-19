from src import pitcher_rating
from src import data_loader
def main():
    data_loader.get_all_pitchers()
    for i in range(2024, 2027):
        pitcher_rating.Player('Chris', 'Sale', data_loader.get_season_pitching(i), i)

if __name__ == "__main__":
    main()