---
name: launch-readout
description: Use when the user wants to know how a launched feature or experiment performed, asks for a post-launch review, readout or retro, or says "did it work". Compares actual results with the concept's success metrics and records what was learned.
---

# Launch readout

Closes the loop: did the thing we built do the job we said it would? Read
`../../reference/evidence-rules.md` first; rules 4–6 matter most here.

## Steps

1. Read `work/<item>/02-concept.md` (success metrics, targets, guardrails) and
   `05-tickets.md` (analytics events, launch date).
2. For each metric, pull the actual value for the agreed window using the governed definitions
   in `context/metrics.md`. Show each query or dashboard. Compare with the baseline and target.
3. Check guardrails. A guardrail breach is reported first, even if the primary metric won.
4. Look for confounders: other launches, seasonality, marketing pushes, outages in the same
   window. Say how confident the comparison is.
5. Pull qualitative signals since launch (support, chat, meeting notes) about the feature.
6. Write the verdict plainly: **worked**, **partly worked**, **didn't work** or **too early to
   tell**, and what to do next (iterate, scale, roll back, revisit).

## Output: `work/<item>/06-launch-readout.md`

```
# <Title> · Launch readout (window: … to …)
**Verdict:** … · **Recommendation:** …

| Metric | Baseline | Target | Actual | Source |
| Guardrails | … |

## What users said
## Confounders and confidence
## What we learned
```

Then propose a decision-log entry and context updates (via `/pm-harness:update-context`), and
set `stage: launched` in `01-idea.md`.
