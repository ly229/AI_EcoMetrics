#!/usr/bin/env python3
"""Fetch Compustat North America annual fundamentals for SP Global Inc. (SPGI).

This script expects WRDS access to be configured locally, either through the
WRDS Python client login flow or through an existing credential setup.

Default output:
    Data/spgi_compustat_annual.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_OUTPUT = Path("Data/spgi_compustat_annual.csv")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pull Compustat North America annual fundamentals for ticker SPGI."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV output path (default: {DEFAULT_OUTPUT})",
    )
    return parser


def fetch_compustat_panel() -> pd.DataFrame:
    try:
        import wrds
    except ImportError as exc:
        raise SystemExit(
            "The wrds package is not installed. Install it first with `python -m pip install wrds pandas`."
        ) from exc

    conn = wrds.Connection()
    sql = """
        select
            datadate as date,
            fyear,
            indfmt,
            tic,
            conm,
            at,
            emp,
            revt,
            xlr
        from comp.funda
        where indfmt = 'INDL'
          and datafmt = 'STD'
          and popsrc = 'D'
          and consol = 'C'
          and tic = 'SPGI'
        order by datadate
    """

    try:
        df = conn.raw_sql(sql)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    df = fetch_compustat_panel()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"saved {len(df):,} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

