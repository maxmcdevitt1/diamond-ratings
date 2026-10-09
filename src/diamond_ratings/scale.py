from statistics import NormalDist

_NORMAL = NormalDist()


def to_rating(values, higher_is_better=True, mean=75, sd=10, lo=50, hi=99):
    """Convert raw values to a 50-99 rating via percentile -> normal quantile."""
    pct = values.rank(pct=True, ascending=higher_is_better).clip(0.001, 0.999)  # clip avoids inv_cdf(1.0) = error
    z = pct.map(_NORMAL.inv_cdf, na_action='ignore')
    return (mean + sd * z).clip(lo, hi).round().astype('Int64')
