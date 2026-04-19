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
./build_tex.sh
```

If you use `uv`, the project root also includes a minimal `pyproject.toml` so `uv run` works as a lightweight environment entry point.

Environment knobs:

- `TECTONIC_ONLY_CACHED=0` to allow network fetching when you explicitly want it
- `TECTONIC_BUNDLE=/path/to/bundle` to point at a specific Tectonic resource bundle
- `TECTONIC_BIN=/path/to/tectonic` to override the binary selection
