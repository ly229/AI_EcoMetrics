# Wage-Related Analysis Summary

This extension uses `xlr` from the Compustat panel as a labor-expense proxy. The dataset does not contain worker-level wages, so the analysis focuses on firm-level labor costs rather than individual pay.

## Main Observations

- Inflation-adjusted labor expense per employee rises over time for most firm groups, but the increase is more moderate than the raw nominal series.
- `S&P Global` has the lowest average labor expense per employee among the firm groups, while `BNY Mellon / Dreyfus family` and `JPMorgan family` are at the top end of the sample.
- Labor expense as a share of revenue generally declines over time for the larger banking and asset-management groups, suggesting that revenue growth outpaced labor-cost growth.
- The lowest firm-year observations in the panel come from the early Bank of America / Merrill Lynch years, when both headcount and labor expense were very small.

## Federal Minimum Wage Benchmark

- The new benchmark panel adds the federal minimum wage, annualized to a full-time year and converted into 2025 dollars.
- The nominal federal minimum wage rose from `$0.75` per hour in 1950 to `$7.25` per hour in 2025, but the real annualized value is much flatter once inflation is removed.
- This makes the contrast with firm-level labor expense useful: the firms' labor costs per employee are far above the minimum-wage benchmark, and the gap widens over time.

## Interpretation

- The wage proxy is not a literal market wage for a marginal worker. It is total labor expense spread across employees.
- Even so, the series is informative because it shows how expensive labor is for these firms in aggregate and how that cost evolved relative to revenue.
- Compared with the minimum wage, the financial firms' labor spending is clearly not a low-wage story. The data instead point to high and rising labor expense per employee, especially after inflation adjustment.

## Lowest Observations

The exported table [`lowest_labor_per_employee.csv`](/Users/xiang/github/AI_EcoMetrics/simple_analysis/tables/lowest_labor_per_employee.csv) lists the ten lowest labor-expense-per-employee firm-year observations in the sample. These are useful as a diagnostic check on the bottom of the distribution.
