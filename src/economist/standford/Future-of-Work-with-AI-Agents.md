# Future of Work with AI Agents: Auditing Automation and Augmentation Potential across the U.S. Workforce

Authors: Yijia Shao, Humishka Zope, Yucheng Jiang, Jiaxin Pei, David Nguyen, Erik Brynjolfsson, Diyi Yang

Affiliation: Stanford University

Data and code: futureofwork.saltlab.stanford.edu

## Abstract

This paper studies how workers and AI experts think about AI agents in the workplace. The authors argue that the rise of compound AI systems is reshaping labor markets, but current research lacks a systematic way to compare what workers want AI to automate or augment against what the technology can actually do.

To address this, they introduce an auditing framework built around two core ideas:

- an audio-enhanced mini-interview to capture worker preferences in context
- the Human Agency Scale (HAS), a shared language for measuring the preferred level of human involvement

Using O*NET tasks, they build WORKBank, a database that combines responses from 1,500 domain workers and capability assessments from AI experts across 844 tasks in 104 occupations. The paper divides tasks into four zones based on worker desire and technological capability:

- Automation Green Light Zone
- Automation Red Light Zone
- R&D Opportunity Zone
- Low Priority Zone

The authors find clear mismatches between worker desires and current AI capabilities, along with signs that AI agents may shift the importance of human skills away from information processing and toward interpersonal work.

## 1. Introduction

Large language models and other foundation models have accelerated interest in AI agents: goal-directed systems that can plan, use tools, and carry out multi-step workflows. These systems are already starting to affect labor markets, but the landscape remains poorly understood.

The paper identifies three limitations in prior work:

- narrow coverage of occupations and tasks
- an emphasis on capital-side productivity rather than worker preferences
- dependence on observed usage data instead of forward-looking task audits

The authors respond with a task-level, worker-centric framework. Key design choices include:

- focusing on computer-compatible tasks from O*NET
- soliciting first-hand feedback from workers actively performing those tasks
- using the Human Agency Scale to move beyond a binary automate-or-not framing
- collecting expert assessments of current AI capability to compare against worker preferences

The resulting database, WORKBank, is presented as the first large-scale audit of both worker desire and AI capability for occupational tasks.

### Main Findings

The paper highlights four headline results:

1. Workers want automation for many repetitive and low-value tasks.
2. Worker desire and AI capability create four distinct task zones, with major mismatches between demand and investment.
3. The Human Agency Scale reveals that workers often prefer meaningful collaboration rather than full automation.
4. Human skill demand appears to be shifting from information processing toward interpersonal and organizational competencies.

## 2. Auditing Framework

The auditing framework is designed to capture both automation and augmentation preferences at the task level. It uses task-specific worker feedback and AI expert assessments to build a more complete picture of the future of work.

### 2.1 Defining Audit Granularity and Scope

The framework focuses on complex, multi-step tasks tied to occupations, rather than isolated low-level actions. This matters because tasks within the same occupation can vary substantially and often depend on context.

The audit is limited to computer-compatible tasks, since those are most susceptible to AI agents powered by foundation models. The paper defines AI agents as systems that can autonomously perform tasks by designing workflows and using software tools, but not physical actions.

### 2.2 The Spectrum of Automation and Augmentation

The authors argue that prior work overemphasizes automation. They introduce the Human Agency Scale (HAS), a five-level scale that measures how much human involvement is desired or required:

- H1: the AI agent completes the task entirely on its own
- H2: minimal human input is needed
- H3: human and AI work as equal partners
- H4: human input is required for successful completion
- H5: continuous human involvement is essential

HAS complements traditional automation scales by centering human agency. The important distinction is not whether higher levels are better, but which level fits the task and the role of the AI system.

### 2.3 Constructing a Worker-Centric Framework

For each task `t`, workers report:

- automation desire `A_w(t)`
- desired HAS level `H_w(t)`

Both are measured using 5-point Likert scales.

The survey is designed to support calibrated responses through three features:

- Audio-enhanced reflection: a short spoken interview helps workers explain their work and AI views in their own words.
- Familiarity filtering: workers rate only tasks relevant to their occupation and confirm they know the task.
- Guided consideration: respondents are prompted to reflect on enjoyment, job security, domain expertise, uncertainty, and interpersonal factors.

### 2.4 Combining Worker and Expert Perspectives

The worker perspective reflects social demand, but workers may not fully know current AI capabilities. To address that, the authors also collect expert assessments of:

- automation capability `A_e(t)`
- feasible HAS level `H_e(t)`

This dual-perspective approach makes it possible to identify alignment, mismatch, and research opportunities.

### 2.5 Building WORKBank

The authors instantiate the framework using O*NET tasks performed at least monthly by computer-using occupations. After filtering, they retain 2,131 tasks across 287 occupations.

Survey recruitment happened through Prolific, Upwork, and LinkedIn between January and May 2025. After filtering for sufficient representation, the final dataset includes:

- 1,500 workers
- 104 occupations
- 7,016 task ratings
- 52 AI experts
- 844 tasks with worker and expert annotations

Inter-annotator agreement is moderate, and the authors compare sector coverage against Bureau of Labor Statistics data to show that WORKBank captures a broad slice of the U.S. workforce.

## 3. Results

The analysis focuses on where workers want AI agents to automate, where they resist automation, how these preferences align with technical capability, and how AI may reshape skills.

### 3.1 Worker-Centered Views on Occupational Task Automation

Workers are broadly positive about automating some tasks, especially low-value and repetitive ones. The paper reports that 46.1% of tasks receive positive automation desire from workers.

The main motivation is time reallocation:

- freeing up time for higher-value work
- reducing repetitive work
- lowering stress
- improving quality

The authors also compare these preferences with Claude.ai usage data and find a mismatch: the occupations with the highest automation desire account for only a small share of observed chatbot usage. This suggests that usage logs do not fully reflect workplace demand.

#### Where Workers Resist Automation

Resistance is driven by several concerns:

- lack of trust in AI accuracy or reliability
- fear of job replacement
- loss of human qualities, creativity, or decision-making agency

The arts, design, and media sector shows particularly strong resistance to content creation automation.

### 3.2 The Desire-Capability Landscape

The paper combines worker desire `A_w(t)` and expert capability `A_e(t)` to define four task zones:

1. Automation Green Light Zone: high desire, high capability
2. Automation Red Light Zone: high capability, low desire
3. R&D Opportunity Zone: high desire, low capability
4. Low Priority Zone: low desire, low capability

The authors find that worker desire and expert capability are only weakly correlated. They also report that automation desire tends to be lower for tasks workers enjoy or associate with job-loss concerns.

#### Investment Mismatches

The paper maps Y Combinator companies to tasks and finds that investment is spread unevenly across the four zones. Many mapped tasks concentrate in software development and business analysis, while some promising tasks in the Green Light and Opportunity zones remain under-addressed.

#### Research Coverage

The authors also map AI agent papers from arXiv to tasks. Research is more concentrated in the R&D Opportunity Zone, but still focused heavily on computer science and engineering tasks.

### 3.3 Human Agency Scale Spectrum

The Human Agency Scale reveals that workers generally want more human involvement than experts think is technologically necessary.

Key observations:

- 26.9% of tasks have matching worker and expert HAS ratings
- 47.5% of tasks fall in the region where workers prefer more human agency than experts expect
- H3, equal partnership, is the dominant worker preference in many occupations

The paper also identifies occupations at the extremes:

- several occupations are rated as H1-dominant by experts
- very few occupations are dominated by H5
- workers most often associate H5 tasks with interpersonal communication
- experts associate H5 tasks with both interpersonal communication and domain expertise

#### Envisioned Human-Agent Collaboration

Workers describe several collaboration patterns:

- role-based support, where AI fills a specific function
- assistant-like support, where AI helps but humans review outputs
- partial automation for selected workflow components

The dominant theme is not replacement, but collaboration.

### 3.4 Potential Shift in Core Human Skills

The authors map tasks to O*NET skills and compare average wage rankings with average required human agency.

They identify three broad trends:

- information-processing skills may decline in relative importance
- interpersonal and organizational skills may become more important
- high-agency work spans a wider set of competencies than simple data work

The implication is that AI agents may reshape which human skills are most valued in the workplace.

## 4. Related Work

### Digital AI Agents

The paper situates AI agents in a long line of work on autonomous systems and multi-step problem solving. Recent LLM-based agents can already handle software engineering, analytical writing, and customer support tasks.

The authors also connect to work on human-agent collaboration, arguing that AI can augment rather than replace workers when tasks require coordinated human input.

### Economic Impacts of Generative AI

The paper builds on prior research on the labor market effects of AI and generative models. It differs from earlier studies by explicitly incorporating worker desire and by focusing on AI agents rather than only chatbots.

## 5. Conclusion

The paper argues that AI agents may reshape work in ways that are both technical and social. Its main contribution is a large-scale audit of worker desire and technological capability for occupational tasks.

The key takeaways are:

- many workers support automation of repetitive tasks
- worker preferences and technical feasibility do not always align
- collaboration is often preferred over full automation
- AI agents may shift the demand for human skills toward interpersonal and organizational work

The authors also emphasize that worker reskilling and retraining will likely be important as these systems evolve.

## Limitations

The paper notes several limitations:

- O*NET task definitions may miss new tasks that emerge as AI systems evolve
- workers may not fully understand current AI capabilities
- some workers may understate concerns due to job security or surveillance fears
- the dataset covers 104 occupations, not the full O*NET universe
- the results reflect the state of generative AI and agentic systems in early 2025

## Acknowledgements

The authors thank collaborators and lab members for distribution help, database setup, and feedback. They also acknowledge the participation of 1,500 domain workers and 52 AI experts, as well as support from ONR, NSF, and the Stanford Digital Economy Lab.
