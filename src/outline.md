1) Title (working)
“From Clerks to Code: How Technology Impacted Labor in Asset Management?”

2) Core Idea (1–2 paragraphs)
•	Financial firms have gone through three technological waves:
1.	Computerization (1980s–1990s)
2.	Index investing (2000s–2010s)
3.	AI / automation (2015–present)
•	This project tracks how much labor is needed to manage capital across these waves.
•	Key metric:
AUM per Employee = Labor productivity in asset management


3) Firms (keep it simple but representative)
Pick 3–4 firms with long history + different models:
•	JP Morgan (scale + AI + ETFs)
•	Vanguard Group (pure passive pioneer)
•	Fidelity Investments (active + retail)
•	State Street Global Advisors (ETF + institutional)
👉 Why this works:
•	Covers active vs passive
•	Covers different adoption speeds
•	All have long time series (or close enough)

4) Periodization (simple and transparent)
Define 3 phases:
•	Phase 1: Computerization (≈1985–2000)
Rise of IT, electronic trading, back-office automation
•	Phase 2: Indexing (≈2000–2015)
Explosion of ETFs and passive funds
•	Phase 3: AI / Automation (≈2015–present)
AI, big data, quant platforms
👉 You don’t need to prove these breakpoints — just motivate them historically.

5) Key Metrics (keep it minimal)
For each firm-year:
(1) Main metric
•	AUM per Employee
(2) Supporting metrics
•	Revenue per employee
•	Operating expense / AUM
•	(Optional) Passive share of AUM

6) Output (what you’ll show)
Figure 1 (most important)
•	Time series of AUM per employee by firm
Figure 2
•	Growth rate of AUM vs employees
Figure 3 (optional)
•	Passive share vs labor productivity

7) Narrative Structure (very simple)
Section 1: Computerization
•	Slow improvement in productivity
•	Reduction in clerical labor
Section 2: Indexing
•	Sharp increase in AUM per employee
•	Passive funds require fewer workers
Section 3: AI
•	Continued increase
•	Potential flattening or shift in labor composition

8) Data Pipeline (Feasible + Realistic)
Here’s the key part — something you can actually build.

Step 1: Firm Financials (Core)
Source: Compustat (via WRDS)
Variables:
•	Employees (EMP)
•	Revenue (REVT)
•	Operating expenses
•	Firm identifiers (GVKEY)
👉 Works well for:
•	BlackRock
•	State Street Corporation
⚠️ Limitation:
•	Vanguard Group and Fidelity Investments are private → not fully in Compustat

Step 2: AUM Data (Most Important)
Option A (Best practical approach)
Manual + semi-automated collection from:
•	Annual reports (10-K for public firms)
•	Company fact sheets / websites
Examples:
•	BlackRock: AUM disclosed in 10-K
•	Vanguard: publishes annual reports
•	Fidelity: partial disclosures
👉 Build a panel dataset manually (CSV):

Firm | Year | AUM | Employees | Revenue


Step 3: Passive vs Active Exposure (Optional but powerful)
Sources:
•	Morningstar Direct (if you have access)
•	CRSP Mutual Fund database
Construct:
•	Passive AUM share (by firm, approximate)
👉 Even rough estimates (e.g., ETFs vs total AUM) are enough for your purpose.

Step 4: AI Exposure (Light-touch, not heavy NLP)
Simple proxies:
•	Count mentions of “AI”, “machine learning” in 10-K
•	Or create a dummy variable:
◦	0 before 2015
◦	1 after 2015
👉 Since this is fact analytics, keep it simple.

Step 5: Build Final Dataset
Structure:
Firm	Year	AUM	Employees	Revenue	AUM/Employee	Phase


Step 6: Implementation (Python-friendly)
You can do everything in pandas:
•	Merge Compustat + manual AUM
•	Compute:

df["aum_per_employee"] = df["AUM"] / df["EMP"]

•	Plot trends (matplotlib)

9) What Makes This Work
This approach works because:
•	You’re not claiming causality
•	You’re showing stylized facts
•	You connect:
Technology → scalability → labor efficiency


10) Expected Findings (What you’ll likely see)
•	Computer era: gradual improvement
•	Indexing era: big jump in AUM per employee
•	AI era: continued increase, maybe slower but more skill-biased

11) Optional Add-on (if you want to level it up slightly)
•	Compare:
◦	Passive-heavy firms vs active-heavy firms
•	Show:
Vanguard vs Fidelity divergence

