# AI_EcoMetrics

This project studies how AI trading agents may transform financial markets, market structure, and finance labor demand. The working paper is [src/AI_ecometrics.tex](src/AI_ecometrics.tex), titled:

`From Clerks to Agentic-AI: How will Technology Transform Us?`

## Core Idea

The paper argues that finance has repeatedly been reshaped by productivity shocks. The historical benchmark is the computer revolution of the 1980s and 1990s, when semiconductors, PCs, spreadsheets, Bloomberg terminals, and Reuters systems increased the speed and scale of market analysis.

The current wave is AI:

1. AI trading agents lower the cost of research, monitoring, execution, and risk management.
2. Small teams can approach capabilities that previously required larger institutional staffs.
3. The industry may become more polarized, with strong pressure on middle-layer analytical and operational roles.

## Main Themes

- Historical parallel: manual finance -> computerization -> AI-augmented finance
- Retail divergence: AI-enabled investors vs non-AI users
- Institutional response: adaptation through infrastructure, data, and compliance
- Democratization: lower-cost access to sophisticated market tools
- Labor impact: routine tasks are the most exposed
- Structural shift: the market may support "mini hedge funds" and AI-supervised workflows

## Evidence Base

The draft uses two compact evidence tables to support the historical analogy:

- [data/Vanguard_Evidence_Table.md](data/Vanguard_Evidence_Table.md)
- [data/Pre_Electronic_Firm_Evidence_Tables.md](data/Pre_Electronic_Firm_Evidence_Tables.md)

These tables document:

- Vanguard as a lean transition case in asset management
- Merrill Lynch, Morgan Stanley, and Smith Barney as pre-electronic firm benchmarks

## Data Collection Skills

The project uses reusable skills for data collection:

- `wrds-data-collection` - collect financial research data from WRDS using Python and SQL pushdown queries
- `sec-api-10k-filings` - connect to official SEC EDGAR endpoints, fetch 10-K filings, download filing text, and build a manifest for the AI exposure proxy / automation level index

These skills support the panel and text-based exposure workflows used to measure productivity, labor intensity, and how much AI- and automation-related language appears in annual reports and 10-K filings.

## AI Automation Score

[src/AI_Intelligence_Index](src/AI_Intelligence_Index/) documents the Artificial Analysis Intelligence Index methodology and treats it as an AI automation score: a model-level proxy for the frontier automation capability available to finance workflows over time.

## AI Exposure Analysis

The SEC filing pipeline and the resulting panel fixed-effects analysis now live in [AI_exposure_analysis](AI_exposure_analysis/).

Key scripts:

- [run_sec_ai_exposure_pipeline.py](AI_exposure_analysis/scripts/run_sec_ai_exposure_pipeline.py)
- [fetch_sec_10k_filings.py](AI_exposure_analysis/scripts/fetch_sec_10k_filings.py)
- [build_ai_exposure_from_filings.py](AI_exposure_analysis/scripts/build_ai_exposure_from_filings.py)
- [run_ai_exposure_panel_fe.py](AI_exposure_analysis/scripts/run_ai_exposure_panel_fe.py)

## Document Structure

The LaTeX draft is organized into:

1. Abstract and introduction
2. Historical parallel to the computer revolution
3. Historical evidence base
4. AI trading agents and market stratification
5. Democratization of financial capability
6. Mini hedge funds and institutional impact
7. Workforce transformation
8. Efficiency versus fairness
9. Historical risk reminders and conclusion

## Build

The PDF is generated from `src/AI_ecometrics.tex`.

Example local build:

```bash
./tectonic --outdir build src/AI_ecometrics.tex
```

If you use `uv`, the project root also includes a minimal `pyproject.toml` so `uv run` works as a lightweight environment entry point.
