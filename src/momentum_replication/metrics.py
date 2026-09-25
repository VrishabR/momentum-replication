"""Statistics and cost adjustments for a monthly return series."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats


def hac_t_stat(series, lags):
    """Newey-West (HAC) t-stat and p-value for 'mean = 0'.

    Overlapping holding periods make consecutive monthly returns correlated, which makes
    the plain t-stat too optimistic. HAC standard errors correct for that.
    """
    x = np.ones(len(series))
    fit = sm.OLS(np.asarray(series, dtype=float), x).fit(
        cov_type="HAC", cov_kwds={"maxlags": int(lags)}
    )
    return float(fit.tvalues[0]), float(fit.pvalues[0])


def summarize(returns, lags=1):
    """Summary statistics for a monthly return series."""
    mean, std = returns.mean(), returns.std()
    naive_t, _ = stats.ttest_1samp(returns, 0.0)
    hac_t, hac_p = hac_t_stat(returns, lags)
    return {
        "months": len(returns),
        "mean_monthly_pct": 100 * mean,
        "t_stat_naive": naive_t,
        "t_stat_hac": hac_t,
        "p_value_hac": hac_p,
        "annualized_sharpe": mean / std * np.sqrt(12),
        "pct_positive_months": 100 * (returns > 0).mean(),
    }


def apply_costs(returns, K, one_way_cost):
    """Subtract an approximate trading-cost drag from monthly strategy returns.

    Assumptions (deliberately conservative):
      * each leg is 100% of capital (long 100%, short 100%);
      * each month 1/K of each leg is sold and 1/K is bought, so 2/K per leg, 4/K total;
      * every trade costs `one_way_cost` (e.g. 0.001 = 0.1%);
      * ignores names that stay in the portfolio (so it overstates turnover),
        and ignores shorting fees and financing costs (so it understates those).
    """
    monthly_drag = (4.0 / K) * one_way_cost
    return returns - monthly_drag
