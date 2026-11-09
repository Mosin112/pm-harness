---
name: metrics-review
description: Use when the PM wants a weekly, monthly or quarterly metrics review, asks "how are our numbers", needs to explain a spike or a drop, or wants a scorecard against targets. Reviews the product's metric hierarchy from governed definitions, tracks launched items against their PRD targets, and turns what it finds into actions.
---

# Metrics review

A recurring look at the product's health, from governed numbers only. `launch-readout` judges one
launch at its gate; this review watches everything in between and catches problems early.
Structure adapted from Anthropic's product-management plugin (Apache-2.0). Read
`../../reference/evidence-rules.md` first; rules 4–7 and 9 decide what may be written.

Read first: `context/metrics.md` (the hierarchy, definitions, owners, targets),
`context/strategy.md`, the PRD §7 of every item at stage `building` or `launched` (their metrics,
targets, guardrails and gate windows), recent `decisions/decision-log.md` entries, and the last
review in `updates/` for comparison.

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs metrics-review` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `governed-metrics` · required · current values against targets for every metric in the hierarchy
- `product-analytics` · optional · funnels and segments behind a change
- `market-data` or `web-research` · optional · outside benchmarks and market moves, kept apart and
  labelled external
- `team-chat` or `docs` · optional · known events in the window: launches, incidents, campaigns

## 1. Scope

Ask (or take from the last review): the **period** (week, month, quarter), the comparison
(previous period, same period last year, target), and any known events in the window (launches,
outages, campaigns, holidays).

If `context/metrics.md` has no hierarchy yet, settle it first with the PM: one **north star**,
four to six **level-1** health metrics (acquisition, activation, engagement, retention, revenue,
satisfaction: whichever apply), and the **level-2** diagnostics under each. Write it to
`metrics.md` on approval.

## 2. Gather

Take each metric's value from the tool `context/tools.md` trusts for it (`governed-metrics`,
or `product-analytics` for event-level metrics) with its governed definition. Show every query
or dashboard used. If a number cannot be pulled, say so and leave its cell empty; never
estimate one. If two internal tools disagree, show both and say which one is governed.

**External benchmarks** (optional): from the `market-data` or `web-research` tools, comparable
outside figures (an industry rate, a competitor's published number) and market moves that may
explain a change (an asset price swing, a competitor's launch). Each carries its URL, its
publication date and the date read, is labelled external, and goes in its own section: never in
the metrics table, and never a target unless the PM approves it.

## 3. Analyse

For each metric: current value, change against each comparison, trend direction and whether it is
speeding up, and status against target (`on track`, `at risk`, `miss`).

- **Guardrails first.** A breached guardrail leads the review, even when the north star is up.
- **Attribution:** link a change to a known event (a launch in `work/`, a decision, an outage, a
  campaign, an outside market move) only with evidence; otherwise say the cause is unknown.
  Check whether one segment drives an aggregate change.
- **Launched items:** for each item still inside its PRD gate window, show progress towards the
  gate, and flag one that will clearly miss so the readout is not a surprise.

## 4. Output: `updates/YYYY-MM-DD-metrics-<period>.md`

```
# Metrics review · <period> (<dates>)
**Summary:** <2–3 sentences: overall health, the biggest change, the call to make>

| Level | Metric | Current | Previous | Change | Target | Status | Source |
|---|---|---|---|---|---|---|---|

## Guardrails
## What changed and why (fact vs inference kept apart)
## Launched items against their gates
## External benchmarks
| Benchmark | Value | Compares with | Source (URL) | Published | Read |
## Actions
## Not measured / data problems   (including needs or tools that did not answer)
```

The metrics table's **Source** column names the internal tool and query or dashboard; external
figures appear only under *External benchmarks*.

## 5. Actions

Each concern becomes one of: an investigation (owner and question), an idea for `capture-idea`
(evidence counted), a `launch-readout` when a gate window has ended, an alert to set, or a
`metrics.md` change (a missing metric, a stale definition). Propose them; apply nothing without
approval. Never post the review to chat or email without the PM approving the exact text.
