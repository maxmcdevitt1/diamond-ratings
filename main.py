from src import pitcher_rating as pitcher
from src import data_loader
from src import batter_rating as batter
from pybaseball import playerid_reverse_lookup
import pandas as pd


def main():
    data_loader.get_all_pitchers()

    first = input("Enter player's first name: ").strip()
    last = input("Enter player's last name: ").strip()
    position = input("Enter 1 for batter, 0 for pitcher: ").strip()
    print(playerid_reverse_lookup([data_loader.get_player(first, last)]))

    if position not in {"0", "1"}:
        print("Invalid position. Enter 0 or 1.")
        return

    player_id = data_loader.get_player(first, last)
    df = []

    for year in range(2023, 2027):
        if position == "0":
            player = pitcher.Player(first, last, year)
        else:
            batting = data_loader.get_batting()

            if not batting["player_id"].eq(player_id).any():
                print(f"{year}: No data for {first} {last}")
                continue

            player = batter.Player(first, last, year, player_id)

        df.append(player.ratings())

    # Outside the loop: combine and print once.
    if df:
        results = pd.concat(df, ignore_index=True)
        print(results.to_string(index=False))
    else:
        print(f"No ratings available for {first} {last}.")


if __name__ == "__main__":
    main()