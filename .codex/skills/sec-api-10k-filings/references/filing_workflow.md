# Filing Workflow Reference

## 1. Auth

Required environment variables:

- `SEC_USER_AGENT`
- `SEC_API_KEY` only if you intentionally use the third-party `sec-api` service

Typical local setup:

```bash
export SEC_USER_AGENT="Your Name your.email@domain.com"
```

If secrets are stored in `.env`, load them before calling the API.
For official SEC EDGAR access, the User-Agent header is the key requirement.

## 2. Query Pattern

Use official SEC EDGAR endpoints with a valid User-Agent header, or use SEC API `QueryApi` if you are intentionally using the third-party service. For the latter, search 10-K filings with a Lucene query:

```text
ticker:SPGI AND formType:"10-K" AND filedAt:[2015-01-01 TO 2025-12-31]
```

Notes:

- quote `10-K` exactly
- page results with `from` and `size`
- use `sort` on `filedAt`
- keep only the fields needed for the manifest

## 3. Recommended Metadata Fields

Retain these fields when available:

- `ticker`
- `companyName`
- `accessionNo`
- `filedAt`
- `periodOfReport`
- `linkToTxt`
- `linkToFilingDetails`

Add these derived fields:

- `year`
- `filed_year`
- `file_path`
- `local_text_path`

## 4. Manifest Schema

Minimum schema for the filing manifest:

| column | purpose |
| --- | --- |
| `file_path` | local path to the raw 10-K text |
| `year` | filing or report year |
| `ticker` or `firm` or `firm_group` | join key for the panel |
| `accessionNo` | unique filing identifier |
| `linkToTxt` | SEC source URL |

Suggested export rule:

- one row per filing
- deduplicate by `ticker`, `year`, and `accessionNo`
- sort by `ticker`, `year`, `filedAt`

## 5. Download Rule

Download raw filing text only after metadata collection is complete.

Use a descriptive `User-Agent` header and save the original SEC text unchanged. Do not rewrite the raw file when cleaning; create a separate cleaned output if needed.

## 6. Exposure Handoff

After the manifest is saved:

1. verify each row has a local `file_path`
2. run the text-based exposure builder
3. merge the resulting exposure series into the panel by firm and year

If the exposure measure changes later, rebuild from the raw corpus rather than patching the existing scores in place.
