from datetime import date, timedelta
from types import SimpleNamespace

import pandas as pd

from diamond_ratings import data_loader


def pitches(day):
    return pd.DataFrame({
        "game_date": [str(day)] * 2,
        "game_pk": [day.toordinal()] * 2,
        "at_bat_number": [1, 1],
        "pitch_number": [1, 2],
        "game_type": ["R", "S"],
    })


def test_only_the_missing_days_of_a_season_are_downloaded(tmp_path, monkeypatch):
    start, end = date(2021, 4, 1), date(2021, 4, 10)
    (tmp_path / "pitching_data").mkdir()
    path = tmp_path / "pitching_data" / "2021.parquet"
    have = [date(2021, 4, 3), date(2021, 4, 4)]
    pd.concat([pitches(day) for day in have]).query("game_type == 'R'").to_parquet(path)

    season = SimpleNamespace(
        regular_season_start_date=str(start), regular_season_end_date=str(end)
    )
    requests = []

    def fake_statcast(start_dt, end_dt):
        requests.append((start_dt, end_dt))
        days = pd.date_range(start_dt, end_dt).date
        return pd.concat([pitches(day) for day in days], ignore_index=True)

    monkeypatch.setattr(data_loader, "data_dir", tmp_path)
    monkeypatch.setattr(data_loader, "Mlb", lambda: SimpleNamespace(get_season=lambda year: season))
    monkeypatch.setattr(data_loader, "statcast", fake_statcast)

    data_loader.get_all_pitchers([2021])

    assert requests == [("2021-04-01", "2021-04-02"), ("2021-04-05", "2021-04-10")]
    saved = pd.read_parquet(path)
    assert (saved["game_type"] == "R").all()
    assert not saved.duplicated().any()
    days = pd.to_datetime(saved["game_date"]).dt.date
    assert sorted(days.unique()) == [start + timedelta(days=n) for n in range(10)]

    requests.clear()
    data_loader.get_all_pitchers([2021])

    assert requests == []  # the file already covers the season
