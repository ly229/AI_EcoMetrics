#!/usr/bin/env python3
"""Plot the AI exposure fixed-effects results as a coefficient figure."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


DEFAULT_MERGED = Path("AI_exposure_analysis/outputs/sec_ai_exposure_pipeline/merged_panel_with_exposure.csv")
DEFAULT_OUTPUT = Path("AI_exposure_analysis/figures/ai_exposure_fe_coefficients.png")
DEFAULT_OUTCOMES = [
    "revenue_per_employee",
    "aum_per_employee",
    "labor_expense_per_employee",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plot AI exposure FE coefficients across outcomes.")
    parser.add_argument("--merged", type=Path, default=DEFAULT_MERGED, help="Merged panel CSV path.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output figure path.")
    parser.add_argument(
        "--outcomes",
        type=str,
        default=",".join(DEFAULT_OUTCOMES),
        help="Comma-separated outcomes to plot.",
    )
    parser.add_argument(
        "--entity-col",
        type=str,
        default="firm",
        help="Panel entity column used in the fixed effects specification.",
    )
    parser.add_argument(
        "--year-col",
        type=str,
        default="year",
        help="Year column used in the fixed effects specification.",
    )
    return parser


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["year", "ai_exposure", "revenue_per_employee", "aum_per_employee", "labor_expense_per_employee"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def fit_model(df: pd.DataFrame, outcome: str, entity_col: str, year_col: str):
    use = df.dropna(subset=[outcome, "ai_exposure", entity_col, year_col]).copy()
    formula = f"np.log1p({outcome}) ~ ai_exposure + C({year_col}) + C({entity_col})"
    model = smf.ols(formula=formula, data=use).fit(cov_type="HC1")
    return model, use


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    outcomes = [o.strip() for o in args.outcomes.split(",") if o.strip()]

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif", "STIX Two Text"],
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
        }
    )

    df = load_panel(args.merged)

    rows = []
    for outcome in outcomes:
        model, use = fit_model(df, outcome, args.entity_col, args.year_col)
        coef = float(model.params["ai_exposure"])
        se = float(model.bse["ai_exposure"])
        ci_low = coef - 1.96 * se
        ci_high = coef + 1.96 * se
        rows.append(
            {
                "outcome": outcome,
                "coef": coef,
                "se": se,
                "ci_low": ci_low,
                "ci_high": ci_high,
                "nobs": int(model.nobs),
                "r2": float(model.rsquared),
            }
        )

    result = pd.DataFrame(rows)
    result["label"] = result.apply(lambda r: f"{r['outcome'].replace('_', ' ')}\nN={r['nobs']}, R²={r['r2']:.3f}", axis=1)
    result = result.sort_values("coef").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    fig.suptitle("AI Exposure and Firm Outcomes: Fixed-Effects Coefficients", fontsize=14, y=0.98)

    y = range(len(result))
    ax.axvline(0, color="#666666", linewidth=1.0, linestyle="--")
    ax.errorbar(
        result["coef"],
        list(y),
        xerr=[
            result["coef"] - result["ci_low"],
            result["ci_high"] - result["coef"],
        ],
        fmt="o",
        color="#2F5D8A",
        ecolor="#2F5D8A",
        elinewidth=1.8,
        capsize=4,
        markersize=6,
    )
    ax.set_yticks(list(y))
    ax.set_yticklabels(result["label"])
    ax.set_xlabel("Coefficient on AI exposure in log1p(outcome) regression")
    ax.set_title("95% confidence intervals from firm and year fixed effects", fontsize=11)
    ax.grid(axis="x", alpha=0.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    note = (
        "Specification: log1p(outcome_it) ~ ai_exposure_it + firm FE + year FE\n"
        "Standard errors: HC1 robust"
    )
    fig.text(0.02, 0.02, note, fontsize=9, color="#444444")
    fig.subplots_adjust(left=0.38, right=0.98, top=0.86, bottom=0.16)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"saved figure to {args.output}")
    print(result.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
