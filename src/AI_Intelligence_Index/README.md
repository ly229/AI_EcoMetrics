# AI Intelligence Index Methodology

Source: [Artificial Analysis Intelligence Benchmarking Methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking), Artificial Analysis Intelligence Index v4.0.4, March 2026.

## Purpose

The Artificial Analysis Intelligence Index is a composite benchmark for comparing language model capability across reasoning, knowledge, mathematics, programming, agentic workflows, long-context reasoning, instruction following, and real-world knowledge work.

For this project, the index can be interpreted as an **AI automation score**: a model-level proxy for how much automation capacity is available at a given point in time. Higher scores indicate stronger general capability across tasks that are relevant to knowledge work and AI-assisted finance workflows.

## Index Construction

The Intelligence Index is calculated as a weighted average across four equally weighted categories:

| Category | Weight | Included evaluations |
| --- | ---: | --- |
| Agents | 25% | GDPval-AA, tau2-Bench Telecom |
| Coding | 25% | Terminal-Bench Hard, SciCode |
| General | 25% | AA-LCR, AA-Omniscience, IFBench |
| Scientific Reasoning | 25% | Humanity's Last Exam, GPQA Diamond, CritPt |

Artificial Analysis reports that the v4.0 index combines 10 evaluations and estimates a 95% confidence interval of less than +/- 1% for the aggregate index, based on repeated experiments on selected models.

## Evaluation Principles

Artificial Analysis describes four core principles:

- Standardized evaluation conditions across models.
- Unbiased extraction and validation methods that avoid penalizing valid answer variations.
- Zero-shot instruction prompting without few-shot examples.
- Transparent disclosure of prompts, scoring criteria, and limitations.

## General Testing Parameters

The methodology uses mostly pass@1 scoring, meaning a model must answer correctly on its first attempt. Evaluations with repeated runs aggregate correctness across repeats. General settings include temperature 0 for non-reasoning models, higher temperature for reasoning models unless model labs recommend otherwise, generous output-token limits, and retries for transient API failures.

## Interpretation for AI EcoMetrics

The index is useful as a time-varying automation-capability proxy because it includes categories that map naturally to financial-market automation:

- Agentic workflows: ability to complete multi-step tasks with tools and simulated work environments.
- Coding: ability to generate, inspect, and repair code used in data pipelines and trading infrastructure.
- General reasoning and knowledge: ability to process long documents, follow instructions, and avoid hallucination.
- Scientific reasoning: ability to solve hard analytical tasks requiring domain transfer and careful inference.

The score should not be treated as a direct measure of adoption, labor displacement, or firm-level productivity. It measures technical model capability under benchmark conditions. In empirical work, it should be combined with adoption, access-cost, deployment, and firm-exposure measures before being interpreted as realized economic impact.
