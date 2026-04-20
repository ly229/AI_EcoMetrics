# AI Exposure Figure Interpretation

## Coefficient Figure

- File: `AI_exposure_analysis/figures/ai_exposure_fe_coefficients.png`
- This figure shows the firm and year fixed-effects estimates for `ai_exposure` across the three outcome variables.

### Main Patterns

- `revenue_per_employee` has a negative and statistically significant coefficient on AI exposure.
- `aum_per_employee` has a positive and statistically significant coefficient.
- `labor_expense_per_employee` is small and not statistically significant.

### Interpretation

- Higher filing-based AI exposure is associated with lower revenue intensity per employee.
- Higher filing-based AI exposure is associated with higher AUM per employee.
- The labor-expense outcome does not show a clear substitution effect in this specification.

Taken together, the pattern looks more like organizational reallocation or business-mix change than a simple labor-cost compression story.

## Event-Study Style Figure

- File: `AI_exposure_analysis/figures/ai_exposure_event_study.png`
- This figure aligns each firm around the first year its AI exposure exceeds its own 2015-2017 baseline by a fixed margin.

### Main Patterns

- AI exposure rises over time for all five firms, but at different speeds.
- `BAC` rises earlier, beginning in the mid-2010s.
- `SPGI` shows the sharpest acceleration later in the sample.
- `JPM` and `STT` rise steadily after 2018 or 2019.
- `BK` crosses the threshold very late and has limited post-event support.

### Interpretation

- The exposure proxy is not flat or random; it trends upward across firms.
- The timing differs across firms, which is useful for later identification work.
- Because the event is defined mechanically from the exposure series, this is descriptive rather than causal evidence.

## Combined Takeaway

- The coefficient plot suggests AI exposure is associated with different operating outcomes in different ways.
- The event-study plot shows that exposure increases are staggered across firms rather than happening all at once.
- The current evidence is exploratory, but it is consistent with a finance-sector transition in which AI changes task allocation and business composition before it shows up as straightforward labor substitution.

