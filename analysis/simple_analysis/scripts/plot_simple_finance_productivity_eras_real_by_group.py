#!/usr/bin/env python3
"""Plot inflation-adjusted productivity trends by firm group and era."""

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
DEFAULT_OUTPUT = Path("figures/simple_finance_productivity_eras_real_by_group.png")

ERA_BINS = [1949, 1979, 1990, 2015, 2100]
ERA_LABELS = [
    "Pre-computerization",
    "Computerization",
    "Indexing",
    "AI",
]
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
    parser = argparse.ArgumentParser(description="Plot inflation-adjusted productivity trends by firm group.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path.")
    parser.add_argument("--cpi", type=Path, default=DEFAULT_CPI, help="Annual CPI-U CSV path.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output figure path.")
    return parser


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["year", "emp", "revt", "aum_crsp"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_cpi(path: Path) -> pd.DataFrame:
    cpi = pd.read_csv(path)
    cpi["year"] = pd.to_numeric(cpi["year"], errors="coerce")
    cpi["cpiu_annual_avg"] = pd.to_numeric(cpi["cpiu_annual_avg"], errors="coerce")
    return cpi


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


def year_group_means(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    return (
        df.dropna(subset=["year", "firm_group", value_col])
        .groupby(["year", "firm_group"], observed=True)
        .agg(mean_value=(value_col, "mean"))
        .reset_index()
        .sort_values(["firm_group", "year"])
    )


def panel_style(ax) -> None:
    ax.grid(axis="y", alpha=0.24)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_major_locator(MultipleLocator(2000))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))


def plot_group(ax, df: pd.DataFrame, group: str) -> None:
    sub = df[df["firm_group"] == group].sort_values("year")
    if sub.empty:
        ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center", va="center")
        ax.set_axis_off()
        return

    rev = sub[["year", "real_revenue_per_employee"]].dropna()
    aum = sub[["year", "real_aum_per_employee"]].dropna()

    if not rev.empty:
        ax.plot(
            rev["year"],
            rev["real_revenue_per_employee"],
            color="#4E79A7",
            linewidth=2.0,
            marker="o",
            markersize=3.7,
            label="Real revenue / employee",
        )

    if not aum.empty:
        ax.plot(
            aum["year"],
            aum["real_aum_per_employee"],
            color="#777777",
            linewidth=2.0,
            marker="s",
            markersize=3.4,
            linestyle="--",
            label="Real AUM / employee",
        )

    add_era_shading(ax)
    ax.set_title(group, fontsize=11, color=GROUP_COLORS[group])
    ax.set_xlabel("Year")
    ax.set_ylabel("2025 $000 / employee")
    ax.set_xlim(1950, 2025)
    panel_style(ax)


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
    cpi = load_cpi(args.cpi)
    merged = df.merge(cpi, on="year", how="left")

    base_cpi = float(cpi.loc[cpi["year"] == 2025, "cpiu_annual_avg"].iloc[0])
    merged["inflation_factor"] = base_cpi / merged["cpiu_annual_avg"]
    merged["real_revenue_per_employee"] = (merged["revt"] * merged["inflation_factor"]) / merged["emp"]
    merged["real_aum_per_employee"] = (merged["aum_crsp"] * merged["inflation_factor"]) / merged["emp"]
    merged = merged.replace([float("inf"), float("-inf")], pd.NA)

    fig, axes = plt.subplots(3, 2, figsize=(13.8, 10.8), sharex=True, constrained_layout=False)
    axes_flat = axes.flatten()
    fig.suptitle("Inflation-Adjusted Productivity Trends by Firm Group", fontsize=14, y=0.985)

    for idx, group in enumerate(GROUP_ORDER):
        plot_group(axes_flat[idx], merged, group)
        if idx % 2 == 1:
            axes_flat[idx].set_ylabel("")

    axes_flat[-1].axis("off")

    metric_handles = [
        Line2D([0], [0], color="#4E79A7", lw=2.0, marker="o", markersize=4, label="Real revenue / employee"),
        Line2D([0], [0], color="#777777", lw=2.0, marker="s", markersize=4, linestyle="--", label="Real AUM / employee"),
    ]
    era_patches = [Patch(facecolor=color, edgecolor="none", alpha=0.22, label=label) for _, _, label, color in ERA_SPANS]

    fig.legend(
        handles=era_patches,
        loc="upper center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 0.965),
    )
    fig.legend(
        handles=metric_handles,
        loc="upper center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 0.91),
    )
    fig.subplots_adjust(left=0.07, right=0.98, top=0.93, bottom=0.07, hspace=0.30, wspace=0.12)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figure to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
