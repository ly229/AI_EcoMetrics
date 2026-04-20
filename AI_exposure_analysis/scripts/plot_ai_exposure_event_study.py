#!/usr/bin/env python3
"""Plot an event-study style view of AI exposure dynamics.

The figure aligns each firm around the first year its filing-based AI exposure
exceeds its own early-period baseline by a fixed margin. This is a descriptive
event-study style plot, not a causal treatment effect.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_INPUT = Path("AI_exposure_analysis/data/ai_exposure_by_firm_year.csv")
DEFAULT_OUTPUT = Path("AI_exposure_analysis/figures/ai_exposure_event_study.png")
DEFAULT_TABLE = Path("AI_exposure_analysis/outputs/sec_ai_exposure_pipeline/ai_exposure_event_time.csv")
DEFAULT_BASELINE_YEARS = "2015,2016,2017"
DEFAULT_WINDOW = 4
DEFAULT_THRESHOLD = 0.10

FIRM_COLORS = {
    "BAC": "#59A14F",
    "BK": "#9C755F",
    "JPM": "#F28E2B",
    "SPGI": "#7E7D7A",
    "STT": "#4E79A7",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plot an event-study style AI exposure figure.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="AI exposure CSV path.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output figure path.")
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE, help="Output event-time table path.")
    parser.add_argument(
        "--baseline-years",
        type=str,
        default=DEFAULT_BASELINE_YEARS,
        help="Comma-separated years used to compute the firm baseline exposure.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Absolute increase above the baseline that defines the event year.",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=DEFAULT_WINDOW,
        help="Years before and after the event to display.",
    )
    return parser


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["ai_exposure"] = pd.to_numeric(df["ai_exposure"], errors="coerce")
    df = df.dropna(subset=["ticker", "year", "ai_exposure"]).copy()
    return df


def find_event_year(group: pd.DataFrame, baseline_years: list[int], threshold: float) -> int | None:
    baseline = group.loc[group["year"].isin(baseline_years), "ai_exposure"].mean()
    if pd.isna(baseline):
        return None
    cutoff = baseline + threshold
    event_years = group.loc[group["ai_exposure"] >= cutoff, "year"].sort_values()
    if event_years.empty:
        return None
    return int(event_years.iloc[0])


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    baseline_years = [int(x) for x in args.baseline_years.split(",") if x.strip()]

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif", "STIX Two Text"],
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )

    df = load_data(args.input)

    event_rows = []
    aligned_rows = []

    for ticker, group in df.groupby("ticker", observed=True):
        group = group.sort_values("year").reset_index(drop=True)
        event_year = find_event_year(group, baseline_years, args.threshold)
        if event_year is None:
            continue

        group = group.assign(event_year=event_year)
        group["event_time"] = group["year"] - group["event_year"]

        # Keep the display window tight around the event.
        windowed = group.loc[group["event_time"].between(-args.window, args.window)].copy()
        if windowed.empty:
            continue

        event_rows.append(
            {
                "ticker": ticker,
                "event_year": event_year,
                "baseline_mean": float(group.loc[group["year"].isin(baseline_years), "ai_exposure"].mean()),
                "pre_event_obs": int((windowed["event_time"] < 0).sum()),
                "post_event_obs": int((windowed["event_time"] >= 0).sum()),
            }
        )
        aligned_rows.extend(windowed[["ticker", "year", "event_year", "event_time", "ai_exposure"]].to_dict("records"))

    if not event_rows:
        raise SystemExit("No firms met the event definition. Try lowering --threshold.")

    aligned = pd.DataFrame(aligned_rows)
    aligned["log_ai_exposure"] = aligned["ai_exposure"].apply(lambda x: math.log1p(float(x)))

    summary = (
        aligned.groupby("event_time", as_index=False)
        .agg(
            mean_log_ai_exposure=("log_ai_exposure", "mean"),
            sd_log_ai_exposure=("log_ai_exposure", "std"),
            n_firms=("ticker", "nunique"),
        )
        .sort_values("event_time")
    )
    summary["se_log_ai_exposure"] = summary["sd_log_ai_exposure"] / summary["n_firms"].pow(0.5)
    summary["ci_low"] = summary["mean_log_ai_exposure"] - 1.96 * summary["se_log_ai_exposure"]
    summary["ci_high"] = summary["mean_log_ai_exposure"] + 1.96 * summary["se_log_ai_exposure"]

    event_info = pd.DataFrame(event_rows).sort_values("event_year")
    args.table.parent.mkdir(parents=True, exist_ok=True)
    event_info.to_csv(args.table, index=False)

    fig, ax = plt.subplots(figsize=(10.5, 6.0))
    fig.suptitle("Event-Study Style AI Exposure Dynamics", fontsize=14, y=0.98)

    for ticker, group in aligned.groupby("ticker", observed=True):
        group = group.sort_values("event_time")
        color = FIRM_COLORS.get(ticker, "#555555")
        ax.plot(
            group["event_time"],
            group["log_ai_exposure"],
            marker="o",
            markersize=4,
            linewidth=1.7,
            alpha=0.75,
            color=color,
            label=ticker,
        )

    ax.plot(
        summary["event_time"],
        summary["mean_log_ai_exposure"],
        color="#111111",
        linewidth=2.6,
        marker="o",
        markersize=4.5,
        label="Mean",
    )
    ax.fill_between(
        summary["event_time"],
        summary["ci_low"],
        summary["ci_high"],
        color="#111111",
        alpha=0.12,
        linewidth=0,
        label="95% CI",
    )
    ax.axvline(0, color="#666666", linestyle="--", linewidth=1.0)
    ax.axhline(0, color="#888888", linestyle=":", linewidth=0.9)
    ax.axvspan(-0.5, 0.5, color="#E8B7B7", alpha=0.16, lw=0)

    ax.set_xlabel("Event time")
    ax.set_ylabel("log(1 + AI exposure)")
    ax.set_xlim(-args.window, args.window)
    ax.grid(axis="y", alpha=0.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    note = (
        f"Event definition: first year ai_exposure exceeds the firm's 2015-2017 mean by {args.threshold:.2f}.\n"
        "This is descriptive alignment, not a causal treatment effect."
    )
    fig.text(0.02, 0.02, note, fontsize=9, color="#444444")
    ax.legend(frameon=False, ncol=2, loc="upper left")
    fig.subplots_adjust(left=0.10, right=0.98, top=0.90, bottom=0.14)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figure to {args.output}")
    print(f"saved event-time table to {args.table}")
    print(event_info.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
