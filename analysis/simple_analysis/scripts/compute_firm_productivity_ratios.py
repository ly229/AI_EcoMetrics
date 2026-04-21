#!/usr/bin/env python3
"""Compute annual AUM/employee and revenue/employee series from the firm panel."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path("Data/compustat_panel_by_firm_group.csv")
DEFAULT_OUTPUT = Path("outputs/tables/annual_firm_productivity_ratios.csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute annual AUM/employee and revenue/employee ratios from the firm panel."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT})",
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


def build_annual_series(df: pd.DataFrame) -> pd.DataFrame:
    annual = (
        df.groupby("year", dropna=True)
        .agg(
            n_obs=("firm_group", "size"),
            n_firms=("firm_group", "nunique"),
            aum_total=("aum_crsp", "sum"),
            emp_total=("emp", "sum"),
            rev_total=("revt", "sum"),
            aum_per_employee_mean=("aum_per_employee", "mean"),
            aum_per_employee_median=("aum_per_employee", "median"),
            revenue_per_employee_mean=("revenue_per_employee", "mean"),
            revenue_per_employee_median=("revenue_per_employee", "median"),
        )
        .reset_index()
    )
    annual["aum_per_employee_total"] = annual["aum_total"] / annual["emp_total"]
    annual["revenue_per_employee_total"] = annual["rev_total"] / annual["emp_total"]
    return annual


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    df = load_panel(args.input)
    annual = build_annual_series(df)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    annual.to_csv(args.output, index=False)

    print(f"saved annual ratios to {args.output}")
    print()
    print(annual.head(8).to_string(index=False, float_format=lambda x: f"{x:,.3f}"))
    print()
    print(annual.tail(8).to_string(index=False, float_format=lambda x: f"{x:,.3f}"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
