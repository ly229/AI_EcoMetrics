# Interpretation of the Simple Productivity Regression

This note explains where the regression numbers come from and how to read them.

## Source Data

The regression uses the panel in [data/compustat_panel_by_firm_group.csv](/Users/xiang/github/AI_EcoMetrics/data/compustat_panel_by_firm_group.csv).

The script [scripts/run_simple_finance_productivity_analysis.py](/Users/xiang/github/AI_EcoMetrics/scripts/run_simple_finance_productivity_analysis.py) does three things:

1. Loads the firm-year panel.
2. Computes:
   - `revenue_per_employee = revt / emp`
   - `aum_per_employee = aum_crsp / emp`
3. Runs regressions with era dummies and firm-group fixed effects.

## Era Definitions

The eras are defined directly in the script:

- Pre-computerization: `1950-1979`
- Computerization: `1980-1989`
- Indexing: `1990-2014`
- AI: `2015-2025`

These are not estimated from the data. They are user-defined time bins.

## What the Regression Coefficients Are

The model is:

```text
log1p(revenue_per_employee) = era dummies + firm-group fixed effects
```

and similarly for `aum_per_employee`.

The coefficients on the era variables are **log differences** relative to the omitted base era, which is **Pre-computerization**.

### Revenue per employee

From [outputs/simple_analysis/revenue_per_employee_fe.txt](/Users/xiang/github/AI_EcoMetrics/outputs/simple_analysis/revenue_per_employee_fe.txt):

- Computerization: `1.4070`
- Indexing: `2.0543`
- AI: `2.3688`

These are not dollar amounts. They are estimated differences in `log1p(revenue per employee)`.

A rough multiplicative interpretation is:

- `exp(1.4070) - 1 ≈ 3.1`
- `exp(2.0543) - 1 ≈ 6.8`
- `exp(2.3688) - 1 ≈ 9.7`

So revenue per employee is much higher in later eras than in the pre-computerization era.

### AUM per employee

From [outputs/simple_analysis/aum_per_employee_fe.txt](/Users/xiang/github/AI_EcoMetrics/outputs/simple_analysis/aum_per_employee_fe.txt):

- Computerization: `1.3638`
- Indexing: `2.4197`
- AI: `3.3944`

These also represent log differences relative to the pre-computerization era.

## What the Summary Table Numbers Are

The file [outputs/simple_analysis/era_summary.csv](/Users/xiang/github/AI_EcoMetrics/outputs/simple_analysis/era_summary.csv) reports raw averages by era, not regression coefficients.

For example:

- `mean_revenue_per_employee` is the average of `revt / emp` within each era.
- `mean_aum_per_employee` is the average of `aum_crsp / emp` within each era.

These are descriptive statistics from the panel.

## What N Means

In the regression output, `N = 320` means the model used 320 firm-year observations after dropping rows with missing values for the relevant outcome and era assignment.

## What R-squared Means

`R-squared = 0.884` means the regression explains about 88.4% of the variation in `log1p(revenue per employee)` in this small panel.

This high fit is mainly because the model includes:

- era dummies, which capture broad time shifts
- firm-group fixed effects, which capture persistent differences across firms

## What the Firm-Group Coefficients Mean

The firm-group coefficients are differences relative to the omitted reference firm group, holding the era constant.

For example:

- `JPMorgan family = 0.2377`
- `S&P Global = -0.4608`

These indicate that some firms are systematically above or below the reference group in productivity.

## Suggested Paper Wording

> The coefficients are estimated from a firm-panel regression using `log1p(revenue per employee)` and `log1p(AUM per employee)` as outcomes, with era indicators defined from the raw Compustat panel and firm-group fixed effects included to absorb persistent differences across firms.

