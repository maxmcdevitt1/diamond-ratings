from src import pitcher_rating as pitcher
from src import data_loader
def main():
    data_loader.get_all_pitchers()
    first = input("Enter player's first name: ")
    last = input("Enter player's last name: ")
    name = f'{last}, {first}'
    
    for i in range(2024, 2027):
        player = pitcher.Player(name, data_loader.get_season_pitching(i), i)
        scores = player.ratings()
        
        
        

if __name__ == "__main__":
    main()