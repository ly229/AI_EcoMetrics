---
name: sum-academic-author
description: Summarize an academic author into an author folder with one author overview markdown file and a selected-works subfolder of paper summaries, focused on technology, automation, AI, and labor-market implications.
---

# Academic Author Summaries

Use this skill when the user asks to summarize an academic author, especially for economists and adjacent researchers working on technology change, automation, AI, productivity, or labor markets.

## Workflow

1. Create a folder named after the author under `economist/`.
2. Create one author overview file named `<author-key-word>.md` inside that folder.
3. Create a `most-selected-works/` subfolder.
4. Add one markdown file per selected paper in `most-selected-works/`, using `<paper-name>.md`.
5. Focus the selected works on the papers most relevant to technology, automation, AI, and labor-market change.

## Author Overview File

The author overview file should include:

- `Official page`
- `Bio`
- `Focus`
- `Selected Works`
- `Most Relevant to This Study`

Keep the overview concise and practical.

## Selected Work Files

For each paper summary, include:

- `Author`
- `Year`
- `Source`
- `Key Idea`
- `Data`
- `Model / Method`
- `Why It Matters For This Study`

When the paper is empirical, identify the dataset and identification strategy.
When the paper is theoretical or conceptual, explain the framework and how it connects to labor-market change.

## Naming

- Use a clean folder name for the author, typically the author's full name.
- Use a slugged filename for the overview file, for example `Philippe-Aghion.md`.
- Use a slugged filename for each paper file, for example `Growth-and-the-Smart-State.md`.

## Selection Rule

Prefer works that best answer:

- How technology advances
- How automation changes tasks and jobs
- How AI or agentic systems shift labor demand, wages, and inequality
- How policy or institutions shape adjustment
