<!-- pm-harness-workspace -->
# PM workspace

This folder is a PM Harness workspace. Claude reads this file at the start of every session.
Keep it short: it routes to detail instead of containing it.

## What this workspace is for

Product work for **<team / product area>**, owned by **<PM name>**. Ideas move through a
pipeline, one folder per idea under `work/`:

```
01-idea.md → 02-concept.md (+ review) → 03-trees/ → 04-prototype/ → 05-tickets.md → 06-launch-readout.md
```

## Routing index (read only what the task needs)

| When the task involves… | Read |
|---|---|
| Company, market, business model | `context/company.md` |
| Product areas, flows, recent launches, design tokens | `context/product.md` |
| Goals, OKRs, priorities | `context/strategy.md` |
| Users, segments, known jobs and pains | `context/users.md` |
| Any number or metric | `context/metrics.md` |
| Who decides, who reviews, how they like updates | `context/stakeholders.md` |
| Regulatory, legal, risk, brand or platform limits | `context/constraints.md` |
| Which connector to use for what | `context/tools.md` |
| Internal terms | `context/glossary.md` |
| Tone, length, formats | `context/writing-style.md` |
| Past decisions | `decisions/decision-log.md` |

## Rules

1. Follow the evidence rules in the PM Harness plugin's `reference/evidence-rules.md`: count
   sources, quote real customer words only, grade evidence, take numbers from governed metric
   definitions and show where every number came from.
2. Never write to an external tool (tracker, wiki, chat, email) without the PM approving the
   exact content first.
3. Never rewrite a context file silently. Propose edits; apply only approved ones.
4. Keep each item's state in its files so any new session can resume from them.
5. When something is unclear, ask one sharp question rather than guessing.
