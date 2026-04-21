#!/usr/bin/env python3
"""Plot five firm-group panels with AUM/employee and revenue/employee trends."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import LogLocator, NullFormatter, FuncFormatter, MultipleLocator
import pandas as pd


DEFAULT_INPUT = Path("Data/compustat_panel_by_firm_group.csv")
DEFAULT_OUTPUT = Path("outputs/figures/firm_group_productivity_small_multiples.png")

GROUP_ORDER = [
    "S&P Global",
    "State Street family",
    "JPMorgan family",
    "Bank of America / Merrill Lynch family",
    "BNY Mellon / Dreyfus family",
]

COLORS = {
    "aum": "#4E79A7",
    "revenue": "#F28E2B",
    "panel": {
        "S&P Global": "#7E7D7A",
        "State Street family": "#4E79A7",
        "JPMorgan family": "#F28E2B",
        "Bank of America / Merrill Lynch family": "#59A14F",
        "BNY Mellon / Dreyfus family": "#E15759",
    },
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plot five firm-group productivity panels.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output figure path.")
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
            aum_per_employee_mean=("aum_per_employee", "mean"),
            revenue_per_employee_mean=("revenue_per_employee", "mean"),
        )
        .reset_index()
        .sort_values(["firm_group", "year"])
    )
    return grouped


def style_axes(ax) -> None:
    ax.grid(axis="y", alpha=0.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_major_locator(LogLocator(base=10))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}" if x >= 1 else ""))


def plot_group(ax, df: pd.DataFrame, group: str) -> None:
    sub = df[df["firm_group"] == group].sort_values("year")
    color = COLORS["panel"][group]

    aum = sub[["year", "aum_per_employee_mean"]].dropna()
    rev = sub[["year", "revenue_per_employee_mean"]].dropna()

    if not aum.empty:
        ax.plot(
            aum["year"],
            aum["aum_per_employee_mean"],
            color=COLORS["aum"],
            linewidth=1.9,
            marker="o",
            markersize=3.7,
            label="AUM / employee",
        )

    if not rev.empty:
        ax.plot(
            rev["year"],
            rev["revenue_per_employee_mean"],
            color=COLORS["revenue"],
            linewidth=1.9,
            marker="s",
            markersize=3.4,
            linestyle="--",
            label="Revenue / employee",
        )

    ax.set_yscale("log")
    ax.set_title(group, fontsize=11, color=color)
    ax.set_xlabel("Year")
    ax.set_ylabel("Ratio")
    style_axes(ax)

    if aum.empty:
        ax.text(
            0.03,
            0.08,
            "AUM missing",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8.5,
            color="#555555",
        )

    if rev.empty:
        ax.text(
            0.03,
            0.03,
            "Revenue missing",
            transform=ax.transAxes,
            ha="left",
            va="bottom",
            fontsize=8.5,
            color="#555555",
        )


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

    fig, axes = plt.subplots(3, 2, figsize=(13.6, 10.8), sharex=True, sharey=True)
    axes_flat = axes.flatten()
    fig.suptitle("Firm-Group Productivity Trends", fontsize=14, y=0.985)

    for idx, group in enumerate(GROUP_ORDER):
        plot_group(axes_flat[idx], grouped, group)
        if idx % 2 == 1:
            axes_flat[idx].set_ylabel("")

    axes_flat[-1].axis("off")

    legend_handles = [
        Line2D([0], [0], color=COLORS["aum"], lw=1.9, marker="o", markersize=4, label="AUM / employee"),
        Line2D([0], [0], color=COLORS["revenue"], lw=1.9, marker="s", markersize=4, linestyle="--", label="Revenue / employee"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        ncol=2,
        frameon=False,
        bbox_to_anchor=(0.5, 0.02),
    )
    fig.subplots_adjust(left=0.07, right=0.98, top=0.93, bottom=0.08, hspace=0.28, wspace=0.12)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figure to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
