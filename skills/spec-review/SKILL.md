---
name: spec-review
description: Use when the user wants feedback on, a critique of, or a review of a PRD, spec, concept doc, behaviour trees or plan before sharing it. Runs independent reviewers (engineering, design, risk, executive, customer advocate) in fresh contexts and consolidates their findings.
---

# Independent spec review

A reviewer that wrote the draft defends it. This skill gets independent critique by running
each reviewer in a fresh context that has not seen the drafting conversation.

## Needs

None: works from the workspace files.

## Steps

1. Identify the document(s) to review, usually `work/<item>/02-prd.md` and, if present, the
   trees in `work/<item>/03-trees/`. Read the PRD's `Phase:`.
2. **Pick the reviewers for the phase** (`../../reference/phases.md`): all five for `MVP`,
   `MMP` and `MLP`; for an `Enhancement`, engineering, design and risk, plus exec and customer
   advocate when the change is visible to customers or leadership.
3. **Run each reviewer independently,** giving it only the document paths and the `context/`
   files its definition names, not this conversation:
   - `engineering-reviewer`, `design-reviewer`, `risk-reviewer`, `exec-reviewer`,
     `customer-advocate` (definitions in `../../agents/`).
   - **If your tool can start subagents,** launch them in parallel, one per reviewer.
   - **If it cannot,** run them one at a time. For each, read only the reviewer's definition,
     the document and the context files it lists, write its findings, then move on. Do not
     use what you remember from drafting to excuse a finding; note in the review file that
     the reviewers ran sequentially.
4. Each returns findings as `blocking`, `important` or `nit`, each with the section it refers
   to (`§5.2`) and a concrete suggested change. For an `MLP`, design findings about polish
   count as blocking.
5. **Consolidate:** merge duplicates, keep the reviewer names, sort by severity. Do not soften
   or drop findings you disagree with; add your view beside them instead.

## Output

One review file per document, so reviewing the trees never overwrites the PRD's trail:

- the PRD → `work/<item>/02-prd-review.md`
- the trees → `work/<item>/03-trees-review.md`

Each review is a dated round. A later round (a re-review after a change, or of changed sections
only) is **appended** under its own heading; earlier rounds and their resolutions stay.

```
# <Title> · Review (YYYY-MM-DD)
Reviewers: engineering, design, risk, exec, customer advocate (independent subagents)
Scope: whole PRD | §5.2 and §7 only (after change log row 3)

| # | Severity | Reviewer | Section | Finding | Suggested change | Resolution |
|---|---|---|---|---|---|---|
| 1 | blocking | risk | §6.1 | … | … | (filled in after revision) |
```

After the PM and the author revise the document, fill in the **Resolution** column for every
blocking and important finding: `changed`, `won't change because …`, or `open`.

A PRD or a set of trees cannot be approved while any blocking finding in any round is `open`.
