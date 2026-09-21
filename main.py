from src import pitcher_rating as pitcher
from src import data_loader
from src import batter_rating as batter

def main():
    data_loader.get_all_pitchers()
    first = input("Enter player's first name: ")
    last = input("Enter player's last name: ")
    position = input('batter or pitcher: Enter 1 for batter, 0 for pitcher: ')
    for i in range(2023, 2027):
        if position == 0:
            season = data_loader.get_season_pitching(i)

            if not season["player_name"].eq(f"{last}, {first}").any():
                print(f"{i}: No data for {first} {last}")
                continue
            
            player = pitcher.Player(first, last, i)
            scores = player.ratings()
            print(scores)
        else:
            batting = data_loader.get_batting()
            id = data_loader.get_player(first, last)
            print(id)

            if not batting["player_id"].eq(id).any():
                print(f"{i}: No data for {first} {last}")
                continue

            player = batter.Player(first, last, i, id)
            print(i)
            print("Power: ", player.power())
            print('Contact: ', player.contact())
                        
        

if __name__ == "__main__":
    main()