"""Download prices from Yahoo Finance and save month-end prices to data/.

Run:  python -m momentum_replication.get_data
"""
from io import StringIO

import pandas as pd
import requests
import yfinance as yf

from momentum_replication import config
from momentum_replication.paths import DATA_DIR, UNIVERSE_DIR


def to_month_end(daily_prices):
    try:
        return daily_prices.resample("ME").last()   # newer pandas
    except ValueError:
        return daily_prices.resample("M").last()    # older pandas


def download_monthly(tickers, start, end, out_file):
    daily = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=True)["Close"]
    daily = daily.dropna(axis=1, how="all")            # drop tickers with no data at all
    missing = sorted(set(tickers) - set(daily.columns))
    if missing:
        print(f"WARNING: no data for {len(missing)} tickers: {missing}")
    monthly = to_month_end(daily)
    monthly.to_csv(out_file)
    print(f"Saved {out_file}: {monthly.shape[0]} months x {monthly.shape[1]} tickers")


def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0 (momentum-replication learning project)"}
    html = requests.get(url, headers=headers, timeout=30).text
    table = pd.read_html(StringIO(html))[0]
    return table["Symbol"].str.replace(".", "-", regex=False).tolist()   # BRK.B -> BRK-B


def main():
    DATA_DIR.mkdir(exist_ok=True)
    UNIVERSE_DIR.mkdir(exist_ok=True)

    sp500 = get_sp500_tickers()
    pd.Series(sp500, name="ticker").to_csv(UNIVERSE_DIR / "sp500_tickers.csv", index=False)
    download_monthly(sp500, config.SP500_START, config.SP500_END, DATA_DIR / "sp500_monthly.csv")

    crypto = config.CRYPTO_TICKERS
    pd.Series(crypto, name="ticker").to_csv(UNIVERSE_DIR / "crypto_tickers.csv", index=False)
    download_monthly(crypto, config.CRYPTO_START, config.CRYPTO_END, DATA_DIR / "crypto_monthly.csv")


if __name__ == "__main__":
    main()
