# Anthropic Economic Index

Source: [Anthropic Economic Index](https://www.anthropic.com/economic-index), last updated March 24, 2026. Dataset: [Anthropic/EconomicIndex](https://huggingface.co/datasets/Anthropic/EconomicIndex/tree/main) on Hugging Face.

## Purpose

The Anthropic Economic Index tracks how Claude is being used across the economy. Anthropic describes it as an effort to measure AI adoption and economic effects from real-world usage data, using privacy-preserving aggregation rather than publishing individual conversations.

For this project, the index is useful as an **AI adoption and labor-exposure signal**. It complements model capability benchmarks by measuring where AI tools are actually being used, which tasks appear in Claude traffic, and whether use patterns look more like augmentation or automation.

## Dataset Location

The public dataset can be downloaded from Hugging Face:

- Main dataset repository: <https://huggingface.co/datasets/Anthropic/EconomicIndex/tree/main>
- Labor-market-impact files: <https://huggingface.co/datasets/Anthropic/EconomicIndex/tree/main/labor_market_impacts>
- Latest Economic Index release as of the source page update: <https://huggingface.co/datasets/Anthropic/EconomicIndex/tree/main/release_2026_03_24>

The Hugging Face repository contains multiple releases, including the initial February 2025 release and later updates for March 2025, September 2025, January 2026, and March 2026. The March 24, 2026 release adds updated Claude.ai and first-party API analysis, including learning-curve and model-selection measures.

## Local Files

This directory currently stores the labor-market-impact subset:

| File | Description |
| --- | --- |
| `job_exposure.csv` | Occupation-level observed exposure scores keyed by O*NET-SOC occupation code and title. |
| `task_penetration.csv` | Task-level penetration scores showing whether specific O*NET tasks have observed Claude usage. |

Anthropic's labor-market-impact report defines observed exposure as a measure that combines theoretical LLM capability, actual Claude usage, work-related usage, automation-vs-augmentation patterns, and each task's importance within an occupation.

## Key Findings From Anthropic

- Claude usage is uneven across occupations and countries, with high-value knowledge-work tasks appearing more frequently than a representative sample of all labor-market activity.
- The March 2026 report finds that Claude.ai use cases diversified relative to November 2025, while coding activity continued shifting toward first-party API workflows.
- Anthropic reports that about 49% of jobs have seen at least one quarter of their tasks performed using Claude, but actual task coverage remains far below theoretical LLM capability.
- In the labor-market-impact analysis, computer programmers, customer service representatives, and data entry keyers are among the most exposed occupations under the observed-exposure measure.
- Anthropic finds no systematic increase in unemployment for highly exposed workers through the analyzed period, while noting suggestive evidence that hiring into exposed occupations slowed for workers aged 22 to 25.

## Interpretation for AI EcoMetrics

Use these files as realized-exposure measures, not as direct estimates of job loss. The data is best interpreted as evidence of where AI is already being applied to occupational tasks. It should be combined with time-varying model capability, employment outcomes, wages, industry composition, and firm-level adoption before drawing conclusions about displacement or productivity effects.

The local CSVs are especially useful for empirical designs that need:

- occupation-level AI exposure based on observed usage;
- task-level AI penetration measures;
- mappings from O*NET tasks to broader labor-market outcomes;
- a distinction between theoretical capability and realized AI deployment.
