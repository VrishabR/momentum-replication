"""All experiment settings live here. Change them here, never inside the logic.

IMPORTANT: these settings are part of the pre-registered protocol (docs/PROTOCOL.md).
If you change one after seeing results, record it under 'Deviations' in the protocol.
"""

# ---- Data download settings ----
SP500_START, SP500_END = "2005-01-01", "2025-12-31"
CRYPTO_START, CRYPTO_END = "2018-01-01", "2025-12-31"
CRYPTO_TICKERS = [
    "BTC-USD", "ETH-USD", "XRP-USD", "BNB-USD", "SOL-USD", "DOGE-USD", "ADA-USD",
    "TRX-USD", "LINK-USD", "AVAX-USD", "XLM-USD", "LTC-USD", "BCH-USD", "DOT-USD",
    "XMR-USD", "ATOM-USD", "ETC-USD", "ALGO-USD", "VET-USD", "FIL-USD", "EOS-USD",
    "XTZ-USD", "NEO-USD", "DASH-USD", "ZEC-USD",
]

# ---- Strategy grid ----
J_VALUES = (3, 6, 9, 12)    # formation (look-back) months
K_VALUES = (3, 6, 9, 12)    # holding months
SKIP_VALUES = (0, 1)        # 0 = paper's main version; 1 = skip most recent month
HEADLINE = (6, 6, 0)        # (J, K, skip) used for the headline table and chart

# ---- Experiments ----
# q = share of assets in each leg (0.1 = deciles); one_way_cost = assumed trading cost per
# dollar traded (0.001 = 0.1%); periods = sub-samples for the stability check.
EXPERIMENTS = [
    {
        "name": "sp500_deciles", "prices_file": "sp500_monthly.csv",
        "q": 0.1, "min_assets": 50, "one_way_cost": 0.001,
        "periods": [("2005-2012", "2005-01-01", "2012-12-31"),
                    ("2013-2019", "2013-01-01", "2019-12-31"),
                    ("2020-2025", "2020-01-01", "2025-12-31")],
    },
    {
        "name": "sp500_quintiles", "prices_file": "sp500_monthly.csv",
        "q": 0.2, "min_assets": 50, "one_way_cost": 0.001,
        "periods": [("2005-2012", "2005-01-01", "2012-12-31"),
                    ("2013-2019", "2013-01-01", "2019-12-31"),
                    ("2020-2025", "2020-01-01", "2025-12-31")],
    },
    {
        "name": "crypto_quintiles", "prices_file": "crypto_monthly.csv",
        "q": 0.2, "min_assets": 10, "one_way_cost": 0.003,
        "periods": [("2019-2021", "2019-01-01", "2021-12-31"),
                    ("2022-2025", "2022-01-01", "2025-12-31")],
    },
]
