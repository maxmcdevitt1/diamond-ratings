import pandas as pd

from diamond_ratings import batter_attributes as batter


def hitters():
    return pd.DataFrame({
        "last_name, first_name": ["Slugger, Sam", "Slapper, Sal", "Average, Al", "Bench, Bo"],
        "player_id": [1, 2, 3, 4],
        "year": 2026,
        "pa": [600, 600, 600, 200],
        "isolated_power": [0.300, 0.080, 0.160, 0.400],
        "barrel_batted_rate": [18.0, 2.0, 8.0, 25.0],
        "avg_best_speed": [106.0, 96.0, 100.0, 108.0],
        "batting_avg": [0.240, 0.320, 0.260, 0.350],
        "xba": [0.250, 0.310, 0.260, 0.350],
        "whiff_percent": [32.0, 10.0, 22.0, 5.0],
        "sprint_speed": [26.0, 29.5, 27.5, 31.0],
    })


def test_normalize_spans_zero_to_one():
    result = batter.normalize(pd.Series([2.0, 4.0, 6.0]))

    assert result.tolist() == [0.0, 0.5, 1.0]


def test_normalize_handles_identical_values():
    result = batter.normalize(pd.Series([3.0, 3.0]))

    assert result.tolist() == [0.0, 0.0]


def test_hitters_at_the_pa_minimum_are_left_out():
    df = hitters()

    for rated in (batter.get_power(df), batter.get_contact(df), batter.get_speed(df)):
        assert sorted(rated["player_id"]) == [1, 2, 3]


def test_power_contact_and_speed_order():
    df = hitters()

    power = batter.get_power(df).set_index("player_id")["power_score"]
    contact = batter.get_contact(df).set_index("player_id")["contact_score"]
    speed = batter.get_speed(df).set_index("player_id")["speed"]

    assert power[1] > power[3] > power[2]
    assert contact[2] > contact[3] > contact[1]
    assert speed[2] > speed[3] > speed[1]
