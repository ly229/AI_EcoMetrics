#!/usr/bin/env python3
"""Plot wage-related trends by firm group and identify the lowest labor-cost observations.

The Compustat panel does not contain worker-level wages. It does contain `xlr`,
which is a labor-expense proxy. We use it to study:
- inflation-adjusted labor expense per employee
- labor expense as a share of revenue
- the lowest labor-expense-per-employee firm-year observations
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MultipleLocator
import pandas as pd


DEFAULT_INPUT = Path("data/compustat_panel_by_firm_group.csv")
DEFAULT_CPI = Path("data/cpiu_annual_average.csv")
DEFAULT_MIN_WAGE = Path("data/federal_minimum_wage.csv")
DEFAULT_FIGURE = Path("figures/wage_trends_by_group_real.png")
DEFAULT_TABLE = Path("tables/lowest_labor_per_employee.csv")
DEFAULT_ANNUAL = Path("tables/annual_wage_trends_by_group.csv")

ERA_SPANS = [
    (1950, 1979, "Pre-computerization", "#D9D9D9"),
    (1980, 1989, "Computerization", "#BFD7EA"),
    (1990, 2014, "Indexing", "#F5D7A1"),
    (2015, 2025, "AI", "#E8B7B7"),
]

GROUP_ORDER = [
    "S&P Global",
    "State Street family",
    "JPMorgan family",
    "Bank of America / Merrill Lynch family",
    "BNY Mellon / Dreyfus family",
]

GROUP_COLORS = {
    "S&P Global": "#7E7D7A",
    "State Street family": "#4E79A7",
    "JPMorgan family": "#F28E2B",
    "Bank of America / Merrill Lynch family": "#59A14F",
    "BNY Mellon / Dreyfus family": "#E15759",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plot wage-related trends by firm group.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path.")
    parser.add_argument("--cpi", type=Path, default=DEFAULT_CPI, help="Annual CPI-U CSV path.")
    parser.add_argument("--min-wage", type=Path, default=DEFAULT_MIN_WAGE, help="Federal minimum wage CSV path.")
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE, help="Output figure path.")
    parser.add_argument("--lowest-table", type=Path, default=DEFAULT_TABLE, help="CSV path for the lowest observations.")
    parser.add_argument("--annual-table", type=Path, default=DEFAULT_ANNUAL, help="CSV path for annual grouped metrics.")
    return parser


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["year", "emp", "revt", "xlr"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_cpi(path: Path) -> pd.DataFrame:
    cpi = pd.read_csv(path)
    cpi["year"] = pd.to_numeric(cpi["year"], errors="coerce")
    cpi["cpiu_annual_avg"] = pd.to_numeric(cpi["cpiu_annual_avg"], errors="coerce")
    return cpi


def load_min_wage(path: Path) -> pd.DataFrame:
    mw = pd.read_csv(path)
    if "observation_date" in mw.columns:
        mw["observation_date"] = pd.to_datetime(mw["observation_date"], errors="coerce")
        mw["year"] = mw["observation_date"].dt.year
    else:
        mw["DATE"] = pd.to_datetime(mw["DATE"], errors="coerce")
        mw["year"] = mw["DATE"].dt.year
    value_col = "FEDMINNFRWG" if "FEDMINNFRWG" in mw.columns else "value"
    mw[value_col] = pd.to_numeric(mw[value_col], errors="coerce")
    annual = (
        mw.dropna(subset=["year", value_col])
        .groupby("year", as_index=False)
        .agg(min_wage_hourly=(value_col, "mean"))
    )
    return annual


def add_era_shading(ax) -> None:
    for start, end, label, color in ERA_SPANS:
        ax.axvspan(start, end, color=color, alpha=0.22, lw=0)
        ax.text(
            (start + end) / 2,
            0.98,
            label,
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=8.5,
            color="#444444",
        )


def panel_style(ax, ylabel: str) -> None:
    ax.set_xlim(1950, 2025)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.grid(axis="y", alpha=0.24)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylabel(ylabel)


def year_group_means(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    return (
        df.dropna(subset=["year", "firm_group", value_col])
        .groupby(["year", "firm_group"], observed=True)
        .agg(mean_value=(value_col, "mean"))
        .reset_index()
        .sort_values(["firm_group", "year"])
    )


def prepare_data(panel: pd.DataFrame, cpi: pd.DataFrame) -> pd.DataFrame:
    merged = panel.merge(cpi, on="year", how="left")
    base_cpi = float(cpi.loc[cpi["year"] == 2025, "cpiu_annual_avg"].iloc[0])
    merged["inflation_factor"] = base_cpi / merged["cpiu_annual_avg"]
    merged["real_labor_expense"] = merged["xlr"] * merged["inflation_factor"]
    merged["real_labor_per_employee"] = merged["real_labor_expense"] / merged["emp"]
    merged["labor_share_revenue"] = merged["xlr"] / merged["revt"]
    merged["real_labor_per_employee"] = merged["real_labor_per_employee"].replace([float("inf"), float("-inf")], pd.NA)
    merged["labor_share_revenue"] = merged["labor_share_revenue"].replace([float("inf"), float("-inf")], pd.NA)
    return merged


def build_annual_table(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["year", "firm_group"], observed=True)
        .agg(
            n_obs=("firm", "size"),
            n_firms=("firm", "nunique"),
            mean_emp=("emp", "mean"),
            mean_xlr=("xlr", "mean"),
            mean_real_labor_per_employee=("real_labor_per_employee", "mean"),
            median_real_labor_per_employee=("real_labor_per_employee", "median"),
            mean_labor_share_revenue=("labor_share_revenue", "mean"),
            median_labor_share_revenue=("labor_share_revenue", "median"),
        )
        .reset_index()
        .sort_values(["firm_group", "year"])
    )


def build_lowest_table(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    cols = ["year", "firm_group", "tic", "xlr", "emp", "revt", "inflation_factor", "real_labor_per_employee", "labor_share_revenue"]
    lowest = (
        df.dropna(subset=["real_labor_per_employee"])
        .sort_values("real_labor_per_employee", ascending=True)
        .loc[:, cols]
        .head(n)
        .copy()
    )
    lowest["real_labor_per_employee"] = lowest["real_labor_per_employee"].round(3)
    lowest["labor_share_revenue"] = lowest["labor_share_revenue"].round(3)
    lowest["inflation_factor"] = lowest["inflation_factor"].round(3)
    return lowest


def plot_panel(ax, df: pd.DataFrame, value_col: str, title: str, ylabel: str) -> None:
    for group in GROUP_ORDER:
        sub = (
            df.loc[df["firm_group"] == group, ["year", value_col]]
            .dropna()
            .groupby("year", as_index=False)
            .agg(mean_value=(value_col, "mean"))
        )
        if sub.empty:
            continue
        ax.plot(
            sub["year"],
            sub["mean_value"],
            marker="o",
            linewidth=1.9,
            markersize=3.4,
            color=GROUP_COLORS[group],
            label=group,
        )

    add_era_shading(ax)
    ax.set_title(title, fontsize=11)
    panel_style(ax, ylabel)


def prepare_min_wage_series(mw: pd.DataFrame, cpi: pd.DataFrame) -> pd.DataFrame:
    base_cpi = float(cpi.loc[cpi["year"] == 2025, "cpiu_annual_avg"].iloc[0])
    out = mw.merge(cpi, on="year", how="left")
    out["inflation_factor"] = base_cpi / out["cpiu_annual_avg"]
    out["min_wage_annual_nominal"] = out["min_wage_hourly"] * 2080 / 1000.0
    out["min_wage_annual_real"] = out["min_wage_annual_nominal"] * out["inflation_factor"]
    return out


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif", "STIX Two Text"],
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
        }
    )

    panel = load_panel(args.input)
    cpi = load_cpi(args.cpi)
    min_wage = load_min_wage(args.min_wage)
    merged = prepare_data(panel, cpi)
    min_wage = prepare_min_wage_series(min_wage, cpi)

    annual = build_annual_table(merged)
    annual = annual.replace([float("inf"), float("-inf")], pd.NA)
    args.annual_table.parent.mkdir(parents=True, exist_ok=True)
    annual.to_csv(args.annual_table, index=False)

    lowest = build_lowest_table(merged, n=10)
    args.lowest_table.parent.mkdir(parents=True, exist_ok=True)
    lowest.to_csv(args.lowest_table, index=False)

    fig, axes = plt.subplots(3, 1, figsize=(11.8, 12.0), constrained_layout=False)
    fig.suptitle("Wage-Related Trends in Financial Firms", fontsize=14, y=0.98)

    plot_panel(
        axes[0],
        merged,
        "real_labor_per_employee",
        "Inflation-Adjusted Labor Expense per Employee",
        "2025 $000 / employee",
    )
    plot_panel(
        axes[1],
        merged,
        "labor_share_revenue",
        "Labor Expense as a Share of Revenue",
        "Labor expense / revenue",
    )
    axes[2].plot(
        min_wage["year"],
        min_wage["min_wage_annual_nominal"],
        color="#8C564B",
        linewidth=2.0,
        marker="o",
        markersize=3.5,
        label="Nominal minimum wage",
    )
    axes[2].plot(
        min_wage["year"],
        min_wage["min_wage_annual_real"],
        color="#D62728",
        linewidth=2.0,
        marker="s",
        markersize=3.3,
        linestyle="--",
        label="2025 $ real minimum wage",
    )
    add_era_shading(axes[2])
    axes[2].set_title("Federal Minimum Wage, Annualized", fontsize=11)
    panel_style(axes[2], "2025 $000 / year")
    axes[2].yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))
    axes[2].set_xlabel("Year")
    axes[0].tick_params(labelbottom=False)
    axes[1].tick_params(labelbottom=False)
    axes[0].yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))
    axes[1].yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:.0%}"))

    legend_handles = [
        Line2D([0], [0], color=GROUP_COLORS[group], lw=1.9, marker="o", markersize=4, label=group)
        for group in GROUP_ORDER
    ]
    wage_handles = [
        Line2D([0], [0], color="#8C564B", lw=2.0, marker="o", markersize=4, label="Nominal minimum wage"),
        Line2D([0], [0], color="#D62728", lw=2.0, marker="s", markersize=4, linestyle="--", label="2025 $ real minimum wage"),
    ]
    era_patches = [Patch(facecolor=color, edgecolor="none", alpha=0.22, label=label) for _, _, label, color in ERA_SPANS]

    fig.legend(handles=legend_handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.915))
    fig.legend(handles=wage_handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.875))
    fig.legend(handles=era_patches, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.965))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.08, hspace=0.34)

    args.figure.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.figure, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figure to {args.figure}")
    print(f"saved annual table to {args.annual_table}")
    print(f"saved lowest observations to {args.lowest_table}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
