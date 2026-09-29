# Pre-Registered Protocol

Written before running the experiment, so results can't be quietly adjusted after the fact.
Any change made after seeing results is logged under **Deviations** at the bottom, not
edited into the sections above it.

## Claim under test

Jegadeesh & Titman (1993), *Returns to Buying Winners and Selling Losers: Implications
for Stock Market Efficiency*, Journal of Finance 48(1), 65–91: assets that performed
best over the past J months continue to outperform the worst performers over the
following K months.

## Datasets

| Dataset | Universe | Period | Source |
|---|---|---|---|
| A | Current S&P 500 constituents | 2005-01 to 2025-12 | Yahoo Finance via `yfinance`, ticker list from Wikipedia |
| B | 25 large cryptocurrencies (see `universe/crypto_tickers.csv`) | 2018-01 to 2025-12 | Yahoo Finance via `yfinance` |

Both are convenience samples, not the original paper's NYSE/AMEX universe (1965–1989)
or its CRSP data source. This is a deliberate substitution to test generalization, not
a like-for-like replication — see **Limitations**.

## Method

1. At each month-end, rank assets by their trailing J-month return (`J ∈ {3, 6, 9, 12}`).
2. Form two legs: the top `q` share of assets ("winners") and the bottom `q` share
   ("losers"), equal-weighted within each leg.
   - Dataset A: `q = 0.10` (deciles) as the primary cut, `q = 0.20` (quintiles) as a
     robustness check.
   - Dataset B: `q = 0.20` (quintiles), because the universe is much smaller than
     Dataset A and deciles would leave too few names per leg.
3. Hold each cohort for K months (`K ∈ {3, 6, 9, 12}`), with overlapping cohorts as in
   the original paper: the reported monthly return is the average return across the K
   cohorts currently open.
4. Run the full method twice: once using the most recent month in the ranking signal
   (`skip = 0`), and once excluding it (`skip = 1`), since the most recent month is
   known to show short-term reversal rather than momentum.
5. A month is excluded from a dataset if fewer than `min_assets` have a valid ranking
   that month (50 for Dataset A, 10 for Dataset B).

## Headline configuration

`J = 6, K = 6, skip = 0` is designated in advance as the single configuration reported
in the top-line results table and chart. All other `(J, K, skip)` combinations are
reported as a full grid in `results/results_grid.csv`, not cherry-picked after the fact.

## Statistics

- Mean monthly winners-minus-losers return.
- **Newey-West (HAC) t-statistic**, not the naive t-statistic, as the primary
  significance measure. Overlapping holding periods induce serial correlation in
  monthly returns, which inflates the naive t-statistic; both are reported, but HAC is
  the one used to judge significance.
- Annualized Sharpe ratio, percentage of positive months.
- A cost-adjusted return, using a simple assumed one-way trading cost per dataset
  (0.10% for Dataset A, 0.30% for Dataset B, reflecting wider crypto spreads), applied
  as a fixed monthly drag proportional to `1/K` (see `metrics.apply_costs` for the exact
  formula and its assumptions).

## Robustness checks (planned, not exploratory)

- Full `J × K × skip` grid (16 × 2 = 32 combinations per dataset).
- Three sub-periods for Dataset A (2005–2012, 2013–2019, 2020–2025) and two for
  Dataset B (2019–2021, 2022–2025), run at the headline `(J, K, skip)` only.
- Cost-adjusted vs. gross returns.

## Predictions

- Dataset A (S&P 500): I predict a positive momentum effect will appear, but weaker
  than in the original 1965–1989 sample. Momentum has been public knowledge in
  academic finance since 1993, so any edge may be partly arbitraged away by now.
- Dataset B (crypto): I predict a stronger raw effect than equities, since crypto
  markets are younger, more retail-driven, and narrative-driven price trends tend to
  persist longer. I also expect it to be noisier (lower t-stats) given the much
  shorter sample (2018–2025 vs. 2005–2025) and higher volatility.
- Cost survival: I predict the S&P 500 result is more likely to survive cost
  adjustment than crypto, since the assumed trading cost for crypto (0.3%/trade) is
  three times higher than equities (0.1%/trade), and any crypto edge is more likely
  to be thin enough that costs erase it.

## Limitations

- **Survivorship bias.** Both universes are defined by membership *today*, so
  companies and coins that failed and disappeared are excluded. This tends to flatter
  the loser leg's realized returns, biasing the winners-minus-losers spread downward
  from what a point-in-time universe would show — the opposite direction from most
  survivorship-bias concerns, and worth checking in the write-up.
- **Data source.** Yahoo Finance daily closes, not the CRSP database the original paper
  used. Adjustments for splits/dividends may differ in edge cases.
- **Costs are approximate.** `apply_costs` assumes full-leg turnover scaled by `1/K`
  and a flat cost per trade; it ignores names that stay in the portfolio between
  months (overstating turnover) and ignores short-financing costs (understating them
  for the short leg).
- **Short-selling practicality.** Shorting a basket of cryptocurrencies monthly is not
  something most retail accounts can actually do; Dataset B's results should be read as
  a test of the momentum pattern in the data, not a tradeable strategy.
- **Different eras.** Any difference from the 1965–1989 result could come from the
  asset class, the more recent period, or the data source — this design cannot
  separate those explanations.

## Deviations from this protocol

- None.
