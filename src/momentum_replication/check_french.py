"""Sanity check against Ken French's momentum factor.

Put the downloaded CSV at data/french_momentum.csv, then:
    python -m momentum_replication.check_french
"""
import pandas as pd

from momentum_replication.paths import DATA_DIR
from momentum_replication.strategy import load_monthly_prices, wml_returns


def read_french_momentum(path):
    """Read monthly rows (like '196301,  0.55') from Ken French's CSV; returns decimals."""
    values = {}
    with open(path, encoding="latin-1") as f:
        for line in f:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2 and len(parts[0]) == 6 and parts[0].isdigit():
                period = pd.Period(year=int(parts[0][:4]), month=int(parts[0][4:]), freq="M")
                values[period] = float(parts[1]) / 100
    return pd.Series(values).sort_index()


def main():
    french = read_french_momentum(DATA_DIR / "french_momentum.csv")
    prices = load_monthly_prices(DATA_DIR / "sp500_monthly.csv")
    # French ranks on returns from month t-12 to t-2 (skips the latest month), holds 1 month
    mine = wml_returns(prices, J=11, K=1, q=0.3, skip=1, min_assets=50)
    mine.index = mine.index.to_period("M")

    both = pd.concat([mine.rename("mine"), french.rename("french")], axis=1).dropna()
    print(f"Overlapping months: {len(both)}")
    print(f"Correlation: {both['mine'].corr(both['french']):.2f}")
    print((both.mean() * 100).round(3).rename("average monthly return (%)"))


if __name__ == "__main__":
    main()
