#!/usr/bin/env python3
"""Fetch Compustat North America annual fundamentals for one or more tickers.

Loads WRDS credentials from a local `.env` file if present, then connects to
WRDS and exports the result to CSV.
"""

from __future__ import annotations

import argparse
import builtins
import os
from contextlib import contextmanager
from pathlib import Path

import pandas as pd


DEFAULT_OUTPUT = Path("Data/compustat_annual_fundamentals.csv")
ENV_PATH = Path(".env")
DEFAULT_TICKERS = ["SPGI"]


def load_env_file(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@contextmanager
def suppress_pgpass_prompt() -> None:
    original_input = builtins.input
    builtins.input = lambda *args, **kwargs: "n"
    try:
        yield
    finally:
        builtins.input = original_input


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pull Compustat North America annual fundamentals for one or more tickers."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=DEFAULT_TICKERS,
        help="One or more tickers to pull (default: SPGI).",
    )
    return parser


def fetch_compustat_panel(tickers: list[str]) -> pd.DataFrame:
    load_env_file()

    try:
        import wrds
    except ImportError as exc:
        raise SystemExit(
            "The wrds package is not installed. Install it first with `python -m pip install wrds pandas`."
        ) from exc

    if not os.environ.get("WRDS_USERNAME") or not os.environ.get("WRDS_PASSWORD"):
        raise SystemExit("WRDS_USERNAME and WRDS_PASSWORD must be set in .env or your shell.")

    with suppress_pgpass_prompt():
        conn = wrds.Connection(
            wrds_username=os.environ["WRDS_USERNAME"],
            wrds_password=os.environ["WRDS_PASSWORD"],
        )
    tickers_sql = ", ".join(f"'{ticker.upper()}'" for ticker in tickers)
    sql = f"""
        select
            gvkey,
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
          and tic in ({tickers_sql})
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

    df = fetch_compustat_panel(args.tickers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"saved {len(df):,} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
