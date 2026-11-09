---
name: launch-readout
description: Use when the user wants to know how a launched feature or experiment performed, asks for a post-launch review, readout or retro, or says "did it work". Compares actual results with the PRD's success metrics and launch gates and records what was learned.
---

# Launch readout

Closes the loop: did the thing we built do the job we said it would? Read
`../../reference/evidence-rules.md` first; rules 4–6 and 9 matter most here.

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs launch-readout` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `governed-metrics` or `product-analytics` · required · actual values of the PRD §7 metrics and
  guardrails
- `support-feedback`, `team-chat` or `meeting-notes` · optional · what users said since launch
- `market-data` or `web-research` · optional · market moves and outside benchmarks that may
  explain a result, labelled external

## Steps

1. Read `work/<item>/02-prd.md` (§7 success metrics, targets, guardrails and the phase's
   gate) and `05-tickets.md` (analytics events, launch date).
2. For each metric, pull the actual value for the agreed window using the governed definitions
   in `context/metrics.md`, from the tool `context/tools.md` trusts for that metric. Show each
   query or dashboard. Compare with the baseline and target.
3. Check guardrails. A guardrail breach is reported first, even if the primary metric won.
4. Look for confounders: other launches, seasonality, marketing pushes, outages in the same
   window, and outside moves (a market swing, a competitor's launch) from the `market-data` or
   `web-research` tools, labelled external with their source and date. Say how confident the
   comparison is.
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
## Confounders and confidence   (outside moves labelled external, with URL and date)
## What we learned
## Not measured                  (needs or tools that did not answer)
```

Then propose a decision-log entry and context updates (via the `update-context` skill), set
`stage: launched` in `01-idea.md` if it is not already, and add `readout: YYYY-MM-DD`.

Until the gate window ends, `metrics-review` tracks the item against its targets; this readout
makes the call at the end. Afterwards, offer the `roadmap` skill to move the item and any next
phase to the right column.

**If the gate says continue** to the next phase, offer to start it as a new linked item with the
`capture-idea` skill (`work/<item>-<phase>/`, `lineage: <item>`). Its PRD starts from this
readout and from the previous PRD's §4 *Later* list and §8.3 open questions. If the gate says
stop, log why and suggest parking related ideas with a "revisit if" condition.
