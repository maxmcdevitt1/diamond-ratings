from types import SimpleNamespace

import pandas as pd

from diamond_ratings import data_loader, team_rating


def test_team_war_is_summed_per_club_and_rated():
    batter_war = pd.DataFrame({
        "team_id": pd.array([1, 1, 2, pd.NA, 3], dtype="Int64"),
        "WAR": [3.0, 1.5, 2.0, 9.0, 0.5],  # the NA row is a traded player's season total
    })
    pitcher_war = pd.DataFrame({
        "team_id": pd.array([1, 2, 3], dtype="Int64"),
        "WAR": [2.0, 1.0, -0.5],
    })

    result = team_rating.team_ratings(batter_war, pitcher_war).set_index("team_id")

    assert result["WAR"].to_dict() == {1: 6.5, 2: 3.0, 3: 0.0}
    assert result["rating"][1] > result["rating"][2] > result["rating"][3]


def test_team_filters_to_the_roster(monkeypatch):
    monkeypatch.setattr(data_loader, "get_team", lambda team_id, year: ([10, 30], [20, 30]))
    batters = pd.DataFrame({"player_id": [20, 30, 99]})
    pitchers = pd.DataFrame({"player_id": [10, 30, 99]})

    team_batters, team_pitchers = team_rating.team(2026, 119, batters, pitchers)

    assert team_batters["player_id"].tolist() == [20, 30]
    assert team_pitchers["player_id"].tolist() == [10, 30]


def test_roster_split_by_position(monkeypatch):
    def player(player_id, position, status="A"):
        return SimpleNamespace(
            id=player_id,
            status=SimpleNamespace(code=status),
            primary_position=SimpleNamespace(code=position),
        )

    roster = [
        player(1, "1"),               # pitcher
        player(2, "6"),               # shortstop
        player(3, "Y"),               # two-way player
        player(4, "1", status="RM"),  # reassigned to minors
        player(5, "10", status="D60"),
    ]
    fake_mlb = SimpleNamespace(get_team_roster=lambda team_id, rosterType, season: roster)
    monkeypatch.setattr(data_loader, "Mlb", lambda: fake_mlb)

    pitchers, batters = data_loader.get_team(119, 2026)

    assert pitchers == [1, 3]
    assert batters == [2, 3, 5]
