import pandas as pd

from diamond_ratings import get_scores

WEIGHTS = {"power": 0.5, "contact": 0.25, "speed": 0.15, "WAR": 0.10}


def players():
    return pd.DataFrame({
        "power": pd.array([90, 60, 75, 99, pd.NA], dtype="Int64"),
        "contact": pd.array([90, 60, 75, pd.NA, pd.NA], dtype="Int64"),
        "speed": pd.array([90, 60, pd.NA, pd.NA, 99], dtype="Int64"),
        "WAR": [5.0, 0.0, 2.0, 1.0, 3.0],
    })


def test_overall_follows_the_weighted_ratings(monkeypatch):
    monkeypatch.setattr(get_scores, "MIN_ATTRIBUTES", 2)

    ovr = get_scores.overall(players(), WEIGHTS)

    assert ovr[0] > ovr[2] > ovr[1]
    assert ovr.dropna().between(50, 99).all()


def test_overall_needs_enough_attributes(monkeypatch):
    monkeypatch.setattr(get_scores, "MIN_ATTRIBUTES", 2)

    ovr = get_scores.overall(players(), WEIGHTS)

    # two attributes is enough, one is not, however good it is
    assert ovr.notna().tolist() == [True, True, True, False, False]
