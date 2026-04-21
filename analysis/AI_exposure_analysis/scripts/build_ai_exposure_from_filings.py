#!/usr/bin/env python3
"""Build a filing-text based AI exposure series for the finance panel.

The preferred research design is a text-based exposure measure built from
annual report or 10-K language. This script reads a manifest of filing text
files, counts AI-related language, and outputs a firm-year exposure panel.

Expected manifest columns:

- `file_path` or `path`: path to the filing text file
- `year`: filing year
- optional `firm`, `tic`, `firm_group`

The output is normalized by total words and scaled per 10,000 words.
"""

from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEFAULT_MANIFEST = Path("AI_exposure_analysis/data/sec_10k_manifest.csv")
DEFAULT_PANEL = Path("simple_analysis/data/compustat_panel_by_firm_group.csv")
DEFAULT_OUTPUT = Path("AI_exposure_analysis/data/ai_exposure_by_firm_year.csv")

TERM_GROUPS = {
    "direct_ai": [
        r"\bartificial intelligence\b",
        r"\bmachine learning\b",
        r"\bdeep learning\b",
        r"\bgenerative ai\b",
        r"\blarge language model(?:s)?\b",
        r"\bfoundation model(?:s)?\b",
        r"\bagentic ai\b",
        r"\bautonomous agent(?:s)?\b",
        r"\bai\b",
    ],
    "adjacent_automation": [
        r"\bautomation\b",
        r"\bautomated\b",
        r"\bautomating\b",
        r"\brobotic process automation\b",
        r"\bstraight-through processing\b",
        r"\bworkflow automation\b",
        r"\balgorithmic\b",
        r"\bpredictive analytics\b",
    ],
}

HTML_TAG_RE = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"\b[\w'-]+\b")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a filing-text based AI exposure series.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="CSV manifest of filing text files.")
    parser.add_argument(
        "--panel",
        type=Path,
        default=DEFAULT_PANEL,
        help="Optional Compustat panel used to attach firm labels from ticker/year.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV path.")
    parser.add_argument(
        "--scale",
        type=float,
        default=10000.0,
        help="Scaling factor for the exposure rate (default: 10000 words).",
    )
    return parser


def clean_text(text: str) -> str:
    text = HTML_TAG_RE.sub(" ", text)
    text = text.replace("\u00a0", " ")
    return text


def count_matches(text: str, patterns: list[str]) -> int:
    total = 0
    for pattern in patterns:
        total += len(re.findall(pattern, text, flags=re.IGNORECASE))
    return total


def read_text_file(path: Path) -> str:
    text = path.read_text(errors="ignore")
    return clean_text(text)


def load_manifest(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    file_col = None
    for candidate in ["file_path", "path", "filing_path", "text_path", "local_text_path"]:
        if candidate in df.columns:
            file_col = candidate
            break
    if file_col is None:
        raise ValueError("Manifest must contain a file path column such as `file_path` or `path`.")
    if "year" not in df.columns:
        raise ValueError("Manifest must contain a `year` column.")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["file_path"] = df[file_col].astype(str)
    if "ticker" in df.columns and "tic" not in df.columns:
        df["tic"] = df["ticker"]
    if "ticker" in df.columns and "firm" not in df.columns:
        df["firm"] = df["ticker"]
    return df


def load_panel_map(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    panel = pd.read_csv(path)
    panel.columns = [c.strip().lower() for c in panel.columns]
    keep = [c for c in ["ticker", "tic", "firm", "firm_group", "year"] if c in panel.columns]
    if not keep:
        return pd.DataFrame()
    return panel.loc[:, keep].drop_duplicates()


@dataclass
class FilingStats:
    direct_ai_count: int
    adjacent_automation_count: int
    total_word_count: int

    @property
    def weighted_count(self) -> int:
        return 2 * self.direct_ai_count + self.adjacent_automation_count


def compute_stats(text: str) -> FilingStats:
    text = text.lower()
    words = WORD_RE.findall(text)
    total_word_count = len(words)
    direct_ai_count = count_matches(text, TERM_GROUPS["direct_ai"])
    adjacent_automation_count = count_matches(text, TERM_GROUPS["adjacent_automation"])
    return FilingStats(
        direct_ai_count=direct_ai_count,
        adjacent_automation_count=adjacent_automation_count,
        total_word_count=total_word_count,
    )


def build_exposure(manifest: pd.DataFrame, panel_map: pd.DataFrame, scale: float) -> pd.DataFrame:
    rows = []
    for _, row in manifest.iterrows():
        file_path = Path(str(row["file_path"]))
        if not file_path.exists():
            raise FileNotFoundError(f"Filing text file not found: {file_path}")

        text = read_text_file(file_path)
        stats = compute_stats(text)
        total_words = max(stats.total_word_count, 1)
        exposure_rate = (stats.weighted_count / total_words) * scale

        rows.append(
            {
                "year": int(row["year"]) if pd.notna(row["year"]) else pd.NA,
                "ticker": row["ticker"] if "ticker" in row.index else pd.NA,
                "firm": row["firm"] if "firm" in row.index else pd.NA,
                "tic": row["tic"] if "tic" in row.index else pd.NA,
                "firm_group": row["firm_group"] if "firm_group" in row.index else pd.NA,
                "accessionNo": row["accessionno"] if "accessionno" in row.index else pd.NA,
                "file_path": str(file_path),
                "document_word_count": stats.total_word_count,
                "direct_ai_count": stats.direct_ai_count,
                "adjacent_automation_count": stats.adjacent_automation_count,
                "weighted_ai_count": stats.weighted_count,
                "ai_exposure": exposure_rate,
            }
        )

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["year"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    group_keys = [c for c in ["ticker", "firm", "tic", "firm_group", "year"] if c in df.columns]
    df = (
        df.groupby(group_keys, dropna=False, as_index=False)
        .agg(
            n_documents=("file_path", "size"),
            document_word_count=("document_word_count", "sum"),
            direct_ai_count=("direct_ai_count", "sum"),
            adjacent_automation_count=("adjacent_automation_count", "sum"),
            weighted_ai_count=("weighted_ai_count", "sum"),
        )
    )

    # Recompute the rate after aggregation using the aggregated counts.
    denom = df["document_word_count"].replace(0, pd.NA)
    df["ai_exposure"] = (df["weighted_ai_count"] / denom) * scale

    join_candidates = [c for c in ["ticker", "tic", "firm", "firm_group"] if c in df.columns and c in panel_map.columns]
    if not panel_map.empty and join_candidates:
        join_key = join_candidates[0]
        merged = df.merge(panel_map, on=[join_key, "year"], how="left", suffixes=("", "_panel"))
        for col in ["ticker", "tic", "firm", "firm_group"]:
            panel_col = f"{col}_panel"
            if panel_col in merged.columns:
                merged[col] = merged[col].fillna(merged[panel_col])
                merged = merged.drop(columns=[panel_col])
        df = merged

    df = df.sort_values([c for c in ["firm", "tic", "firm_group", "year"] if c in df.columns]).reset_index(drop=True)
    return df


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    panel_map = load_panel_map(args.panel)
    exposure = build_exposure(manifest, panel_map, args.scale)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    exposure.to_csv(args.output, index=False, quoting=csv.QUOTE_MINIMAL)

    print(f"saved AI exposure series to {args.output}")
    print(exposure.head(10).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
