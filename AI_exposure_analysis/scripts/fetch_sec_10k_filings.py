#!/usr/bin/env python3
"""Fetch 10-K filings from the official SEC EDGAR endpoints.

This script uses only SEC-hosted data:

- `https://www.sec.gov/files/company_tickers.json`
- `https://data.sec.gov/submissions/CIK##########.json`
- `https://www.sec.gov/Archives/edgar/data/...`

It writes a manifest of 10-K filings and can optionally download the raw
filing text to a local directory for downstream AI-exposure scoring.

Required environment:

- `SEC_USER_AGENT`

Optional environment:

- `.env` file with `SEC_USER_AGENT=...`
"""

from __future__ import annotations

import argparse
import builtins
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd


DEFAULT_TICKERS = ["SPGI", "STT", "JPM", "BAC", "BK"]
DEFAULT_START_YEAR = 1993
DEFAULT_END_YEAR = 2025
DEFAULT_OUTPUT = Path("AI_exposure_analysis/data/sec_10k_manifest.csv")
DEFAULT_TEXT_DIR = Path("AI_exposure_analysis/data/sec_10k_text")
DEFAULT_SLEEP_SECONDS = 0.2
ENV_PATH = Path(".env")
SEC_TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accn_nodash}/{filename}"


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
def suppress_pgpass_prompt() -> None:
    original_input = builtins.input
    builtins.input = lambda *args, **kwargs: "n"
    try:
        yield
    finally:
        builtins.input = original_input


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch official SEC 10-K metadata and text.")
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS, help="Ticker symbols to query.")
    parser.add_argument("--start-year", type=int, default=DEFAULT_START_YEAR, help="First filing year to include.")
    parser.add_argument("--end-year", type=int, default=DEFAULT_END_YEAR, help="Last filing year to include.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV manifest path.")
    parser.add_argument(
        "--text-dir",
        type=Path,
        default=DEFAULT_TEXT_DIR,
        help="Directory for downloaded 10-K text files.",
    )
    parser.add_argument(
        "--download-text",
        action="store_true",
        help="Download raw filing text from the SEC archives into --text-dir.",
    )
    parser.add_argument(
        "--limit-per-ticker",
        type=int,
        default=0,
        help="Optional maximum number of filings to keep per ticker. 0 means no limit.",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=DEFAULT_SLEEP_SECONDS,
        help="Pause between SEC requests to stay polite (default: 0.2).",
    )
    parser.add_argument(
        "--user-agent",
        type=str,
        default=None,
        help="Override SEC_USER_AGENT for this run.",
    )
    return parser


def get_user_agent(cli_user_agent: str | None = None) -> str:
    load_env_file()
    user_agent = cli_user_agent or os.environ.get("SEC_USER_AGENT")
    if not user_agent:
        raise SystemExit(
            "SEC_USER_AGENT is not set. Add it to `.env` or your shell, for example:\n"
            'SEC_USER_AGENT="Your Name your.email@domain.com"'
        )
    return user_agent


def make_headers(user_agent: str) -> dict[str, str]:
    return {
        "User-Agent": user_agent,
        "Accept": "application/json, text/html, text/plain, */*",
    }


def fetch_json(url: str, headers: dict[str, str], sleep_seconds: float = 0.0) -> Any:
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    request = Request(url, headers=headers)
    try:
        with urlopen(request) as response:
            data = response.read()
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc
    return json.loads(data.decode("utf-8"))


def fetch_bytes(url: str, headers: dict[str, str], sleep_seconds: float = 0.0) -> bytes:
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    request = Request(url, headers=headers)
    try:
        with urlopen(request) as response:
            return response.read()
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Failed to fetch {url}: {exc}") from exc


def normalize_cik(cik: int | str) -> int:
    return int(str(cik).lstrip("0") or "0")


def cik_to_padded_str(cik: int | str) -> str:
    return f"{normalize_cik(cik):010d}"


def accession_nodash(accession_no: str) -> str:
    return str(accession_no).replace("-", "")


def company_ticker_map(headers: dict[str, str], sleep_seconds: float) -> dict[str, dict[str, Any]]:
    raw = fetch_json(SEC_TICKER_MAP_URL, headers=headers, sleep_seconds=sleep_seconds)
    out: dict[str, dict[str, Any]] = {}
    for _, rec in raw.items():
        ticker = str(rec.get("ticker", "")).upper()
        if not ticker:
            continue
        out[ticker] = rec
    return out


def fetch_submissions(cik: int, headers: dict[str, str], sleep_seconds: float) -> list[dict[str, Any]]:
    url = SEC_SUBMISSIONS_URL.format(cik=cik)
    root = fetch_json(url, headers=headers, sleep_seconds=sleep_seconds)

    records: list[dict[str, Any]] = []

    def extract_recent_block(payload: dict[str, Any]) -> dict[str, Any]:
        """Return the filing arrays from either SEC submissions schema variant."""

        if isinstance(payload, dict) and all(isinstance(v, list) for v in payload.values()):
            return payload
        return payload.get("filings", {}).get("recent", {})

    def extract_older_files(payload: dict[str, Any]) -> list[dict[str, Any]]:
        if isinstance(payload, dict) and "files" in payload:
            return payload.get("files", [])
        return payload.get("filings", {}).get("files", [])

    def append_from_payload(payload: dict[str, Any], source: str) -> None:
        recent = extract_recent_block(payload)
        if not recent:
            return

        keys = [
            "accessionNumber",
            "filingDate",
            "reportDate",
            "acceptanceDateTime",
            "act",
            "form",
            "fileNumber",
            "filmNumber",
            "items",
            "size",
            "isXBRL",
            "isInlineXBRL",
            "primaryDocument",
            "primaryDocDescription",
        ]
        accession_numbers = recent.get("accessionNumber", [])
        n = len(accession_numbers) if isinstance(accession_numbers, list) else 0
        if n == 0:
            return
        company_name = payload.get("name") or payload.get("companyName") or ""

        for i in range(n):
            record = {
                "cik": cik,
                "companyName": company_name,
                "source": source,
            }
            for key in keys:
                values = recent.get(key, [])
                record[key] = values[i] if i < len(values) else pd.NA
            records.append(record)

    append_from_payload(root, "recent")

    for item in extract_older_files(root):
        name = item.get("name")
        if not name:
            continue
        older_url = f"https://data.sec.gov/submissions/{name}"
        older_payload = fetch_json(older_url, headers=headers, sleep_seconds=sleep_seconds)
        append_from_payload(older_payload, name)

    return records


def filter_10k_records(records: list[dict[str, Any]], ticker: str, start_year: int, end_year: int) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df["ticker"] = ticker.upper()
    df["form"] = df["form"].astype(str).str.upper()
    df["filingDate"] = pd.to_datetime(df["filingDate"], errors="coerce")
    df["reportDate"] = pd.to_datetime(df["reportDate"], errors="coerce")
    df["filedAt"] = df["filingDate"]
    df["year"] = df["filedAt"].dt.year

    forms = {"10-K", "10-K405"}
    df = df.loc[df["form"].isin(forms)].copy()
    df = df.loc[df["year"].between(start_year, end_year, inclusive="both")].copy()
    df = df.sort_values(["ticker", "year", "filedAt", "accessionNumber"], kind="stable")
    df = df.drop_duplicates(subset=["ticker", "accessionNumber"], keep="first")

    df = df.rename(
        columns={
            "accessionNumber": "accessionNo",
            "reportDate": "periodOfReport",
            "primaryDocument": "primaryDocument",
            "primaryDocDescription": "primaryDocDescription",
        }
    )
    df["cik"] = df["cik"].map(normalize_cik)
    df["cik_padded"] = df["cik"].map(cik_to_padded_str)
    df["accession_nodash"] = df["accessionNo"].map(accession_nodash)
    return df.reset_index(drop=True)


def safe_filename(ticker: str, accession_no: str, year: int | float | None) -> str:
    year_part = "unknown" if pd.isna(year) else str(int(year))
    accession_part = str(accession_no).replace("/", "-").replace(":", "-")
    return f"{ticker.upper()}_{year_part}_{accession_part}.txt"


def filing_text_urls(cik_padded: str, accession_nodash_value: str, primary_document: str | None) -> list[str]:
    urls = [SEC_ARCHIVES_URL.format(cik=int(cik_padded), accn_nodash=accession_nodash_value, filename=f"{accession_nodash_value}.txt")]
    if primary_document and str(primary_document) not in {"<NA>", "nan", "None"}:
        urls.append(
            SEC_ARCHIVES_URL.format(
                cik=int(cik_padded),
                accn_nodash=accession_nodash_value,
                filename=str(primary_document),
            )
        )
    return urls


def download_filing_text(urls: list[str], headers: dict[str, str], path: Path, sleep_seconds: float) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    last_error: Exception | None = None

    for url in urls:
        try:
            body = fetch_bytes(url, headers=headers, sleep_seconds=sleep_seconds)
            path.write_bytes(body)
            return url
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue

    raise RuntimeError(f"Failed to download filing text from any candidate URL. Last error: {last_error}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    user_agent = get_user_agent(args.user_agent)
    headers = make_headers(user_agent)

    ticker_map = company_ticker_map(headers, args.sleep_seconds)
    frames: list[pd.DataFrame] = []

    for ticker in args.tickers:
        ticker_norm = ticker.upper()
        if ticker_norm not in ticker_map:
            raise SystemExit(f"Ticker not found in SEC company_tickers.json: {ticker_norm}")

        cik = normalize_cik(ticker_map[ticker_norm]["cik_str"])
        submissions = fetch_submissions(cik, headers, args.sleep_seconds)
        filings = filter_10k_records(submissions, ticker_norm, args.start_year, args.end_year)
        if filings.empty:
            continue
        filings["ticker_name"] = ticker_map[ticker_norm].get("title", pd.NA)
        frames.append(filings)

    if frames:
        manifest = pd.concat(frames, ignore_index=True)
    else:
        manifest = pd.DataFrame(
            columns=[
                "ticker",
                "cik",
                "ticker_name",
                "companyName",
                "accessionNo",
                "filedAt",
                "periodOfReport",
                "year",
                "form",
                "primaryDocument",
                "primaryDocDescription",
                "cik_padded",
                "accession_nodash",
            ]
        )

    manifest = manifest.sort_values(["ticker", "year", "filedAt"], kind="stable").reset_index(drop=True)
    if args.limit_per_ticker and args.limit_per_ticker > 0:
        manifest = manifest.groupby("ticker", group_keys=False).head(args.limit_per_ticker).reset_index(drop=True)

    file_paths: list[str | pd._libs.missing.NAType] = []
    local_text_paths: list[str | pd._libs.missing.NAType] = []
    archive_text_urls: list[str | pd._libs.missing.NAType] = []
    archive_document_urls: list[str | pd._libs.missing.NAType] = []

    for _, row in manifest.iterrows():
        cik_padded = str(row["cik_padded"])
        accession_nodash_value = str(row["accession_nodash"])
        primary_document = row.get("primaryDocument")
        candidate_urls = filing_text_urls(cik_padded, accession_nodash_value, primary_document if pd.notna(primary_document) else None)

        text_path = None
        chosen_url = pd.NA
        if args.download_text:
            text_path = args.text_dir / safe_filename(row["ticker"], row["accessionNo"], row["year"])
            chosen_url = download_filing_text(candidate_urls, headers, text_path, args.sleep_seconds)

        file_paths.append(str(text_path) if text_path is not None else pd.NA)
        local_text_paths.append(str(text_path) if text_path is not None else pd.NA)
        archive_text_urls.append(candidate_urls[0] if candidate_urls else pd.NA)
        archive_document_urls.append(candidate_urls[1] if len(candidate_urls) > 1 else pd.NA)
        if args.download_text and pd.isna(chosen_url):
            raise RuntimeError("download_text requested but no filing URL was resolved")

    manifest["archiveTextUrl"] = archive_text_urls
    manifest["archiveDocumentUrl"] = archive_document_urls
    manifest["file_path"] = file_paths
    manifest["local_text_path"] = local_text_paths

    args.output.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(args.output, index=False)

    print(f"saved {len(manifest):,} 10-K filings to {args.output}")
    if args.download_text:
        print(f"downloaded filing text to {args.text_dir}")
    print(manifest.head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
