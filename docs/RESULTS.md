# Results

*Fill this in after running `python -m momentum_replication.run_experiment` on real
data. Do not edit `docs/PROTOCOL.md` to match what you find here — if something
changed, log it under "Deviations" in that file instead.*

## Headline results (J=6, K=6, skip=0)

| Experiment | Gross mean monthly return | HAC t-stat | Annualized Sharpe | Net (cost-adjusted) mean monthly |
|---|---|---|---|---|
| S&P 500 deciles | | | | |
| S&P 500 quintiles | | | | |
| Crypto quintiles | | | | |

*(Copy from `results/results_headline.csv`.)*

![Cumulative returns](../results/cumulative_returns.png)

## Full grid

See `results/results_grid.csv` for all 32 `(J, K, skip)` combinations per dataset.
Summarize the pattern here, e.g. whether longer formation/holding windows help or hurt,
and whether `skip=1` changes the picture.

## Sub-period stability

See `results/results_subperiods.csv`. Summarize whether the effect is stable across
sub-periods or concentrated in one.

## Validation against Ken French's momentum factor

*(From `python -m momentum_replication.check_french`.)* Correlation: \_\_\_. Does the
sign and rough magnitude agree with your Dataset A result?

## Interpretation

For each dataset, classify the result as **same** (positive and HAC-significant),
**weaker**, **absent**, or **reversed** relative to the original paper, and compare to
the predictions written in `docs/PROTOCOL.md` before running anything.

- **S&P 500:** 
- **Crypto:** 

## What matched the original paper, and what didn't

## Threats to validity

Revisit the Limitations section of `docs/PROTOCOL.md` in light of the actual results —
e.g., does the direction of survivorship bias you expected match what you see?

## Possible follow-ups

- [ ] Try a different sub-period split
- [ ] Try a different cost assumption in `config.EXPERIMENTS`
- [ ] Add a third dataset (see README "Extending this project")
