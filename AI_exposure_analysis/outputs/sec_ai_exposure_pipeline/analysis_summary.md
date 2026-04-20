# AI Exposure Panel FE Extension

Panel source: `simple_analysis/data/compustat_panel_by_firm_group.csv`
Exposure source: `AI_exposure_analysis/data/ai_exposure_by_firm_year.csv`

## Specification

`log1p(outcome_it) ~ ai_exposure_it + C(year) + C(firm)`

## Outputs

- merged panel: `AI_exposure_analysis/outputs/sec_ai_exposure_pipeline/merged_panel_with_exposure.csv`
- revenue_per_employee regression: `AI_exposure_analysis/outputs/sec_ai_exposure_pipeline/revenue_per_employee_ai_exposure_fe.txt`
- aum_per_employee regression: `AI_exposure_analysis/outputs/sec_ai_exposure_pipeline/aum_per_employee_ai_exposure_fe.txt`
- labor_expense_per_employee regression: `AI_exposure_analysis/outputs/sec_ai_exposure_pipeline/labor_expense_per_employee_ai_exposure_fe.txt`
