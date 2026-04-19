#!/usr/bin/env python3
"""Plot histogram views of productivity ratios by era for the Compustat panel."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_INPUT = Path("data/compustat_panel_by_firm_group.csv")
DEFAULT_OUTPUT = Path("outputs/figures/simple_finance_productivity_histograms.png")

ERA_ORDER = [
    "Pre-computerization\n(before 1980)",
    "Computerization\n(1980-1990)",
    "Indexing\n(1990-2015)",
    "AI\n(2015-present)",
]
ERA_BINS = [1949, 1979, 1990, 2015, 2100]
PALETTE = ["#7E7D7A", "#4E79A7", "#F28E2B", "#E15759"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plot productivity-ratio histograms by era.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output figure path.")
    return parser


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["emp"] = pd.to_numeric(df["emp"], errors="coerce")
    df["revt"] = pd.to_numeric(df["revt"], errors="coerce")
    df["aum_crsp"] = pd.to_numeric(df["aum_crsp"], errors="coerce")
    df["revenue_per_employee"] = df["revt"] / df["emp"]
    df["aum_per_employee"] = df["aum_crsp"] / df["emp"]
    df = df.replace([float("inf"), float("-inf")], pd.NA)
    df["era"] = pd.cut(df["year"], bins=ERA_BINS, labels=ERA_ORDER, right=True)
    return df


def prep_ratio(df: pd.DataFrame, value_col: str) -> pd.Series:
    series = df[value_col].dropna()
    series = series[series > 0]
    return series.map(lambda x: math.log10(float(x)))


def hist_bounds(series: pd.Series) -> tuple[float, float]:
    low = float(series.quantile(0.05))
    high = float(series.quantile(0.95))
    if not math.isfinite(low) or not math.isfinite(high) or low == high:
        low = float(series.min())
        high = float(series.max())
    pad = (high - low) * 0.12 if high > low else 0.5
    return low - pad, high + pad


def plot_panel(ax, series: pd.Series, title: str, xlabel: str, color: str) -> None:
    if series.empty:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes, fontsize=10)
        ax.set_axis_off()
        return

    lo, hi = hist_bounds(series)
    bins = 12 if len(series) < 40 else 16
    ax.hist(series, bins=bins, range=(lo, hi), color=color, alpha=0.88, edgecolor="white", linewidth=0.8)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Count")
    ax.grid(axis="y", alpha=0.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


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
        }
    )

    df = load_panel(args.input)

    fig, axes = plt.subplots(2, 4, figsize=(16, 7.2), constrained_layout=True)
    fig.suptitle("Distributions of Productivity Ratios by Era", fontsize=14, y=1.02)

    for idx, era in enumerate(ERA_ORDER):
        sub = df[df["era"] == era]
        era_aum = prep_ratio(sub, "aum_per_employee")
        era_rev = prep_ratio(sub, "revenue_per_employee")

        plot_panel(
            axes[0, idx],
            era_aum,
            era,
            "log10(AUM / employee)",
            PALETTE[idx],
        )
        plot_panel(
            axes[1, idx],
            era_rev,
            era,
            "log10(Revenue / employee)",
            PALETTE[idx],
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"saved figure to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
