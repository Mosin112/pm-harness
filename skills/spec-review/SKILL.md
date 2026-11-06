---
name: spec-review
description: Use when the user wants feedback on, a critique of, or a review of a concept doc, PRD, spec, behaviour trees or plan before sharing it. Runs independent reviewer subagents (engineering, design, risk, executive, customer advocate) in fresh contexts and consolidates their findings.
---

# Independent spec review

A reviewer that wrote the draft defends it. This skill gets genuinely independent critique by
running each reviewer as a separate subagent with a fresh context.

## Steps

1. Identify the document(s) to review, usually `work/<item>/02-concept.md` and, if present,
   the trees in `work/<item>/03-trees/`.
2. Launch these subagents **in parallel**, giving each only the document paths and the
   relevant `context/` files, not this conversation:
   - `engineering-reviewer`
   - `design-reviewer`
   - `risk-reviewer`
   - `exec-reviewer`
   - `customer-advocate`
3. Each returns findings as `blocking`, `important` or `nit`, each with a concrete suggested
   change.
4. **Consolidate:** merge duplicates, keep the reviewer names, sort by severity. Do not soften
   or drop findings you disagree with; add your view beside them instead.

## Output: `work/<item>/02-concept-review.md`

```
# <Title> · Review (YYYY-MM-DD)
Reviewers: engineering, design, risk, exec, customer advocate

| # | Severity | Reviewer | Finding | Suggested change | Resolution |
|---|---|---|---|---|---|
| 1 | blocking | risk | … | … | (filled in after revision) |
```

After the PM and the author revise the document, fill in the **Resolution** column for every
blocking and important finding: `changed`, `won't change because …`, or `open`.

A concept cannot be approved while any blocking finding is `open`.
