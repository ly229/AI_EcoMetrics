#!/usr/bin/env python3
"""Run the SEC filing exposure pipeline end-to-end.

Steps:
1. Fetch 10-K filings and optionally download raw filing text.
2. Build a text-based AI exposure series from the filing corpus.
3. Run the panel fixed-effects regression using the exposure series.

This is the reproducible analysis entry point for the SEC-based AI exposure
workflow.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_TICKERS = ["SPGI", "STT", "JPM", "BAC", "BK"]
DEFAULT_START_YEAR = 1993
DEFAULT_END_YEAR = 2025
DEFAULT_OUTPUT_DIR = Path("AI_exposure_analysis/outputs/sec_ai_exposure_pipeline")
DEFAULT_MANIFEST = Path("AI_exposure_analysis/data/sec_10k_manifest.csv")
DEFAULT_TEXT_DIR = Path("AI_exposure_analysis/data/sec_10k_text")
DEFAULT_EXPOSURE = Path("AI_exposure_analysis/data/ai_exposure_by_firm_year.csv")
REPO_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the SEC 10-K AI exposure pipeline.")
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS, help="Ticker symbols to query.")
    parser.add_argument("--start-year", type=int, default=DEFAULT_START_YEAR, help="First filing year to include.")
    parser.add_argument("--end-year", type=int, default=DEFAULT_END_YEAR, help="Last filing year to include.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="SEC filing manifest path.")
    parser.add_argument("--text-dir", type=Path, default=DEFAULT_TEXT_DIR, help="Directory for downloaded filing text.")
    parser.add_argument("--exposure", type=Path, default=DEFAULT_EXPOSURE, help="Output AI exposure CSV path.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for final analysis outputs.")
    parser.add_argument(
        "--limit-per-ticker",
        type=int,
        default=0,
        help="Optional maximum number of filings to keep per ticker. 0 means no limit.",
    )
    parser.add_argument(
        "--outcomes",
        type=str,
        default="revenue_per_employee,aum_per_employee,labor_expense_per_employee",
        help="Comma-separated outcomes for the panel FE stage.",
    )
    parser.add_argument(
        "--allow-fallback",
        action="store_true",
        help="Allow a temporary fallback exposure proxy if the filing series is unavailable.",
    )
    return parser


def run_step(cmd: list[str]) -> None:
    result = subprocess.run(cmd, check=False, cwd=REPO_ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    fetch_cmd = [
        sys.executable,
        str(REPO_ROOT / "AI_exposure_analysis/scripts/fetch_sec_10k_filings.py"),
        "--tickers",
        *args.tickers,
        "--start-year",
        str(args.start_year),
        "--end-year",
        str(args.end_year),
        "--output",
        str(args.manifest),
        "--text-dir",
        str(args.text_dir),
        "--limit-per-ticker",
        str(args.limit_per_ticker),
        "--download-text",
    ]

    build_cmd = [
        sys.executable,
        str(REPO_ROOT / "AI_exposure_analysis/scripts/build_ai_exposure_from_filings.py"),
        "--manifest",
        str(args.manifest),
        "--panel",
        "simple_analysis/data/compustat_panel_by_firm_group.csv",
        "--output",
        str(args.exposure),
    ]

    fe_cmd = [
        sys.executable,
        str(REPO_ROOT / "AI_exposure_analysis/scripts/run_ai_exposure_panel_fe.py"),
        "--panel",
        "simple_analysis/data/compustat_panel_by_firm_group.csv",
        "--exposure",
        str(args.exposure),
        "--output-dir",
        str(args.output_dir),
        "--outcomes",
        args.outcomes,
    ]
    if args.allow_fallback:
        fe_cmd.append("--allow-fallback")

    run_step(fetch_cmd)
    run_step(build_cmd)
    run_step(fe_cmd)

    print(f"Pipeline complete. Outputs saved under {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
