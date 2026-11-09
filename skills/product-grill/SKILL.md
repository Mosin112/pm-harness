---
name: product-grill
description: Use when an idea, PRD, requirement or stakeholder request is fuzzy, when the user says "grill me" or "challenge this", or before writing a PRD whose actors, states, scope, phase or trade-offs are unclear. Asks one question at a time with a recommended answer, checks the workspace before asking, and records settled terms, decisions and the prototype decision.
---

# Product grill

Interview the PM one question at a time before the thinking hardens into a PRD. This is a
shaping conversation, not a review report and not a document generator.

- Ask **one** question, then wait.
- Answer from the workspace before asking the PM.
- Recommend an answer with every question.
- Challenge fuzzy or conflicting language straight away.
- Record terms and decisions only once they have settled, and only with approval.
- Do not write the PRD here; hand over to `write-prd` when the PM is ready.

## Start here

Read before the first question: `work/<item>/01-idea.md` (if it exists),
`context/users.md`, `context/product.md`, `context/strategy.md`, `context/constraints.md`,
`context/glossary.md`, `decisions/decision-log.md`, `../../reference/phases.md`, and anything
the PM points to (a request, a transcript, research in `signals/`).

If the workspace answers a question, use that answer and say where it came from. If the brief
is too thin to start, ask only for the smallest useful brief: the idea, who it is for, and when
a decision is needed.

## The loop

Privately pick the riskiest unresolved ambiguity, then ask exactly one question in this form:

```
**Question:** <the ambiguity or decision to resolve>
**Why it matters:** <what it changes downstream: requirements, trees, metrics, risk, rollout>
**My recommendation:** <your proposed answer and why>
**Changes:** <which PRD section or tree this settles>
```

Then stop and wait. Prefer questions that force a decision over open brainstorming. Never send
a questionnaire. When the PM answers, restate the settled point in one line before moving on.

## What to challenge, in rough priority

1. **Problem and job:** is it a real problem in the customer's terms, or a solution looking for
   one? What do people do today?
2. **Actors:** `investor`, `user`, `customer`, `member`, `operator`, `admin`: who exactly?
3. **States:** `verified`, `active`, `pending`, `triggered`, `failed`, `closed`: what are the
   states and who can be in each?
4. **Phase:** `MVP`, `MMP`, `MLP` or `Enhancement`? Recommend one from the evidence grade.
5. **Scope and non-goals:** what is tempting but out of this phase? What moves to *Later*?
6. **Failure paths:** what happens when it goes wrong, offline, at a limit, without permission?
7. **Obligations:** constraints from `context/constraints.md`, audit, permissions, analytics.
8. **The prototype decision:** the one design trade-off the prototype variants should argue
   about, with both sides named ("one-step setup (speed) versus a preview of the message
   (confidence)").
9. **Contradictions** with the glossary, past decisions or other items in `work/`.

When language is fuzzy, name the ambiguity and propose the canonical term. When a boundary is
unclear, use a concrete scenario to force precision ("an unverified investor taps Set price
alert: what do they see?").

## What to record

- **Glossary:** propose a row for `context/glossary.md` when a term will recur across PRDs,
  trees and conversations. Not for one-off wording.
- **Decision log:** propose an entry in `decisions/decision-log.md` (its existing format) only
  when the decision is all three: **durable** (shapes more than one artefact or conversation),
  **non-obvious** (a future reader would ask why), and **trade-off based** (real alternatives
  existed). Most answers belong in the PRD instead.
- **Prototype decision:** capture it word for word; `write-prd` puts it in §6.3 and
  `build-prototype` builds one variant per side.

Never write to the glossary or the decision log without the PM approving the exact text.

## Stop and hand over

When the PM is ready to stop (or the riskiest ambiguities are settled), write
`work/<item>/01-grill.md`. If there is no item yet, run `capture-idea` first so the grill has a
home; if the request may never become an item (a stakeholder ask you are only exploring), write
`signals/YYYY-MM-DD-grill-<topic>.md` instead and link it from the item if one follows.

```
# <Title> · Grill (YYYY-MM-DD)
**Phase:** <recommended or agreed phase, and why>
**Prototype decision:** <the trade-off, both sides named>

## Settled
- <point> (→ PRD §<n>)
## Still open
| Question | Owner |
## Glossary and decisions
- <added / proposed / declined>
```

Then recommend one next step: the `write-prd` skill, the `desktop-research` or
`opportunity-brief` skill if evidence is missing, or pausing for a decision-maker.
