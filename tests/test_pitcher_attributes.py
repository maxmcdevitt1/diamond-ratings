import pandas as pd
import pytest

from diamond_ratings import pitcher_attributes as pitcher
from diamond_ratings.woba_weights import WOBA_WEIGHTS


def pitches(pitcher_id, rows):
    """Build pitch-level rows for one pitcher from (count, {column: value}) pairs."""
    frames = [pd.DataFrame([values] * count) for count, values in rows]
    return pd.concat(frames, ignore_index=True).assign(
        pitcher=pitcher_id, player_name=f"Pitcher {pitcher_id}", game_date="2026-04-01"
    )


def test_woba_counts_and_formula():
    season = pd.concat([
        pitches(1, [
            (10, {"events": "single"}),
            (4, {"events": "double"}),
            (1, {"events": "triple"}),
            (3, {"events": "home_run"}),
            (8, {"events": "walk"}),
            (2, {"events": "intent_walk"}),
            (1, {"events": "hit_by_pitch"}),
            (2, {"events": "sac_fly"}),
            (1, {"events": "sac_bunt"}),
            (30, {"events": "strikeout"}),
            (40, {"events": "field_out"}),
            (150, {"events": None}),
        ]),
        pitches(2, [(50, {"events": "strikeout"})]),  # under the pitch minimum
    ], ignore_index=True)

    result = pitcher.calculate_woba(2026, season)

    assert result["pitcher"].tolist() == [1]
    row = result.iloc[0]
    assert row["total_pitches"] == 252
    assert (row["bb"], row["ibb"], row["hbp"], row["sf"]) == (10, 2, 1, 2)
    assert (row["1b"], row["2b"], row["3b"], row["hr"]) == (10, 4, 1, 3)
    assert row["ab"] == 88  # hits, strikeouts and field outs; walks, HBP and sacrifices excluded

    w = WOBA_WEIGHTS[2026]
    expected = (
        w["nibb"] * 8 + w["hbp"] * 1 + w["1b"] * 10 + w["2b"] * 4 + w["3b"] * 1 + w["hr"] * 3
    ) / (88 + 8 + 2 + 1)
    assert row["wOBA"] == pytest.approx(expected)


def test_whiff_rate():
    season = pd.concat([
        pitches(1, [
            (30, {"description": "swinging_strike"}),
            (10, {"description": "foul_tip"}),
            (40, {"description": "foul"}),
            (40, {"description": "hit_into_play"}),
            (80, {"description": "ball"}),
            (50, {"description": "called_strike"}),
        ]),
        pitches(2, [(99, {"description": "swinging_strike"})]),  # one swing short
    ], ignore_index=True)

    result = pitcher.get_whif(season)

    assert result["pitcher"].tolist() == [1]
    assert result["whiff_rate"].iloc[0] == pytest.approx(40 / 120)


def test_velocity_is_relative_to_the_league_median():
    season = pd.concat([
        pitches(1, [(101, {"pitch_type": "FF", "release_speed": 98.0})]),
        pitches(2, [(101, {"pitch_type": "SI", "release_speed": 94.0})]),
        pitches(3, [(101, {"pitch_type": "FC", "release_speed": 90.0})]),
        pitches(4, [(100, {"pitch_type": "FF", "release_speed": 94.0})]),  # needs more than 100
        pitches(5, [(500, {"pitch_type": "SL", "release_speed": 85.0})]),  # no fastballs
    ], ignore_index=True)

    result = pitcher.velocity(season).set_index("pitcher")["differential"]

    assert sorted(result.index) == [1, 2, 3]
    assert result[1] == pytest.approx(4.0)
    assert result[2] == pytest.approx(0.0)
    assert result[3] == pytest.approx(-4.0)


def test_movement_rewards_break_above_the_pitch_type_average():
    slider = {"pitch_type": "SL", "pfx_z": 0.0, "release_speed": 85.0}
    season = pd.concat([
        pitches(1, [(400, {**slider, "pfx_x": 1.5})]),
        pitches(2, [(400, {**slider, "pfx_x": 0.5})]),
        pitches(3, [(350, {**slider, "pfx_x": 1.0})]),  # needs more than 350
    ], ignore_index=True)

    result = pitcher.movement(season).set_index("pitcher")["scores"]

    assert sorted(result.index) == [1, 2]
    assert result[1] > 0 > result[2]


def test_control_ranks_smaller_misses_higher():
    command = pd.DataFrame({
        "pitcher_id": [1, 1, 2, 3],
        "pitch_type": ["ALL", "FF", "ALL", "ALL"],
        "n": [500, 300, 500, 150],
        "inferred_in": [8.0, 7.0, 11.0, 6.0],
    })

    result = pitcher.get_control(command).set_index("pitcher_id")["score"]

    assert sorted(result.index) == [1, 2]  # pitcher 3 is under the pitch minimum
    assert result[1] > result[2]
