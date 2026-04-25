# Anthropic Economic Index Report: Learning Curves

Source: [Anthropic Economic Index report: Learning curves](https://www.anthropic.com/research/economic-index-march-2026-report), published March 24, 2026.

Supporting materials:

- PDF: <https://cdn.sanity.io/files/4zrzovbb/website/4053bf3440c0c85b8852052770c5b4cf882689c3.pdf>
- Appendix: <https://cdn.sanity.io/files/4zrzovbb/website/a3cdcd9e67c3c4c51440429dd016cacba514b35b.pdf>
- Data: <https://huggingface.co/datasets/Anthropic/EconomicIndex/tree/main/release_2026_03_24>

## Overview

This March 2026 Anthropic Economic Index report studies Claude usage during February 5-12, 2026. It extends Anthropic's economic primitives framework from the January 2026 report, which analyzed November 2025 usage, and adds a new focus on learning curves in AI adoption.

The report has two central questions:

- How did Claude usage change between November 2025 and February 2026?
- Do experienced users appear to get more value from Claude than newer users?

Anthropic's answer is that Claude.ai usage broadened into more diverse and somewhat lower-wage tasks, while first-party API traffic continued to absorb coding and more automated workflows. The report also finds that longer-tenure users tend to use Claude for more complex, work-related, and collaborative tasks, and that their conversations have higher measured success rates even after controls.

## Key Findings

- Claude.ai use cases became less concentrated. The top 10 O*NET tasks fell from 24% of Claude.ai conversations in November 2025 to 19% in February 2026.
- Coding remained central, but its locus shifted. Computer and Mathematical tasks accounted for 35% of Claude.ai conversations, while coding activity increasingly moved into first-party API traffic, including Claude Code workflows.
- Personal use increased on Claude.ai. Personal conversations rose from 35% to 42%, while coursework fell from 19% to 12%.
- The average value of Claude.ai tasks declined slightly. Anthropic estimates average task value using US wages for associated occupations; Claude.ai moved from $49.3 to $47.9 per hour, largely because of more casual and factual queries and less coding share on Claude.ai.
- Augmentation increased slightly on Claude.ai. Validation and learning patterns rose modestly, while the appendix reports a sharp decline in automation share in first-party API data.
- Exposure breadth barely changed. The cumulative estimate that about 49% of jobs have seen at least one quarter of their tasks performed using Claude remained essentially stable.
- Geographic convergence continued inside the US but slowed. The top five US states' share of per-person usage fell from 30% in August 2025 to 24% in February 2026, but the implied convergence horizon lengthened to roughly 5-9 years.
- Global inequality in Claude usage persisted. The top 20 countries' share of population-adjusted usage increased from 45% to 48%.
- Users select stronger models for higher-value tasks. Opus was used more often for tasks tied to higher-wage occupations, with the Opus share rising by about 1.5 percentage points per additional $10 of task value on Claude.ai and 2.8 percentage points in first-party API traffic.
- Longer-tenure users have higher measured success. Users with at least six months of tenure had higher conversation success rates. The raw difference was about 5 percentage points, and the fully controlled estimate was about 4 percentage points.

## What Changed Since January 2026

### Use-Case Diversification

Claude.ai traffic became less dominated by the most common tasks. Anthropic attributes this to two overlapping changes:

- coding tasks moved from Claude.ai into first-party API workflows, where Claude Code can break work into many smaller API calls;
- broader consumer adoption added more casual personal queries, such as sports, product comparison, and home maintenance questions.

This diversification does not mean that Claude entered many entirely new areas of work. Anthropic reports that almost all tasks in the February 2026 sample had appeared in earlier samples, and that the cumulative 49% job-exposure breadth measure barely changed.

### Automation and Augmentation

Anthropic continues to classify interactions into five patterns:

- directive
- feedback loop
- task iteration
- validation
- learning

These are grouped into automation and augmentation. In Claude.ai, augmentation rose slightly, driven by validation and learning. In the API, the report emphasizes a different pattern: as coding and operational workflows migrate to API traffic, they may become more automation-exposed because API use is more likely to be directive and less likely to keep a human in the loop.

The report highlights two emerging API workflow categories that at least doubled relative to the prior sample:

- business sales and outreach automation, including lead qualification, customer data enrichment, and cold-email drafting;
- automated trading and market operations, including market monitoring, position monitoring, investment proposals, and trader-facing market updates.

### Task Value and Complexity

Anthropic uses task-associated US wages as a proxy for the economic value of work performed on Claude. On Claude.ai, the average task value declined from $49.3 to $47.9 per hour. The report links this to a mix shift toward simpler factual questions and the migration of coding work to API traffic.

Other economic primitives moved in the same general direction for Claude.ai:

- estimated education required for user inputs fell from 12.2 to 11.9 years;
- estimated human-only completion time fell by about two minutes;
- users granted slightly more autonomy to Claude.

Anthropic notes one exception: tasks performed by Claude were judged slightly less possible for a human without AI access.

### Geography

Within the United States, Claude usage continued to converge across states, but at a slower pace than in the January 2026 report. The earlier estimate suggested roughly equal per-capita state usage within 2-5 years; the March report revises that to 5-9 years.

Across countries, the pattern moved in the opposite direction. Population-adjusted usage became more concentrated, with the top 20 countries rising from 45% to 48% of usage.

## Learning to Use AI

The report's second chapter studies whether users appear to improve at matching Claude to tasks and whether tenure is associated with better outcomes.

### Model Selection

Anthropic analyzes demand for model intelligence by looking at when users choose Opus rather than other Claude model classes. The pattern is consistent with users reserving Opus for harder or higher-value work:

- among paid Claude.ai users, 55% of Computer and Mathematical tasks used Opus, compared with 45% of Educational tasks;
- on Claude.ai, Software Developer tasks used Opus more often than Tutor tasks;
- each additional $10 of task value was associated with a 1.5 percentage point increase in Opus share on Claude.ai;
- the API showed a stronger slope, with a 2.8 percentage point increase in Opus share per additional $10 of task value.

For this project, this model-selection evidence is useful because it suggests observed AI use is not only about task incidence. Users also allocate model quality across tasks in ways that may reflect perceived task complexity, cost sensitivity, and expected returns.

### Tenure and Success

Anthropic defines high-tenure users as those who signed up at least six months before the data pull. Compared with lower-tenure users, high-tenure users:

- used Claude more often for work;
- used Claude for tasks requiring higher estimated education levels;
- used Claude less for personal tasks;
- showed slightly less concentration in the top 10 O*NET tasks;
- were more likely to iterate with Claude rather than use purely directive patterns.

The report also finds a positive association between user tenure and conversation success:

- simple bivariate estimate: about 5 percentage points higher success for high-tenure users;
- within-task and request-cluster fixed effects: about 3 percentage points;
- full controls for model, use case, and country: about 4 percentage points.

Anthropic interprets this as evidence consistent with learning-by-doing, while noting important caveats. High-tenure users are self-selected, early adopters may differ systematically from later users, and survivorship bias may matter because the data does not include users who signed up early but stopped using Claude.

## Interpretation for AI EcoMetrics

This report is most useful as evidence on realized AI adoption, not as a direct labor-displacement estimate. It contributes several signals that can be connected to employment, wage, task, and firm-level data:

- realized task penetration by O*NET task and occupation;
- migration from consumer chatbot use to API-mediated workflows;
- changing automation versus augmentation patterns;
- geographic diffusion across states and countries;
- model-selection behavior as a proxy for task complexity and willingness to pay for capability;
- tenure-based learning curves that may affect who captures AI benefits.

The learning-curve result is especially important for inequality analysis. If experienced users become more effective at extracting value from AI, early access and repeated use may compound advantages among high-skill workers, high-income geographies, and firms that adopted AI sooner.

At the same time, the report's own caveats should be preserved in downstream empirical work. The tenure-success association is not a randomized estimate of learning, and observed Claude usage is not representative of the whole labor market. Claude traffic overweights tasks and users who have already adopted Anthropic products.

## Suggested Variables for Downstream Analysis

Potential variables to extract or join from the March 2026 release:

| Concept | Possible use |
| --- | --- |
| O*NET task share | Measure realized task-level Claude adoption. |
| Occupation task value | Proxy for wage-weighted economic value of AI-mediated work. |
| Automation / augmentation category | Distinguish replacement-like and complementarity-like usage. |
| First-party API versus Claude.ai platform | Separate consumer exploratory use from integrated workflow use. |
| Geography-adjusted usage index | Study regional diffusion and convergence. |
| Model class selection | Infer demand for intelligence or task complexity. |
| User tenure group | Study learning curves and adoption maturity. |
| Conversation success measure | Link experience and task characteristics to observed outcomes. |

## Citation

```bibtex
@online{anthropic2026aeiv5,
  author = {Maxim Massenkoff and Eva Lyubich and Peter McCrory and Ruth Appel and Ryan Heller},
  title = {Anthropic Economic Index report: Learning curves},
  date = {2026-03-24},
  year = {2026},
  url = {https://www.anthropic.com/research/economic-index-march-2026-report},
}
```
