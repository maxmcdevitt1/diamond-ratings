import numpy as np
import pandas as pd

from diamond_ratings.scale import to_rating


def test_ratings_stay_on_the_scale_and_keep_order():
    values = pd.Series(np.linspace(-3, 12, 500))
    ratings = to_rating(values)

    assert ratings.min() == 50
    assert ratings.max() == 99
    assert ratings.is_monotonic_increasing
    assert abs(ratings.median() - 75) <= 1


def test_lower_is_better_reverses_the_order():
    values = pd.Series([0.250, 0.300, 0.350])
    ratings = to_rating(values, higher_is_better=False)

    assert ratings[0] > ratings[1] > ratings[2]


def test_missing_values_stay_missing():
    ratings = to_rating(pd.Series([1.0, np.nan, 3.0]))

    assert pd.isna(ratings[1])
    assert ratings.notna().sum() == 2


def test_ties_share_a_rating():
    ratings = to_rating(pd.Series([1.0, 2.0, 2.0, 3.0]))

    assert ratings[1] == ratings[2]


def test_all_missing_input():
    ratings = to_rating(pd.Series([np.nan, np.nan]))

    assert ratings.isna().all()
