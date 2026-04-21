#!/usr/bin/env python3
"""Plot annual AUM/employee and revenue/employee trends by firm group."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, MultipleLocator
import pandas as pd


DEFAULT_INPUT = Path("Data/compustat_panel_by_firm_group.csv")
DEFAULT_OUTPUT = Path("outputs/figures/firm_group_productivity_trends.png")
DEFAULT_TABLE = Path("outputs/tables/annual_firm_group_productivity_ratios.csv")

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
    parser = argparse.ArgumentParser(description="Plot firm-group trends for key productivity ratios.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output figure path.")
    parser.add_argument(
        "--table",
        type=Path,
        default=DEFAULT_TABLE,
        help=f"Output annual table path (default: {DEFAULT_TABLE})",
    )
    return parser


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["year", "aum_crsp", "emp", "revt"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["aum_per_employee"] = df["aum_crsp"] / df["emp"]
    df["revenue_per_employee"] = df["revt"] / df["emp"]
    df = df.replace([float("inf"), float("-inf")], pd.NA)
    return df


def build_grouped_series(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["year", "firm_group"], dropna=False)
        .agg(
            n_obs=("firm_group", "size"),
            n_firms=("firm", "nunique"),
            aum_total=("aum_crsp", lambda s: s.sum(min_count=1)),
            emp_total=("emp", lambda s: s.sum(min_count=1)),
            rev_total=("revt", lambda s: s.sum(min_count=1)),
            aum_per_employee_mean=("aum_per_employee", "mean"),
            aum_per_employee_median=("aum_per_employee", "median"),
            revenue_per_employee_mean=("revenue_per_employee", "mean"),
            revenue_per_employee_median=("revenue_per_employee", "median"),
        )
        .reset_index()
        .sort_values(["firm_group", "year"])
    )
    grouped["aum_per_employee_total"] = grouped["aum_total"] / grouped["emp_total"]
    grouped["revenue_per_employee_total"] = grouped["rev_total"] / grouped["emp_total"]
    grouped = grouped.replace([float("inf"), float("-inf")], pd.NA)
    return grouped


def style_axes(ax) -> None:
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))


def plot_group_trends(ax, df: pd.DataFrame, value_col: str, title: str, ylabel: str) -> list[Line2D]:
    handles: list[Line2D] = []
    missing_groups: list[str] = []

    for group in GROUP_ORDER:
        series = df.loc[df["firm_group"] == group, ["year", value_col]].dropna()
        if series.empty:
            missing_groups.append(group)
            continue

        color = GROUP_COLORS[group]
        line, = ax.plot(
            series["year"],
            series[value_col],
            label=group,
            color=color,
            linewidth=2.0,
            marker="o",
            markersize=3.6,
            alpha=0.95,
        )
        handles.append(line)

    ax.set_title(title, fontsize=11)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    style_axes(ax)

    if missing_groups:
        note = ", ".join(missing_groups)
        ax.text(
            0.99,
            0.04,
            f"No data: {note}",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8.5,
            color="#555555",
        )

    return handles


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

    df = load_panel(args.input)
    grouped = build_grouped_series(df)

    args.table.parent.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(args.table, index=False)

    fig = plt.figure(figsize=(12.5, 10.0), constrained_layout=False)
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 0.16], hspace=0.18)
    axes = [
        fig.add_subplot(gs[0, 0]),
        fig.add_subplot(gs[1, 0], sharex=None),
    ]
    legend_ax = fig.add_subplot(gs[2, 0])
    legend_ax.axis("off")
    fig.suptitle("Firm-Group Trends in Labor Productivity", fontsize=14, y=0.985)

    plot_group_trends(
        axes[0],
        grouped,
        "aum_per_employee_mean",
        "AUM per Employee",
        "AUM / employee",
    )
    plot_group_trends(
        axes[1],
        grouped,
        "revenue_per_employee_mean",
        "Revenue per Employee",
        "Revenue / employee",
    )
    axes[0].tick_params(labelbottom=False)

    legend_handles = [
        Line2D([0], [0], color=GROUP_COLORS[group], lw=2.0, marker="o", markersize=4, label=group)
        for group in GROUP_ORDER
    ]
    legend_ax.legend(
        handles=legend_handles,
        labels=GROUP_ORDER,
        loc="center",
        ncol=3,
        frameon=False,
    )
    fig.subplots_adjust(left=0.085, right=0.985, top=0.93, bottom=0.06)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figure to {args.output}")
    print(f"saved table to {args.table}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
