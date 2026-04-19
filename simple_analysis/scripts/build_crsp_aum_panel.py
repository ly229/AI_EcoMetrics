#!/usr/bin/env python3
"""Build an annual CRSP mutual-fund AUM panel and merge it into the current dataset.

The script maps CRSP management-company names to the project firms, aggregates
monthly total net assets (TNA) to year-end firm-level AUM, and merges the result
onto the existing Compustat panel.
"""

from __future__ import annotations

import argparse
import builtins
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

import pandas as pd


ENV_PATH = Path(".env")
DEFAULT_BASE_PANEL = Path("Data/compustat_combined_panel.csv")
DEFAULT_AUM_PANEL = Path("Data/crsp_aum_firm_year.csv")
DEFAULT_MERGED_PANEL = Path("Data/compustat_combined_panel_with_aum.csv")
DEFAULT_START_DATE = "1962-01-01"

FIRM_PATTERNS = {
    "STT": ["STATE STREET"],
    "JPM": ["JPMORGAN"],
    "BAC": ["BANK OF AMERICA", "MERRILL LYNCH"],
    "BK": ["BNY MELLON", "DREYFUS", "BANK OF NEW YORK"],
}


def load_env_file(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@contextmanager
def suppress_pgpass_prompt() -> Iterable[None]:
    original_input = builtins.input
    builtins.input = lambda *args, **kwargs: "n"
    try:
        yield
    finally:
        builtins.input = original_input


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aggregate CRSP mutual fund AUM by firm-year.")
    parser.add_argument("--base-panel", type=Path, default=DEFAULT_BASE_PANEL)
    parser.add_argument("--aum-panel", type=Path, default=DEFAULT_AUM_PANEL)
    parser.add_argument("--merged-panel", type=Path, default=DEFAULT_MERGED_PANEL)
    parser.add_argument("--start-date", type=str, default=DEFAULT_START_DATE)
    return parser


def connect_wrds():
    load_env_file()

    try:
        import wrds
    except ImportError as exc:
        raise SystemExit(
            "The wrds package is not installed. Install it first with `uv pip install wrds pandas`."
        ) from exc

    username = os.environ.get("WRDS_USERNAME")
    password = os.environ.get("WRDS_PASSWORD")
    if not username or not password:
        raise SystemExit("WRDS_USERNAME and WRDS_PASSWORD must be set in .env or your shell.")

    with suppress_pgpass_prompt():
        return wrds.Connection(wrds_username=username, wrds_password=password)


def classify_firm(mgmt_name: str) -> str | None:
    if pd.isna(mgmt_name):
        return None
    text = str(mgmt_name).upper()
    for firm, patterns in FIRM_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            return firm
    return None


def chunked(values: list[int], size: int = 400) -> Iterable[list[int]]:
    for idx in range(0, len(values), size):
        yield values[idx : idx + size]


def fetch_fund_headers(db) -> pd.DataFrame:
    hdr = db.get_table(
        library="crsp",
        table="fund_hdr",
        columns=["crsp_fundno", "mgmt_name", "ticker", "fund_name"],
    )
    hdr["firm"] = hdr["mgmt_name"].map(classify_firm)
    return hdr.dropna(subset=["firm"]).copy()


def fetch_monthly_tna(db, fundnos: list[int], start_date: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for group in chunked(fundnos):
        fund_list = ", ".join(str(int(f)) for f in group)
        sql = f"""
            select crsp_fundno, caldt, mtna
            from crsp.monthly_tna
            where crsp_fundno in ({fund_list})
              and caldt >= '{start_date}'
        """
        frames.append(db.raw_sql(sql))
    out = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["crsp_fundno", "caldt", "mtna"])
    out["caldt"] = pd.to_datetime(out["caldt"])
    return out


def build_aum_panel(db, start_date: str) -> pd.DataFrame:
    hdr = fetch_fund_headers(db)
    fund_map = hdr[["crsp_fundno", "firm"]].drop_duplicates()
    tna = fetch_monthly_tna(db, fund_map["crsp_fundno"].astype(int).tolist(), start_date)
    merged = tna.merge(fund_map, on="crsp_fundno", how="left")
    merged = merged[merged["caldt"].dt.month == 12].copy()
    merged["year"] = merged["caldt"].dt.year
    aum = (
        merged.groupby(["firm", "year"], as_index=False)
        .agg(aum_crsp=("mtna", "sum"), matched_funds=("crsp_fundno", "nunique"))
        .sort_values(["year", "firm"])
        .reset_index(drop=True)
    )
    return aum


def merge_with_base_panel(base_panel: pd.DataFrame, aum_panel: pd.DataFrame) -> pd.DataFrame:
    base = base_panel.copy()
    if "date" in base.columns:
        base["year"] = pd.to_datetime(base["date"]).dt.year
    elif "fyear" in base.columns:
        base["year"] = base["fyear"].astype(int)
    else:
        raise ValueError("Base panel must contain either `date` or `fyear`.")

    base["firm"] = base["tic"].astype(str).str.upper()
    merged = base.merge(aum_panel, on=["firm", "year"], how="left")
    merged = merged.sort_values(["date", "conm", "tic"]).reset_index(drop=True)
    return merged


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.base_panel.exists():
        raise SystemExit(f"Base panel not found: {args.base_panel}")

    with connect_wrds() as db:
        aum_panel = build_aum_panel(db, args.start_date)

    args.aum_panel.parent.mkdir(parents=True, exist_ok=True)
    aum_panel.to_csv(args.aum_panel, index=False)

    base = pd.read_csv(args.base_panel)
    merged = merge_with_base_panel(base, aum_panel)
    merged.to_csv(args.merged_panel, index=False)

    print(f"saved {len(aum_panel):,} firm-year rows to {args.aum_panel}")
    print(f"saved {len(merged):,} rows to {args.merged_panel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
