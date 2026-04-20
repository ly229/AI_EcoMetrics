---
name: sec-api-10k-filings
description: Connect to official SEC EDGAR data.sec.gov endpoints or the third-party sec-api service to query 10-K filings, download raw filing text, and build a firm-year manifest for text-based AI exposure analysis. Use when you need to fetch SEC filings by ticker, year, or form type, save local filing text, or prepare a 10-K corpus for downstream automation or AI-exposure research.
---

# SEC API 10-K Filings

## Overview

Use this skill to build a reproducible SEC filing pipeline for finance research:

- connect to official SEC EDGAR endpoints with a valid User-Agent header, or use the third-party sec-api service when that is the chosen source
- search EDGAR for 10-K filings by ticker and date range
- capture filing metadata and `linkToTxt`
- optionally download raw filing text to local disk
- create a manifest that downstream AI-exposure code can consume

## Workflow

1. Set credentials.
   - `SEC_USER_AGENT` should identify the researcher or workspace.
   - `SEC_API_KEY` is only needed if you are intentionally using the third-party `sec-api` service.
   - Load secrets from `.env` when available.
2. Query filings from the chosen source.
   - For official SEC EDGAR access, use the `data.sec.gov` / EDGAR endpoints with a descriptive User-Agent header.
   - For the third-party `sec-api` service, use `sec_api.QueryApi` with a Lucene query such as `ticker:SPGI AND formType:"10-K" AND filedAt:[2015-01-01 TO 2025-12-31]`.
   - Page through results in batches of 50.
   - Keep the fields needed for research: `ticker`, `companyName`, `accessionNo`, `filedAt`, `periodOfReport`, `linkToTxt`, and `linkToFilingDetails`.
3. Download filing text only after metadata is validated.
   - Save the raw 10-K text to a stable local path.
   - Keep the raw file separate from the cleaned manifest.
4. Build a firm-year manifest.
   - Include `file_path`, `year`, and any join key available in the panel (`firm`, `tic`, or `firm_group`).
   - Deduplicate by firm-year-accession if needed.
5. Hand the manifest to the exposure builder.
   - The downstream exposure step should count AI-related language in the filing text and normalize by total words.
   - Keep the raw text corpus so the exposure measure can be rebuilt later with a revised lexicon.

## Practical Rules

- Prefer raw EDGAR text from `linkToTxt` over screenshots, HTML snippets, or secondary summaries.
- For official SEC access, a valid User-Agent header is the authentication control. Do not invent API-key requirements for `data.sec.gov`.
- Keep the extraction reproducible: record the query, date range, ticker set, and pull date.
- If the API returns multiple 10-Ks in a year, retain the filing that matches the analysis rule and document the choice.
- Treat the downloaded text corpus as the source of truth for exposure construction.
- Validate that each manifest row has a usable local text path before running exposure scoring.

## Common Failure Modes

- Missing `SEC_API_KEY` or invalid `sec-api` installation.
- Missing or generic `SEC_USER_AGENT` for official SEC access.
- Query too broad or missing quotes around `formType:"10-K"`.
- Filing text download blocked by missing or generic user-agent headers.
- Manifest built without a year or join key, which prevents the panel merge.

## Reference Material

See [Filing Workflow Reference](references/filing_workflow.md) for the query template, manifest schema, and text-download conventions.
