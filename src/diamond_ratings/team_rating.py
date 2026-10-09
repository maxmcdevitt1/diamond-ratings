from . import data_loader


def team(year, team_id, batters, pitchers):
    """Filter the league-wide rating frames down to one team's roster."""
    pitcher_ids, batter_ids = data_loader.get_team(team_id, year)

    return (
        batters[batters['player_id'].isin(batter_ids)],
        pitchers[pitchers['player_id'].isin(pitcher_ids)],
    )

def team_rating(team_id, batter_war, pitcher_war):
    batters = batter_war[batter_war['team_id'] == team_id]
    pitchers = pitcher_war[pitcher_war['team_id'] == team_id]
    return (batters['WAR'].sum() + pitchers['WAR'].sum()).round(2)
