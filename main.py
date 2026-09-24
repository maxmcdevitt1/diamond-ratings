import pandas as pd
from diamond_ratings import team_rating, data_loader


def main():
    scores = {}
    batter_teams = []
    pitcher_teams = []

    for team_name, team_id in data_loader.team_ids.items():
        batters, pitchers = team_rating.team(2026, team_id)

        scores[team_name] = team_rating.team_rating(pitchers, batters)

        batters = batters.assign(team=team_name, team_id=team_id)
        pitchers = pitchers.assign(team=team_name, team_id=team_id)

        batter_teams.append(batters)
        pitcher_teams.append(pitchers)

    all_batters = pd.concat(batter_teams, ignore_index=True)
    all_pitchers = pd.concat(pitcher_teams, ignore_index=True)

    data_loader.save_df(all_batters, "batter.parquet")
    data_loader.save_df(all_pitchers, "pitcher.parquet")

    scores = (
        pd.DataFrame(
            scores.items(),
            columns=["team", "rating"],
        )
        .sort_values("rating", ascending=False)
        .reset_index(drop=True)
    )    
    return scores


if __name__ == "__main__":
    main()
