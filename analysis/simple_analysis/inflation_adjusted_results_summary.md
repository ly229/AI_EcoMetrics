# Inflation-Adjusted Results Summary

The inflation-adjusted results show that the long-run rise in productivity is real, but smaller than the nominal chart suggests.

## Main Observations

- `Revenue / employee` rises over time for all firm groups in real terms, but the growth is much less dramatic than in nominal dollars.
- `AUM / employee` also rises strongly for the groups with AUM data, especially `State Street family` and `JPMorgan family`.
- The AI-era increase is still visible, but inflation adjustment removes part of the apparent surge.
- Early decades look higher after adjustment because old nominal values are converted into 2025 dollars.
- The grouped figure makes clear that the trends differ across firm groups: some groups show steadier growth, while others have more uneven or incomplete AUM coverage.
- `JPMorgan family` shows a large gap between nominal and inflation-adjusted revenue per employee because many of its early observations are from the 1960s and 1970s, when the CPI deflator is much larger. Inflation adjustment lifts the early part of the series substantially, but the underlying long-run upward trend remains. So the adjustment changes the level more than the shape.

## Interpretation

- The nominal figures mix true productivity gains with general price-level growth.
- The real figures are better for comparing productivity across time because they isolate changes in output per worker from inflation.
- After adjustment, the evidence still supports a long-run increase in firm productivity, but the magnitude is more moderate.
- In other words, the finance firms did become more productive, but the nominal charts overstate how much of that increase reflects real economic change.

## Short Paper Version

Inflation adjustment attenuates the sharp upward trend seen in nominal productivity measures, but the long-run increase in revenue and AUM per employee remains clearly positive across firm groups. This indicates that part of the nominal growth reflects price-level changes, while a substantial share still reflects genuine productivity gains.

## Inflation Adjustment Mechanics

The inflation adjustment converts every nominal dollar amount into 2025 dollars using CPI-U. The formula is:

`real value = nominal value × (CPI in 2025 / CPI in that year)`

Applied to the productivity measures, this becomes:

`real revenue / employee = revt × (CPI_2025 / CPI_year) / emp`

`real AUM / employee = aum_crsp × (CPI_2025 / CPI_year) / emp`

This means the analysis is not changing the underlying business data. It is only rescaling older dollar amounts so that a dollar in 1950, 1960, or 1980 is comparable with a dollar in 2025. Because CPI was much lower in earlier decades, those observations receive a larger upward adjustment. More recent years receive little or no adjustment because they are already close to 2025 dollars.

## Why The Real Series Looks Different

The nominal chart combines two forces: actual changes in firm productivity and changes in the general price level. Once inflation is removed, the plot usually looks less explosive because part of the growth in the nominal series was simply the economy becoming more expensive over time. The real series is therefore the cleaner series for comparing productivity across decades.

That also explains why the inflation-adjusted plot can look more volatile. The deflator itself changes year by year, so the line is being reweighted across the whole sample. In addition, per-employee ratios already depend on both the numerator and the denominator, so any fluctuations in employment can create sharper year-to-year movement after adjustment.

## JPMorgan-Specific Note

`JPMorgan family` looks especially affected because much of its series begins in the 1960s and 1970s, when the CPI multiplier relative to 2025 is still large. As a result, the early part of the series is pushed up substantially in real terms. That creates a large gap between nominal and inflation-adjusted revenue per employee, but it does not imply a different underlying trend. The long-run pattern is still upward; the adjustment mainly changes the level of the series, not the direction of movement.

## Reading The Figure

The best way to interpret the inflation-adjusted figure is:

- the nominal chart shows how large the firms look in current dollars
- the real chart shows how much productivity growth remains after removing the price level
- the difference between the two is the portion of growth that can be attributed to inflation

Taken together, the results suggest that finance firms did become more productive over time, but the nominal figures exaggerate the size of that improvement because they embed decades of inflation.
