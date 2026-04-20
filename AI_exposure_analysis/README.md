# AI Exposure Analysis

This folder contains the official SEC EDGAR 10-K exposure pipeline and the panel fixed-effects analysis built from the resulting AI exposure variable.

## Setup

Set `SEC_USER_AGENT` in `.env` or your shell before running the SEC fetch script. The official SEC endpoints do not require an API key.

## Main idea

Estimate how firm outcomes move with AI exposure after absorbing:

- firm fixed effects
- year fixed effects

The baseline specification is:

```text
log1p(outcome_it) = beta * ai_exposure_it + firm FE + year FE + error_it
```

## Intended outcomes

- `revenue_per_employee`
- `aum_per_employee`
- `labor_expense_per_employee`

## Exposure input

The preferred input is an external exposure file with at least:

- a firm identifier such as `firm`, `tic`, or `firm_group`
- a year column such as `year`, `fyear`, or `date`
- an exposure column named `ai_exposure`

Build the series with [`build_ai_exposure_from_filings.py`](./scripts/build_ai_exposure_from_filings.py). The builder expects a manifest of filing text files and computes a scaled mention-rate using AI-related language in annual reports or 10-Ks fetched from official SEC EDGAR endpoints.

The FE script still supports a fallback proxy for development, but the main analysis should use the filing-based exposure series.

## Why this is the right next step

The current `simple_analysis` work documents trends, but the FE design lets you test whether variation in AI exposure is associated with within-firm changes in productivity or labor intensity over time.

## Script

1. Build the exposure series with [`build_ai_exposure_from_filings.py`](./scripts/build_ai_exposure_from_filings.py).
2. Run [`run_ai_exposure_panel_fe.py`](./scripts/run_ai_exposure_panel_fe.py).
3. Or run the full pipeline with [`run_sec_ai_exposure_pipeline.py`](./scripts/run_sec_ai_exposure_pipeline.py).
