---
name: opportunity-brief
description: Use when the user wants to size, score or prioritise an idea or compare several ideas, asks "is this worth doing", or wants RICE/ICE scores. Produces a one-page sizing brief backed by governed metrics.
---

# Opportunity brief

Sizes an idea with real numbers before anyone writes a spec. Read
`../../reference/evidence-rules.md` first; numbers must follow rules 4 and 9.

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs opportunity-brief` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `governed-metrics` or `product-analytics` · required · reach and baselines
- `market-data` or `web-research` · optional · outside benchmarks for the impact assumption,
  labelled external

## Steps

1. Read the idea (`work/<item>/01-idea.md` if it exists), `context/strategy.md` and
   `context/metrics.md`.
2. **Reach.** How many users meet the job's situation in a typical month? Use the governed
   metric definitions and the tool `context/tools.md` trusts for each metric. Show each query
   or dashboard used.
3. **Impact.** Which metric moves, by how much, and why you believe it. Use a comparable past
   launch from `decisions/decision-log.md` or analytics if one exists. An outside benchmark
   (a competitor's published adoption, an industry rate) from `market-data` or `web-research`
   may inform the assumption: label it external with its URL and dates (evidence rule 9). It
   never stands in for our own data. With neither, say the impact is an assumption.
4. **Confidence.** High / medium / low, from the evidence grade of the idea.
5. **Effort.** Ask the PM or note it as unknown. Do not guess engineering effort.
6. **Score.** RICE = Reach × Impact × Confidence ÷ Effort. Show the inputs, not just the score.
   When comparing ideas, put them in one table.
7. **Fit.** One line on how it serves the current strategy, or why it does not.

## Output

Append an `## Opportunity` section to `work/<item>/01-idea.md` (or write
`work/opportunity-<date>.md` for a comparison):

```
## Opportunity
| Input | Value | Source |
|---|---|---|
| Reach | 18,400 users/month | <metric name> (<query or dashboard>) |
| Impact | 1 (medium) | assumption: comparable to <past launch> |
| Impact benchmark | <outside figure> | external: <URL> (published …, read …) |
| Confidence | 80% | evidence grade: strong |
| Effort | 3 person-weeks | engineering estimate from <name> |
| **RICE** | **4,907** | |
Strategy fit: …
What would change this score: …
```
