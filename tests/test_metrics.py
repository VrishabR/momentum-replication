"""Unit tests for the statistics and cost-adjustment functions."""
import numpy as np
import pandas as pd

from momentum_replication.metrics import apply_costs, summarize


def test_summarize_on_series_of_all_same_value():
    returns = pd.Series([0.01] * 24)
    stats = summarize(returns, lags=1)
    assert stats["months"] == 24
    assert np.isclose(stats["mean_monthly_pct"], 1.0)
    assert np.isclose(stats["pct_positive_months"], 100.0)


def test_summarize_on_symmetric_series_has_mean_near_zero():
    returns = pd.Series([0.02, -0.02] * 12)
    stats = summarize(returns, lags=1)
    assert abs(stats["mean_monthly_pct"]) < 1e-6


def test_apply_costs_reduces_returns_by_expected_drag():
    returns = pd.Series([0.05] * 10)
    K, cost = 6, 0.001
    net = apply_costs(returns, K, cost)
    expected_drag = (4.0 / K) * cost
    assert np.allclose(net.values, returns.values - expected_drag)


def test_apply_costs_zero_cost_is_a_no_op():
    returns = pd.Series([0.03, -0.01, 0.02])
    net = apply_costs(returns, K=6, one_way_cost=0.0)
    pd.testing.assert_series_equal(net, returns)
