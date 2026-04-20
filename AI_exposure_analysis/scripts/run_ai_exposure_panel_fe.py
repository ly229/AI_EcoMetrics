#!/usr/bin/env python3
"""Run a panel fixed-effects analysis with an AI exposure variable.

This script is designed as the next-step extension to the simple finance
productivity analysis. It supports two exposure modes:

1. External AI exposure file merged by firm and year.
2. Internal fallback proxy based on labor-expense intensity when no exposure
   file is provided.

The main specification is:

    log1p(outcome_it) = beta * ai_exposure_it + firm FE + year FE + error_it

The script is intentionally conservative: it is a flexible estimation wrapper,
not a claim that any fallback proxy is a true AI exposure measure.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


DEFAULT_PANEL = Path("simple_analysis/data/compustat_panel_by_firm_group.csv")
DEFAULT_EXPOSURE = Path("AI_exposure_analysis/data/ai_exposure_by_firm_year.csv")
DEFAULT_OUTPUT_DIR = Path("AI_exposure_analysis/outputs/ai_exposure_panel_fe")
DEFAULT_OUTCOMES = [
    "revenue_per_employee",
    "aum_per_employee",
    "labor_expense_per_employee",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run firm-panel FE regressions with AI exposure.")
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL, help="Panel CSV path.")
    parser.add_argument(
        "--exposure",
        type=Path,
        default=DEFAULT_EXPOSURE,
        help="AI exposure CSV path built from filing text.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for regression tables and merged data (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--outcomes",
        type=str,
        default=",".join(DEFAULT_OUTCOMES),
        help="Comma-separated outcomes to regress on AI exposure.",
    )
    parser.add_argument(
        "--entity-col",
        type=str,
        default="firm",
        help="Panel entity column for firm fixed effects.",
    )
    parser.add_argument(
        "--year-col",
        type=str,
        default="year",
        help="Year column in the panel.",
    )
    parser.add_argument(
        "--exposure-col",
        type=str,
        default="ai_exposure",
        help="Exposure column name in the exposure file.",
    )
    parser.add_argument(
        "--cov-type",
        type=str,
        default="HC1",
        choices=["HC1", "HC3"],
        help="Covariance estimator for the regression.",
    )
    parser.add_argument(
        "--allow-fallback",
        action="store_true",
        help="Allow a temporary fallback exposure proxy if the filing-based series is unavailable.",
    )
    return parser


def resolve_existing_path(path: Path, fallback_names: list[str] | None = None) -> Path:
    """Resolve a path, checking the repo's simple_analysis/data folder as needed."""

    if path.exists():
        return path

    fallback_names = fallback_names or []
    candidates = [Path(name) for name in fallback_names]
    if path.parts:
        candidates.append(Path("simple_analysis") / path)
        candidates.append(Path("Data") / path.name)
        candidates.append(Path("data") / path.name)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return path


def load_panel(path: Path, entity_col: str, year_col: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in [year_col, "emp", "revt", "aum_crsp", "xlr", "at"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "revenue_per_employee" not in df.columns:
        df["revenue_per_employee"] = df["revt"] / df["emp"]
    if "aum_per_employee" not in df.columns:
        df["aum_per_employee"] = df["aum_crsp"] / df["emp"]
    df["labor_expense_per_employee"] = df["xlr"] / df["emp"]

    df = df.replace([np.inf, -np.inf], np.nan)

    if entity_col not in df.columns:
        if "firm" in df.columns:
            df[entity_col] = df["firm"]
        elif "tic" in df.columns:
            df[entity_col] = df["tic"]
        elif "firm_group" in df.columns:
            df[entity_col] = df["firm_group"]
        else:
            raise ValueError("Could not infer a firm identifier column.")

    if year_col not in df.columns:
        raise ValueError(f"Year column '{year_col}' not found in panel.")

    return df


def load_exposure(path: Path, exposure_col: str, year_col: str) -> pd.DataFrame:
    exposure = pd.read_csv(path)
    exposure.columns = [c.strip().lower() for c in exposure.columns]

    if exposure_col not in exposure.columns:
        if "ai_exposure" in exposure.columns:
            exposure_col = "ai_exposure"
        else:
            raise ValueError(f"Exposure file must contain '{exposure_col}' or 'ai_exposure'.")

    if year_col not in exposure.columns:
        if "fyear" in exposure.columns:
            exposure[year_col] = pd.to_numeric(exposure["fyear"], errors="coerce")
        elif "year" in exposure.columns:
            exposure[year_col] = pd.to_numeric(exposure["year"], errors="coerce")
        elif "date" in exposure.columns:
            exposure["date"] = pd.to_datetime(exposure["date"], errors="coerce")
            exposure[year_col] = exposure["date"].dt.year
        else:
            raise ValueError("Exposure file must contain a year, fyear, or date column.")

    if "firm" not in exposure.columns and "tic" not in exposure.columns and "firm_group" not in exposure.columns:
        raise ValueError("Exposure file must contain a firm-, ticker-, or firm_group-level identifier.")

    exposure = exposure.rename(columns={exposure_col: "ai_exposure"})
    exposure[year_col] = pd.to_numeric(exposure[year_col], errors="coerce")
    return exposure


def build_fallback_exposure(df: pd.DataFrame) -> pd.DataFrame:
    """Create a transparent fallback exposure proxy when no external file is available.

    This is not a pure AI exposure measure. It is a simple intensity proxy that
    lets the panel FE workflow run before a text-based exposure series is built.
    """

    out = df.copy()
    tech_intensity = out["xlr"] / out["emp"]
    out["ai_exposure"] = np.log1p(tech_intensity)
    out["ai_exposure_source"] = "fallback_labor_expense_intensity"
    return out


def merge_exposure(
    panel: pd.DataFrame,
    exposure_path: Path | None,
    exposure_col: str,
    entity_col: str,
    year_col: str,
) -> pd.DataFrame:
    if exposure_path is None:
        return build_fallback_exposure(panel)

    exposure_path = resolve_existing_path(exposure_path)
    if not exposure_path.exists():
        return build_fallback_exposure(panel)

    exposure = load_exposure(exposure_path, exposure_col, year_col)

    join_key = None
    for candidate in ["firm", "tic", "firm_group"]:
        if candidate in panel.columns and candidate in exposure.columns:
            join_key = candidate
            break
    if join_key is None:
        raise ValueError(
            "Could not find a shared identifier to merge exposure with panel. "
            "Use firm, tic, or firm_group in both files."
        )

    merged = panel.merge(
        exposure,
        left_on=[join_key, year_col],
        right_on=[join_key, year_col],
        how="left",
        suffixes=("", "_exp"),
    )
    if "ai_exposure_exp" in merged.columns:
        merged["ai_exposure"] = merged["ai_exposure"].fillna(merged["ai_exposure_exp"])
        merged = merged.drop(columns=["ai_exposure_exp"])

    merged["ai_exposure_source"] = np.where(
        merged["ai_exposure"].notna(),
        f"external:{exposure_path.name}",
        "missing",
    )
    return merged


def fit_fe_model(df: pd.DataFrame, outcome: str, entity_col: str, year_col: str, cov_type: str):
    use = df.dropna(subset=[outcome, "ai_exposure", entity_col, year_col]).copy()
    formula = f"np.log1p({outcome}) ~ ai_exposure + C({year_col}) + C({entity_col})"
    model = smf.ols(formula=formula, data=use).fit(cov_type=cov_type)
    return model, use


def save_regression_table(model, path: Path, title: str) -> None:
    lines = [
        title,
        "",
        f"N = {int(model.nobs)}",
        f"R-squared = {model.rsquared:.3f}",
        "",
    ]

    for name in model.params.index:
        if name == "Intercept":
            continue
        coef = model.params[name]
        se = model.bse[name]
        pval = model.pvalues[name]
        stars = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
        lines.append(f"{name}: {coef:.4f} ({se:.4f}){stars}")

    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    panel_path = resolve_existing_path(args.panel)
    panel = load_panel(panel_path, args.entity_col, args.year_col)

    exposure_path = resolve_existing_path(args.exposure)
    if not exposure_path.exists():
        if args.allow_fallback:
            exposure_path = None
        else:
            raise FileNotFoundError(
                f"AI exposure file not found: {args.exposure}. "
                "Build it first with AI_exposure_analysis/scripts/build_ai_exposure_from_filings.py "
                "or pass --allow-fallback for a temporary placeholder."
            )

    merged = merge_exposure(panel, exposure_path, args.exposure_col, args.entity_col, args.year_col)

    outdir = args.output_dir
    outdir.mkdir(parents=True, exist_ok=True)
    merged_path = outdir / "merged_panel_with_exposure.csv"
    merged.to_csv(merged_path, index=False)

    outcomes = [o.strip() for o in args.outcomes.split(",") if o.strip()]
    summary_lines = [
        "# AI Exposure Panel FE Extension",
        "",
        f"Panel source: `{panel_path}`",
        f"Exposure source: `{exposure_path}`" if exposure_path is not None else "Exposure source: fallback labor-expense intensity proxy",
        "",
        "## Specification",
        "",
        f"`log1p(outcome_it) ~ ai_exposure_it + C({args.year_col}) + C({args.entity_col})`",
        "",
        "## Outputs",
        "",
        f"- merged panel: `{merged_path}`",
    ]

    for outcome in outcomes:
        model, _ = fit_fe_model(merged, outcome, args.entity_col, args.year_col, args.cov_type)
        table_path = outdir / f"{outcome}_ai_exposure_fe.txt"
        save_regression_table(model, table_path, f"Firm FE regression: log1p({outcome}) on AI exposure")
        summary_lines.append(f"- {outcome} regression: `{table_path}`")

    summary_path = outdir / "analysis_summary.md"
    summary_path.write_text("\n".join(summary_lines) + "\n")

    print(f"Saved merged panel to {merged_path}")
    print(f"Saved analysis summary to {summary_path}")
    for outcome in outcomes:
        print(f"Saved regression table for {outcome} to {outdir / f'{outcome}_ai_exposure_fe.txt'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
