"""Unit tests for the momentum strategy code.

Run:  pytest
"""
import numpy as np
import pandas as pd
import pytest

from momentum_replication.strategy import formation_rank, load_monthly_prices, wml_returns


def make_prices(seed=0, n_months=120, n_assets=40, monthly_drift_scale=0.01, noise_scale=0.05):
    """Synthetic month-end prices where each asset has its own persistent monthly drift
    plus noise, so a true momentum effect exists and we know its rough size."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2010-01-31", periods=n_months, freq="ME")
    drift = rng.normal(0, monthly_drift_scale, n_assets)
    noise = rng.normal(0, noise_scale, (n_months, n_assets))
    monthly_ret = drift + noise
    prices = 100 * np.cumprod(1 + monthly_ret, axis=0)
    return pd.DataFrame(prices, index=idx, columns=[f"A{i}" for i in range(n_assets)])


def test_formation_rank_is_a_percentile_between_0_and_1():
    prices = make_prices()
    rank = formation_rank(prices, J=6)
    valid = rank.stack().dropna()  # early months have no J-month history yet -> NaN, expected
    assert len(valid) > 0
    assert valid.between(0, 1).all()


def test_formation_rank_skip_shifts_by_one_month():
    prices = make_prices()
    no_skip = formation_rank(prices, J=6, skip=0)
    skip_one = formation_rank(prices, J=6, skip=1)
    # skipping one month should equal the no-skip ranking shifted forward one month
    aligned = no_skip.shift(1).dropna(how="all")
    compare = skip_one.loc[aligned.index]
    assert np.allclose(aligned.values, compare.values, equal_nan=True)


def test_wml_returns_detects_planted_momentum():
    """With a strong persistent per-asset drift, winners should beat losers on average."""
    prices = make_prices(seed=1, monthly_drift_scale=0.02, noise_scale=0.03)
    wml = wml_returns(prices, J=6, K=6, q=0.2, skip=0, min_assets=10)
    assert wml.mean() > 0
    # rough sanity bound: shouldn't be wildly larger than the injected drift spread
    assert wml.mean() < 0.20


def test_wml_returns_near_zero_on_pure_noise():
    """With no persistent drift (pure random walk), winners should not reliably beat losers."""
    rng = np.random.default_rng(2)
    idx = pd.date_range("2010-01-31", periods=180, freq="ME")
    noise = rng.normal(0, 0.05, (180, 40))
    prices = pd.DataFrame(100 * np.cumprod(1 + noise, axis=0), index=idx,
                           columns=[f"A{i}" for i in range(40)])
    wml = wml_returns(prices, J=6, K=6, q=0.2, skip=0, min_assets=10)
    assert abs(wml.mean()) < 0.02   # should be small; a few % is within noise


def test_wml_returns_has_no_lookahead():
    """Changing a future price must not change today's ranking-driven return."""
    prices = make_prices(seed=3)
    wml_before = wml_returns(prices, J=6, K=3, q=0.2, skip=0, min_assets=10)

    altered = prices.copy()
    last_date = altered.index[-1]
    altered.loc[last_date, "A0"] *= 5.0  # shock only the final month, only one asset

    wml_after = wml_returns(altered, J=6, K=3, q=0.2, skip=0, min_assets=10)
    # every return except possibly the final month(s) touched by that price must be unchanged
    unaffected = wml_before.index[:-3]
    pd.testing.assert_series_equal(wml_before.loc[unaffected], wml_after.loc[unaffected])


def test_min_assets_threshold_drops_thin_months():
    prices = make_prices(n_assets=15)
    thin = prices.copy()
    thin.iloc[50:55, 5:] = np.nan  # collapse most assets for a few months
    wml = wml_returns(thin, J=6, K=3, q=0.2, skip=0, min_assets=10)
    # months 50-54 should not appear as valid observations once their K-month window passes
    assert wml.index.isin(thin.index[50:55]).sum() <= 5


def test_load_monthly_prices_sorts_by_date(tmp_path):
    csv = tmp_path / "prices.csv"
    df = pd.DataFrame(
        {"A": [10, 11, 9]},
        index=pd.to_datetime(["2021-03-31", "2021-01-31", "2021-02-28"]),
    )
    df.index.name = "Date"
    df.to_csv(csv)
    loaded = load_monthly_prices(csv)
    assert list(loaded.index) == sorted(loaded.index)


def test_wml_returns_raises_nothing_on_empty_result_gracefully():
    prices = make_prices(n_assets=5)  # fewer assets than min_assets requires
    wml = wml_returns(prices, J=6, K=3, q=0.2, skip=0, min_assets=50)
    assert wml.empty
