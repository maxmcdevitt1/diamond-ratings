import pandas as pd
from diamond_ratings import team_rating, data_loader, get_scores

YEAR = 2026


def main():
    batter_teams = []
    pitcher_teams = []

    league_batters = get_scores.batter_ratings(YEAR)
    league_pitchers = get_scores.pitcher_ratings(YEAR)
    batter_war = data_loader.get_war(YEAR, is_pitcher=False, for_team=True)
    pitcher_war = data_loader.get_war(YEAR, is_pitcher=True, for_team=True)

    for team_name, team_id in data_loader.team_ids.items():
        batters, pitchers = team_rating.team(YEAR, team_id, league_batters, league_pitchers)

        batters = batters.assign(team=team_name)
        pitchers = pitchers.assign(team=team_name)

        batter_teams.append(batters)
        pitcher_teams.append(pitchers)

    all_batters = pd.concat(batter_teams, ignore_index=True)
    all_pitchers = pd.concat(pitcher_teams, ignore_index=True)

    data_loader.save_df(all_batters, "batter.parquet")
    data_loader.save_df(all_pitchers, "pitcher.parquet")

    team_names = {team_id: name for name, team_id in data_loader.team_ids.items()}
    scores = team_rating.team_ratings(batter_war, pitcher_war)
    scores = (
        scores.assign(team=scores['team_id'].map(team_names))
        [['team', 'WAR', 'rating']]
        .sort_values('WAR', ascending=False)
        .reset_index(drop=True)
    )
    data_loader.save_df(scores, 'teams.parquet')

if __name__ == "__main__":
    main()
