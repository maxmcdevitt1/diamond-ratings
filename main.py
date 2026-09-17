from src import pitcher_rating

def main():
    for i in range(2024, 2027):
        pitcher_rating.get_player("Chris", "Sale", i)

if __name__ == "__main__":
    main()