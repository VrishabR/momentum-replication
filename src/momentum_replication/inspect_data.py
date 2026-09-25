"""Basic data-quality report. Run after downloading:  python -m momentum_replication.inspect_data"""
from momentum_replication.paths import DATA_DIR
from momentum_replication.strategy import load_monthly_prices


def report(path):
    prices = load_monthly_prices(path)
    rets = prices.pct_change(fill_method=None)
    print(f"\n===== {path.name} =====")
    print(f"Shape: {prices.shape[0]} months x {prices.shape[1]} tickers")
    print(f"Date range: {prices.index.min().date()} to {prices.index.max().date()}")
    print(f"Non-positive prices (should be 0): {int((prices <= 0).sum().sum())}")
    counts = prices.notna().sum(axis=1)
    print("Assets with a price, last month of each year:")
    print(counts.groupby(prices.index.year).last().to_string())
    print("Largest single-month moves (check these are real, not data errors):")
    biggest = rets.abs().max().sort_values(ascending=False).head(5)
    for ticker, value in biggest.items():
        when = rets[ticker].abs().idxmax().date()
        print(f"  {ticker}: {value:.0%} in the month ending {when}")


def main():
    for name in ("sp500_monthly.csv", "crypto_monthly.csv"):
        report(DATA_DIR / name)


if __name__ == "__main__":
    main()
