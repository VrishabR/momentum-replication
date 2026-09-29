# Momentum Replication

[![tests](https://github.com/VrishabR/momentum-replication/actions/workflows/tests.yml/badge.svg)](https://github.com/VrishabR/momentum-replication/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A replication of the price momentum effect from Jegadeesh & Titman (1993),
*"Returns to Buying Winners and Selling Losers: Implications for Stock Market
Efficiency,"* Journal of Finance 48(1), 65–91, tested on two datasets the original
paper did not use: current S&P 500 constituents (2005–2025) and large
cryptocurrencies (2018–2025).

**Claim tested:** assets that performed best over the past 3–12 months continue to
outperform the worst performers over the following 3–12 months.

## Why this project

Backtests are easy to get quietly wrong. A single unshifted line of code can leak
future information into a signal and make almost any strategy look profitable. This
project is built to make that mistake hard to make silently. The experimental protocol
is written and committed before any result is produced (`docs/PROTOCOL.md`), the
core ranking logic has an explicit unit test asserting no look-ahead, and significance
is judged with Newey-West-corrected standard errors rather than a naive t-test, since
the strategy's overlapping holding periods inflate the naive one.

## Project structure

```
momentum-replication/
├── src/momentum_replication/
│   ├── config.py           # all experiment settings (single source of truth)
│   ├── strategy.py         # ranking + winners-minus-losers return construction
│   ├── metrics.py          # HAC t-stats, Sharpe, cost adjustment
│   ├── get_data.py         # downloads and saves month-end prices
│   ├── inspect_data.py     # data-quality checks before trusting any result
│   ├── check_french.py     # sanity check against Ken French's published factor
│   └── run_experiment.py   # runs the full grid, saves tables + chart
├── tests/                  # pytest unit tests (incl. a look-ahead-bias regression test)
├── docs/
│   ├── PROTOCOL.md         # pre-registered method, written before any results
│   └── RESULTS.md          # results write-up (filled in after running on real data)
├── universe/                # ticker lists used (committed, so the sample is auditable)
├── results/                  # output tables and chart (committed)
└── .github/workflows/tests.yml   # CI: runs the test suite on every push
```

## Setup

Requires Python 3.10+.

```bash
git clone https://github.com/VrishabR/momentum-replication.git
cd momentum-replication
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Usage

```bash
# 1. Download data (S&P 500 constituents + 25 large cryptocurrencies)
python -m momentum_replication.get_data

# 2. Check the data for obvious problems before trusting any result
python -m momentum_replication.inspect_data

# 3. (Optional) validate the pipeline against Ken French's published momentum factor
#    — download the "Momentum Factor (Mom)" CSV from the Ken French Data Library
#    (Dartmouth) and save it as data/french_momentum.csv first
python -m momentum_replication.check_french

# 4. Run the full experiment: J x K x skip grid, sub-periods, cost adjustment, chart
python -m momentum_replication.run_experiment
```

Outputs land in `results/`: `results_grid.csv` (every configuration),
`results_headline.csv` (the pre-registered headline configuration),
`results_subperiods.csv` (stability over time), and `cumulative_returns.png`.

## Testing

```bash
pytest -v
```

12 unit tests cover the ranking logic, the winners-minus-losers construction, cost
adjustment, and — most importantly — a regression test that perturbing a future price
does not change past strategy returns. Tests run automatically on every push via GitHub
Actions (see the badge above).

## Method summary

For each month, assets are ranked by trailing J-month return and split into a top-`q`
"winners" leg and bottom-`q` "losers" leg, equal-weighted. Cohorts are held for K
months with overlap, as in the original paper. The full method, including why HAC
standard errors are used and how trading costs are approximated, is in
[`docs/PROTOCOL.md`](docs/PROTOCOL.md) — written before any experiment was run.

## Results

See [`docs/RESULTS.md`](docs/RESULTS.md) for the full write-up once populated,
including the headline table, the full parameter grid, sub-period stability, and the
Ken French validation.

## Known limitations

- **Survivorship bias:** both universes are defined by membership today, so failed
  companies and coins are excluded.
- **Data source:** Yahoo Finance via `yfinance`, not the CRSP database the original
  paper used.
- **Approximate costs:** `metrics.apply_costs` is a simplified turnover-based estimate,
  not a broker-accurate cost model.
- **Not investment advice:** this is a research replication exercise. A backtest that
  looks good, even one that reproduces a well-known academic result, is not evidence
  that a strategy will be profitable after real-world execution, financing, and
  short-selling constraints.

Full details in [`docs/PROTOCOL.md`](docs/PROTOCOL.md#limitations-stated-in-advance).



## References

Jegadeesh, N., & Titman, S. (1993). Returns to Buying Winners and Selling Losers:
Implications for Stock Market Efficiency. *The Journal of Finance*, 48(1), 65–91.

## License

MIT — see [LICENSE](LICENSE).
