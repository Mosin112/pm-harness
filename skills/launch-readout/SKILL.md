---
name: launch-readout
description: Use when the user wants to know how a launched feature or experiment performed, asks for a post-launch review, readout or retro, or says "did it work". Compares actual results with the PRD's success metrics and launch gates and records what was learned.
---

# Launch readout

Closes the loop: did the thing we built do the job we said it would? Read
`../../reference/evidence-rules.md` first; rules 4–6 matter most here.

## Steps

1. Read `work/<item>/02-prd.md` (§7 success metrics, targets, guardrails and the phase's
   gate) and `05-tickets.md` (analytics events, launch date).
2. For each metric, pull the actual value for the agreed window using the governed definitions
   in `context/metrics.md`. Show each query or dashboard. Compare with the baseline and target.
3. Check guardrails. A guardrail breach is reported first, even if the primary metric won.
4. Look for confounders: other launches, seasonality, marketing pushes, outages in the same
   window. Say how confident the comparison is.
5. Pull qualitative signals since launch (support, chat, meeting notes) about the feature.
6. **Apply the phase's gate** from §7: for an MVP, continue or stop; for an MMP or MLP, whether
   the next rollout stage's launch gate is met.
7. Write the verdict plainly: **worked**, **partly worked**, **didn't work** or **too early to
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

Then propose a decision-log entry (including the next phase, if the gate says continue) and
context updates (via the `update-context` skill), and set `stage: launched` in `01-idea.md`.
