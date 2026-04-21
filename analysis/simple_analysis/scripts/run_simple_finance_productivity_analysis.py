#!/usr/bin/env python3
"""Run a simple productivity analysis on the Compustat firm panel.

This script is intentionally minimal:
- main outcome: log(revenue per employee)
- secondary outcome: log(AUM per employee) when available
- model: firm fixed effects + era dummies

The goal is a first-pass descriptive regression, not a causal design.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


DEFAULT_INPUT = Path("data/compustat_panel_by_firm_group.csv")
DEFAULT_OUTPUT_DIR = Path("outputs/simple_analysis")

ERA_BINS = [1949, 1979, 1990, 2015, 2100]
ERA_LABELS = [
    "Pre-computerization",
    "Computerization",
    "Indexing",
    "AI",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simple finance productivity analysis.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for output tables (default: {DEFAULT_OUTPUT_DIR})",
    )
    return parser


def load_panel(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["emp"] = pd.to_numeric(df["emp"], errors="coerce")
    df["revt"] = pd.to_numeric(df["revt"], errors="coerce")
    df["aum_crsp"] = pd.to_numeric(df["aum_crsp"], errors="coerce")
    df["revenue_per_employee"] = df["revt"] / df["emp"]
    df["aum_per_employee"] = df["aum_crsp"] / df["emp"]
    df = df.replace([np.inf, -np.inf], np.nan)
    df["era"] = pd.cut(df["year"], bins=ERA_BINS, labels=ERA_LABELS)
    return df


def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("era", dropna=True)
        .agg(
            n_obs=("firm", "size"),
            n_firms=("firm", "nunique"),
            mean_emp=("emp", "mean"),
            mean_rev=("revt", "mean"),
            mean_revenue_per_employee=("revenue_per_employee", "mean"),
            median_revenue_per_employee=("revenue_per_employee", "median"),
            mean_aum_per_employee=("aum_per_employee", "mean"),
            median_aum_per_employee=("aum_per_employee", "median"),
        )
        .reset_index()
    )
    return summary


def run_fe_regression(df: pd.DataFrame, outcome: str):
    use = df.copy().dropna(subset=[outcome, "firm_group", "era"])

    # Firm fixed effects + era dummies.
    # The base era is Pre-computerization.
    formula = f"np.log1p({outcome}) ~ C(era, Treatment(reference='Pre-computerization')) + C(firm_group)"
    model = smf.ols(formula=formula, data=use).fit(cov_type="HC1")
    return model, use


def save_regression_table(model, path: Path, title: str) -> None:
    lines = []
    lines.append(title)
    lines.append("")
    lines.append(f"N = {int(model.nobs)}")
    lines.append(f"R-squared = {model.rsquared:.3f}")
    lines.append("")

    params = model.params
    ses = model.bse
    pvals = model.pvalues
    for name in params.index:
        if name == "Intercept":
            continue
        coef = params[name]
        se = ses[name]
        p = pvals[name]
        stars = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
        lines.append(f"{name}: {coef:.4f} ({se:.4f}){stars}")

    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    df = load_panel(args.input)
    outdir = args.output_dir
    outdir.mkdir(parents=True, exist_ok=True)

    summary = build_summary_table(df)
    summary_path = outdir / "era_summary.csv"
    summary.to_csv(summary_path, index=False)

    rev_model, rev_use = run_fe_regression(df, "revenue_per_employee")
    rev_table_path = outdir / "revenue_per_employee_fe.txt"
    save_regression_table(rev_model, rev_table_path, "Firm FE regression: log(revenue per employee)")

    aum_model, aum_use = run_fe_regression(df, "aum_per_employee")
    aum_table_path = outdir / "aum_per_employee_fe.txt"
    save_regression_table(aum_model, aum_table_path, "Firm FE regression: log(AUM per employee)")

    print(f"Saved era summary to {summary_path}")
    print(f"Saved revenue regression summary to {rev_table_path}")
    print(f"Saved AUM regression summary to {aum_table_path}")
    print()
    print(summary.to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
    print()
    print("Revenue per employee model:")
    print(rev_model.summary().tables[1].as_text())
    print()
    print("AUM per employee model:")
    print(aum_model.summary().tables[1].as_text())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
