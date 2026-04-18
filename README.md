# AI_EcoMetrics

This project tells a simple story: as asset management moved through computerization, index investing, and AI-driven automation, the industry became more scalable and required fewer employees per dollar of assets managed.

The central question is whether technology changed the labor intensity of asset management. The main outcome is `AUM per Employee`, which measures how much capital each worker supports. If this ratio rises over time, it suggests that firms are managing more assets with relatively less labor, or with labor shifted toward higher-value tasks such as oversight, research, compliance, and model governance.

The narrative follows three technology waves:

1. Computerization reduced routine clerical and back-office work.
2. Index investing expanded scalable, rules-based portfolio management.
3. AI and automation may further reduce routine analytical work while increasing the value of specialized judgment and supervision.

## Methodology

The empirical design is intentionally simple and descriptive. It uses a firm-year panel for major asset managers and combines labor counts with assets under management, revenue, and operating expense data. The key metric is computed as:

`AUM per Employee = Assets Under Management / Employees`

Supporting measures include:

`Revenue per Employee`

`Operating Expense / AUM`

Optional extensions add passive AUM share and a simple AI-exposure proxy from filings or era dummies. The goal is not causal identification but a clear set of stylized facts that show how labor productivity changed across the three technology eras.

I also created a WRDS data-collection skill to make the extraction workflow reusable and reproducible. The skill is saved in `.codex/skills/wrds-data-collection`.
