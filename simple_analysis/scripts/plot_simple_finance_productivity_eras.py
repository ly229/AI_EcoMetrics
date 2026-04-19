#!/usr/bin/env python3
"""Plot simple productivity trends by era for the Compustat firm panel."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator
import pandas as pd


DEFAULT_INPUT = Path("data/compustat_panel_by_firm_group.csv")
DEFAULT_OUTPUT = Path("outputs/figures/simple_finance_productivity_eras.png")

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
    parser = argparse.ArgumentParser(description="Plot simple finance productivity trends by era.")
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
    df["era"] = pd.cut(df["year"], bins=ERA_BINS, labels=ERA_LABELS)
    return df


def build_era_group_table(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    grouped = (
        df.dropna(subset=[value_col, "era", "firm_group"])
        .groupby(["era", "firm_group"], observed=True)
        .agg(mean_value=(value_col, "mean"))
        .reset_index()
    )
    return grouped


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


def plot_panel(ax, df: pd.DataFrame, value_col: str, title: str, ylabel: str) -> None:
    table = build_era_group_table(df, value_col)

    for group in GROUP_ORDER:
        sub = (
            df.dropna(subset=[value_col, "year", "firm_group"])
            .loc[df["firm_group"] == group, ["year", value_col]]
            .groupby("year", as_index=False)
            .agg(mean_value=(value_col, "mean"))
        )
        if sub.empty:
            continue
        ax.plot(
            sub["year"],
            sub["mean_value"],
            marker="o",
            linewidth=1.8,
            markersize=3.2,
            color=GROUP_COLORS[group],
            label=group,
        )

    add_era_shading(ax)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel(ylabel)
    ax.set_xlim(1950, 2025)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.grid(axis="y", alpha=0.25)
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
            "legend.fontsize": 9,
        }
    )

    df = load_panel(args.input)

    fig, axes = plt.subplots(2, 1, figsize=(11.5, 8.5), constrained_layout=False)
    fig.suptitle("Simple Productivity Trends in Financial Firms", fontsize=14, y=0.98)

    plot_panel(
        axes[0],
        df,
        "revenue_per_employee",
        "Revenue per Employee by Era",
        "Revenue / employee",
    )
    plot_panel(
        axes[1],
        df,
        "aum_per_employee",
        "AUM per Employee by Era",
        "AUM / employee",
    )
    axes[1].set_xlabel("Era")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False)
    era_patches = [Patch(facecolor=color, edgecolor="none", alpha=0.22, label=label) for _, _, label, color in ERA_SPANS]
    fig.legend(
        handles=era_patches,
        loc="upper center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 0.965),
    )
    fig.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.12, hspace=0.28)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figure to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
