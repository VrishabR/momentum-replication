"""Run the full momentum experiment grid and save tables + charts to results/.

Run:  python -m momentum_replication.run_experiment
"""
import matplotlib
matplotlib.use("Agg")  # write chart files directly, no display needed
import matplotlib.pyplot as plt
import pandas as pd

from momentum_replication import config
from momentum_replication.metrics import apply_costs, summarize
from momentum_replication.paths import DATA_DIR, RESULTS_DIR
from momentum_replication.strategy import load_monthly_prices, wml_returns


def run_grid(exp):
    """Run every (J, K, skip) combination for one experiment; return a results DataFrame
    and the headline (J,K,skip)=config.HEADLINE return series for the chart."""
    prices = load_monthly_prices(DATA_DIR / exp["prices_file"])
    rows, headline_series = [], None
    for skip in config.SKIP_VALUES:
        for J in config.J_VALUES:
            for K in config.K_VALUES:
                gross = wml_returns(prices, J, K, exp["q"], skip, exp["min_assets"])
                net = apply_costs(gross, K, exp["one_way_cost"])
                row = {"experiment": exp["name"], "skip": skip, "J": J, "K": K}
                row.update({f"gross_{k}": v for k, v in summarize(gross).items()})
                row.update({f"net_{k}": v for k, v in summarize(net).items()})
                rows.append(row)
                if (J, K, skip) == config.HEADLINE:
                    headline_series = gross
    return pd.DataFrame(rows), headline_series


def run_subperiods(exp):
    """Re-run the headline (J,K,skip) setting on each declared sub-period."""
    prices = load_monthly_prices(DATA_DIR / exp["prices_file"])
    J, K, skip = config.HEADLINE
    rows = []
    for label, start, end in exp["periods"]:
        sliced = prices.loc[start:end]
        gross = wml_returns(sliced, J, K, exp["q"], skip, exp["min_assets"])
        row = {"experiment": exp["name"], "period": label, "J": J, "K": K}
        row.update(summarize(gross))
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    RESULTS_DIR.mkdir(exist_ok=True)
    all_rows, subperiod_rows, headline = [], [], {}

    for exp in config.EXPERIMENTS:
        grid, series = run_grid(exp)
        all_rows.append(grid)
        headline[exp["name"]] = series
        subperiod_rows.append(run_subperiods(exp))

    results = pd.concat(all_rows, ignore_index=True).round(4)
    results.to_csv(RESULTS_DIR / "results_grid.csv", index=False)

    subperiods = pd.concat(subperiod_rows, ignore_index=True).round(4)
    subperiods.to_csv(RESULTS_DIR / "results_subperiods.csv", index=False)

    # Human-readable headline table: one row per experiment, at config.HEADLINE settings
    J, K, skip = config.HEADLINE
    headline_rows = results[(results.J == J) & (results.K == K) & (results.skip == skip)]
    headline_table = headline_rows[
        ["experiment", "gross_mean_monthly_pct", "gross_t_stat_hac",
         "gross_annualized_sharpe", "net_mean_monthly_pct"]
    ]
    headline_table.to_csv(RESULTS_DIR / "results_headline.csv", index=False)
    print(f"\n=== Headline results (J={J}, K={K}, skip={skip}) ===")
    print(headline_table.to_string(index=False))

    print("\n=== Sub-period stability (headline setting) ===")
    print(subperiods[["experiment", "period", "mean_monthly_pct", "t_stat_hac"]].to_string(index=False))

    fig, ax = plt.subplots(figsize=(9, 5))
    for name, series in headline.items():
        (1 + series).cumprod().plot(ax=ax, label=name)
    ax.set_title(f"Growth of $1 in the winners-minus-losers strategy (J={J}, K={K})")
    ax.set_ylabel("Portfolio value ($)")
    ax.axhline(1.0, color="gray", linewidth=0.8, linestyle="--")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "cumulative_returns.png", dpi=150)
    print(f"\nSaved CSVs and chart to {RESULTS_DIR}/")


if __name__ == "__main__":
    main()
