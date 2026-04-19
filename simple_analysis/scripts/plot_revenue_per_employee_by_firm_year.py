#!/usr/bin/env python3
"""Plot revenue per employee over time by firm with era shading."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator
import pandas as pd


DEFAULT_INPUT = Path("data/compustat_panel_by_firm_group.csv")
DEFAULT_OUTPUT = Path("outputs/figures/revenue_per_employee_by_firm_year.png")

ERA_SPANS = [
    (1950, 1979, "Pre-computerization", "#D9D9D9"),
    (1980, 1989, "Computerization", "#BFD7EA"),
    (1990, 2014, "Indexing", "#F5D7A1"),
    (2015, 2025, "AI", "#E8B7B7"),
]

FIRM_ORDER = [
    "S&P Global",
    "State Street family",
    "JPMorgan family",
    "Bank of America / Merrill Lynch family",
    "BNY Mellon / Dreyfus family",
]

FIRM_COLORS = {
    "S&P Global": "#7E7D7A",
    "State Street family": "#4E79A7",
    "JPMorgan family": "#F28E2B",
    "Bank of America / Merrill Lynch family": "#59A14F",
    "BNY Mellon / Dreyfus family": "#E15759",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plot revenue per employee by firm and year.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output figure path.")
    return parser


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["emp"] = pd.to_numeric(df["emp"], errors="coerce")
    df["revt"] = pd.to_numeric(df["revt"], errors="coerce")
    df["revenue_per_employee"] = df["revt"] / df["emp"]
    df = df.replace([float("inf"), float("-inf")], pd.NA)
    return df


def add_era_shading(ax) -> None:
    for start, end, label, color in ERA_SPANS:
        ax.axvspan(start, end, color=color, alpha=0.20, lw=0)
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


def build_firm_series(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.dropna(subset=["year", "revenue_per_employee", "firm_group"])
        .assign(year_5y=lambda x: (x["year"] // 5) * 5)
        .groupby(["year_5y", "firm_group"], observed=True)
        .agg(mean_revenue_per_employee=("revenue_per_employee", "mean"))
        .reset_index()
        .sort_values(["firm_group", "year_5y"])
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif", "STIX Two Text"],
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
        }
    )

    df = load_panel(args.input)
    series = build_firm_series(df)

    fig, ax = plt.subplots(figsize=(12.0, 7.2))
    fig.suptitle("Revenue per Employee by Firm, with Era Shading", fontsize=15, y=0.98)

    add_era_shading(ax)

    bar_width = 0.8
    offsets = {
        firm: (idx - (len(FIRM_ORDER) - 1) / 2) * bar_width
        for idx, firm in enumerate(FIRM_ORDER)
    }

    for firm in FIRM_ORDER:
        sub = series[series["firm_group"] == firm]
        if sub.empty:
            continue
        ax.bar(
            sub["year_5y"] + offsets[firm],
            sub["mean_revenue_per_employee"],
            width=bar_width,
            color=FIRM_COLORS[firm],
            alpha=0.88,
            label=firm,
        )

    ax.set_xlabel("Year")
    ax.set_ylabel("Revenue per employee")
    ax.set_xlim(1950, 2025)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.grid(axis="y", alpha=0.25)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    era_handles = [Line2D([0], [0], color=color, lw=10, alpha=0.20, label=label) for _, _, label, color in ERA_SPANS]
    firm_handles = [
        Line2D([0], [0], color=FIRM_COLORS[firm], lw=8, alpha=0.88, label=firm)
        for firm in FIRM_ORDER
    ]
    leg1 = ax.legend(handles=firm_handles, loc="upper left", frameon=False, title="Firm")
    ax.add_artist(leg1)
    ax.legend(handles=era_handles, loc="upper right", frameon=False, title="Era")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figure to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
