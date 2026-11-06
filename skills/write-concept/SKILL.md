---
name: write-concept
description: Use when the user wants a concept doc, one-pager, PRD, problem statement or jobs-to-be-done for an idea. Step 2 of the one-shot pipeline - writes the why (problem, JTBD, forces, success metrics, scope, risks), then sends it for independent review.
---

# Step 2 · Concept doc + JTBD

The concept doc is the *why*. It must be strong enough that a sceptical engineer, designer and
executive would all agree the problem is real and worth solving. The *what* comes later as
behaviour trees.

Read first: `work/<item>/01-idea.md`, `../../reference/jtbd.md`,
`../../reference/evidence-rules.md`, and from the workspace `context/users.md`,
`context/strategy.md`, `context/metrics.md`, `context/constraints.md`,
`context/writing-style.md`.

## Steps

1. **Challenge the problem first.** If the idea card's problem is vague, solution-shaped or
   a hunch, say so and ask the PM up to three sharp questions before writing. Do not polish a
   weak problem statement into a confident document.
2. **Write the job statement** in the form *When…, I want to…, so I can…*. Offer two
   alternatives if the situation could be framed differently, and let the PM pick.
3. **Map the forces** (push, pull, anxiety, habit) and **today's alternatives**, each backed by
   evidence where it exists.
4. **Outline the solution** at the level of capabilities and the user's path, not screens or
   implementation. Note which capabilities are new and which already exist.
5. **Set success metrics:** one primary metric tied to the job's outcome, one or two guardrails,
   each defined using `context/metrics.md`, with a baseline from data where available.
6. **Scope:** in scope, explicit non-goals, and what a later version might add.
7. **Risks and constraints:** check every item in `context/constraints.md` and say how the
   concept respects it. Add product, technical and adoption risks.
8. **Open questions,** each with an owner.
9. Keep it under two pages. Link out to evidence rather than pasting it.

## Output: `work/<item>/02-concept.md`

```
# <Title> · Concept
Status: draft · Owner: <PM> · Updated: YYYY-MM-DD · Evidence: <grade>

## Problem
## Job to be done
> When …, I want to …, so I can …
## Forces
| Push | Pull | Anxiety | Habit |
## Today's alternatives
## Proposed solution
## Success metrics
| Metric | Definition | Baseline | Target | Source |
## Scope
In: … · Not now: … · Later: …
## Risks and constraints
## Open questions
| Question | Owner |
```

## Gate

1. Run `/pm-harness:spec-review` on the concept (independent reviewers in fresh contexts).
2. Revise the concept to address every **blocking** finding, or record why not.
3. Ask the PM to approve. On approval set `stage: concept` and `updated:` in `01-idea.md`,
   change the concept's status to `approved`, and offer `/pm-harness:write-behaviour-trees`.
