---
name: wrds-data-collection
description: Collect financial research data from WRDS using Python connections and SQL pushdown queries. Use when building reproducible extraction workflows, filtering WRDS datasets, pulling firm-level or security-level panels, validating row counts, or writing a data collection procedure for finance or economics research.
---

# WRDS Data Collection

Use this skill when the task is to pull research data from WRDS with Python, apply SQL filters at the source, and save a reproducible panel for analysis.

## Procedure

1. Load credentials from `.env` or shell environment variables.
2. Connect to WRDS in Python with explicit `wrds_username` and `wrds_password`.
2. Identify the exact library, table, key fields, and date range before writing code.
3. Push all row filters, joins, and column selection into SQL.
4. Fetch only the reduced result set into pandas.
5. Standardize identifiers, dates, and numeric fields after loading.
6. Save raw extracts separately from cleaned analysis files.
7. Log the query, pull date, row counts, and any exclusions.

## Connection Setup

Use environment variables when connecting locally:

```bash
export WRDS_USERNAME="YOUR_USERNAME"
export WRDS_PASSWORD="YOUR_PASSWORD"
```

Then test the connection:

```bash
python -c "import wrds; c = wrds.Connection(); print('connected')"
```

For scripted extraction, prefer passing the credentials directly so WRDS does not prompt interactively:

```python
import os
import wrds

conn = wrds.Connection(
    wrds_username=os.environ["WRDS_USERNAME"],
    wrds_password=os.environ["WRDS_PASSWORD"],
)
```

When running in a non-interactive session, suppress the optional `.pgpass` prompt by answering `n` or wrapping the connection call in a small helper that returns `n` from `input()`.

## Working Rules

- Prefer SQL pushdown over pulling full tables into Python.
- Select only the fields needed for the analysis.
- Pull in chunks when the table is large or the date range is long.
- Validate the extract by comparing SQL counts with the loaded dataframe.
- Keep raw and processed data in separate folders.
- Write reusable code so the same query can be rerun later.

## Reusable Resources

- Use [`references/wrds_query_templates.md`](references/wrds_query_templates.md) for source-specific SQL patterns for Compustat, CRSP, and Thomson Reuters / I/B/E/S.
- Use [`scripts/wrds_extract.py`](scripts/wrds_extract.py) when you want a reproducible command-line extraction workflow with optional export to CSV or Parquet.

## Standard Extraction Pattern

```python
from pathlib import Path
import os
import wrds
import pandas as pd

def load_env_file(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file()

conn = wrds.Connection(
    wrds_username=os.environ["WRDS_USERNAME"],
    wrds_password=os.environ["WRDS_PASSWORD"],
)

sql = """
select gvkey, datadate, at, sale, emp
from comp.funda
where indfmt = 'INDL'
  and datafmt = 'STD'
  and popsrc = 'D'
  and consol = 'C'
  and fyear between 2000 and 2024
"""

df = conn.raw_sql(sql)
df["datadate"] = pd.to_datetime(df["datadate"])
```

## Output Expectations

When asked to draft the procedure, produce:

- A short description of the dataset and source table
- The Python connection code
- The SQL query with filters
- The dataframe cleaning and export steps
- A brief validation note
