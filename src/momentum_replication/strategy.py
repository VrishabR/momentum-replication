"""The momentum strategy: rank assets, form winner/loser portfolios, compute returns."""
import pandas as pd

EPS = 1e-9  # tolerance so ties at a cutoff are treated consistently on both legs


def load_monthly_prices(path):
    """Load a CSV of month-end prices (rows = months, columns = tickers)."""
    prices = pd.read_csv(path, index_col=0, parse_dates=True)
    return prices.sort_index()


def formation_rank(prices, J, skip=0):
    """Percentile-rank assets by past-J-month return, measured at each month-end.

    skip=1 leaves out the most recent month. 1.0 = best past performer.
    Uses only prices up to and including the current month-end.
    """
    past_return = prices.shift(skip).pct_change(J, fill_method=None)
    return past_return.rank(axis=1, pct=True)


def wml_returns(prices, J, K, q=0.1, skip=0, min_assets=10):
    """Monthly winners-minus-losers returns, Jegadeesh-Titman style.

    Each month a new cohort is formed and held for K months; the strategy return is the
    average of the K live cohorts. Winners = top q share of assets, losers = bottom q
    share, each leg equal-weighted. Months without at least `min_assets` rankable
    assets are skipped.
    """
    monthly_ret = prices.pct_change(fill_method=None)
    rank = formation_rank(prices, J, skip)
    n_valid = rank.notna().sum(axis=1)

    cohorts = []
    for k in range(1, K + 1):
        r = rank.shift(k)  # ranks that were known k months ago -> no look-ahead
        enough = n_valid.shift(k) >= min_assets
        winners = monthly_ret.where(r > (1 - q) + EPS).mean(axis=1)   # strictly above cutoff
        losers = monthly_ret.where(r <= q + EPS).mean(axis=1)         # at or below cutoff
        cohorts.append((winners - losers).where(enough))
    return pd.concat(cohorts, axis=1).mean(axis=1, skipna=False).dropna()
