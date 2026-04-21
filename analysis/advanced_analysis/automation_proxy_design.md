# Feasible Automation Proxy for the Advanced Analysis

The goal is to measure how exposed a financial firm is to automation, without building a complicated task index that is hard to maintain.

## Recommendation

Use a **text-based automation exposure proxy** built from annual filings.

This is the most feasible option because it can be constructed for many firms with the same procedure and does not require occupation-level staffing data.

## Main Proxy: Automation Language Intensity

Define automation exposure as the intensity of automation-related language in a firm's annual report or 10-K.

### Basic idea

Firms that discuss more:

- automation
- systems
- digitization
- workflow
- straight-through processing
- electronic trading
- machine learning
- artificial intelligence
- models
- platform efficiency

are likely more advanced in automation adoption or more exposed to it.

### Simple formula

For firm `i` in year `t`:

```text
AutomationProxy_it = AutomationTermCount_it / TotalWordCount_it
```

Where:

- `AutomationTermCount_it` is the number of times automation-related terms appear in the filing
- `TotalWordCount_it` is total filing length

You can scale this by 1,000 or 10,000 words for readability.

### Example implementation

Create a dictionary of terms:

- automation
- automated
- automation
- digitization
- digital
- algorithm
- algorithms
- machine learning
- artificial intelligence
- AI
- robotics
- workflow
- straight-through processing
- electronic trading
- platform
- system upgrade

Then compute:

```text
AutomationProxy_it = (# of matched terms) / (total words in filing)
```

## Why this is feasible

- It can be applied to a large sample of firms.
- It uses public filing text.
- It does not require occupation-level employment data.
- It can be updated year by year.
- It is transparent and reproducible.

## What it captures

This proxy is not a perfect measure of true automation.

It captures a mix of:

- actual automation adoption
- managerial emphasis on technology
- disclosure style
- strategic positioning

That is acceptable for a first advanced proxy if you are clear about the interpretation.

## How to improve it

If you want a better version, split the proxy into two components:

### 1. Automation adoption terms

Words that suggest actual process automation:

- automation
- automated
- straight-through processing
- workflow automation
- electronic processing
- robotic process automation

### 2. AI / analytics terms

Words that suggest advanced software and model-based automation:

- artificial intelligence
- machine learning
- predictive analytics
- algorithm
- model governance
- data science

Then build:

```text
AutomationProxy_it = z(AdoptionTerms_it) + z(AITerms_it)
```

This is still simple, but more informative.

## Alternative Proxy if Text Is Too Hard

If filings are not available or text processing is too heavy, use a **technology expense proxy** from Compustat:

```text
TechIntensity_it = xlr_it / emp_it
```

where `xlr` is labor-related expense in the dataset.  
But this is not a pure automation measure, so it is weaker than the text proxy.

Another fallback is:

```text
AutomationProxy_it = log(revenue per employee)
```

This is easy, but it is really an outcome proxy, not an input proxy, so it should only be used as a rough descriptive measure.

## Preferred Research Design

Once the proxy is built, estimate:

```text
log(Revenue per employee)_it = firm FE + year FE + beta * AutomationProxy_it + controls + error
```

Possible controls:

- firm size
- profitability
- market conditions
- AUM
- business line mix

## Interpretation

- Higher automation proxy values should correspond to more scalable operations.
- If the coefficient on the proxy is positive, firms with more automation language tend to have higher revenue per employee.
- If the coefficient is negative for employment, that suggests automation is associated with lower labor intensity.

## Practical Recommendation

Start with the text-based proxy and keep it simple:

1. extract annual filing text
2. count automation-related words
3. normalize by total words
4. use the result as the main automation exposure variable

This is the most feasible advanced proxy because it is easy to explain, scalable, and compatible with a larger firm sample.

