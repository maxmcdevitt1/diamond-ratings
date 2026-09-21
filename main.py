from src import pitcher_rating as pitcher
from src import data_loader
def main():
    data_loader.get_all_pitchers()
    first = input("Enter player's first name: ")
    last = input("Enter player's last name: ")
    #name = f'{last}, {first}'

    
    for i in range(2024, 2027):
        season = data_loader.get_season_pitching(i)
        if not season["player_name"].eq(f"{last}, {first}").any():
            print(f"{i}: No data for {first} {last}")
            continue
        player = pitcher.Player(first, last,season , i)
        scores = player.ratings()
        print(scores)
        
        
        

if __name__ == "__main__":
    main()