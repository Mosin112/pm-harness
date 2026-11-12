---
name: product-grill
description: Use when the PM wants to brainstorm or explore a problem or idea, says "grill me" or "challenge this", or before writing a PRD whose problem, actors, states, scope, phase or trade-offs are unclear. Explores first if the problem is open (How Might We, opportunity solution tree, riskiest assumptions), then converges one question at a time with a recommended answer, and records settled terms, decisions and the prototype decision.
---

# Product grill

Shape the thinking before it hardens into a PRD, in two modes:

- **Explore** (diverge) when the problem or the solution is still open: widen the options,
  then find the riskiest assumption. The explore mode is adapted from Anthropic's
  product-management plugin (Apache-2.0).
- **Grill** (converge) when there is a direction: one question at a time until the PRD can be
  written.

Start in explore mode if the PM says "brainstorm" or "explore", or if the idea card names a
solution but not a problem; otherwise go straight to the grill. This is a conversation, not a
report or a document generator.

- Ask **one** question, then wait.
- Answer from the workspace before asking the PM.
- Recommend an answer with every question.
- Challenge fuzzy or conflicting language straight away.
- Record terms and decisions only once they have settled, and only with approval.
- Do not write the PRD here; hand over to `write-prd` when the PM is ready.

## Needs

None: works from the workspace files.

## Start here

Read before the first question: `work/<item>/01-idea.md` (if it exists),
`context/users.md`, `context/product.md`, `context/strategy.md`, `context/constraints.md`,
`context/glossary.md`, `decisions/decision-log.md`, `../../reference/phases.md`, and anything
the PM points to (a request, a transcript, research in `signals/`).

If the workspace answers a question, use that answer and say where it came from. If the brief
is too thin to start, ask only for the smallest useful brief: the idea, who it is for, and when
a decision is needed.

**Never ask twice.** Keep a running list of settled points (the *Settled* list that goes into
`01-grill.md`). Before every question, check it, the idea card and what the PM has already
said. Ask about a settled point again only when new evidence has appeared, and say what it is.
A risk the idea card already records (a past decision, an evidence gap) is built on, not
raised again.

## Explore mode

Keep it to one sitting and a handful of exchanges; the aim is better options, not more notes.

1. **Frame:** restate the problem as two or three *How might we…* questions at different
   altitudes (narrow, the job itself, the bigger outcome). Ask the PM which one to work on.
2. **Map the opportunity:** a small opportunity solution tree for the chosen question, with
   the outcome (a metric from `context/metrics.md`), the two to four opportunities under it (user
   problems, with their evidence counts from `signals/` or the idea card), and the solutions
   under each.
3. **Diverge:** offer three to five genuinely different directions, including at least one
   non-obvious one (a policy change, a partner, a manual first version) and "do nothing". One
   line each on what it bets on.
4. **Find the riskiest assumption** behind the direction the PM leans to: desirability (they
   want it), viability (it works for the business and regulators), feasibility (we can build it),
   usability (they can use it). Propose the cheapest test for it, such as the evidence to look
   for, five interviews, or a fake door, and say what result would change the plan.
5. **Converge:** when the PM picks a direction, switch to the grill. Keep the directions that
   were not taken, and why, for the summary.

Push back like a sparring partner: name the weak link, ask what would have to be true, never
just list ideas. Do not treat a solution the PM brought as the problem.

## The grill

Privately pick the riskiest unresolved ambiguity, then ask exactly one question in this form:

```
**Question:** <the ambiguity or decision to resolve>
**Why it matters:** <what it changes downstream: requirements, trees, metrics, risk, rollout>
**My recommendation:** <your proposed answer and why>
**Changes:** <which PRD section or tree this settles>
```

Then stop and wait. Prefer questions that force a decision over open brainstorming. Never send
a questionnaire. When the PM answers, restate the settled point in one line before moving on.

When a constraint, a past decision or the capacity rules an option out, recommend the cut
plainly. Do not offer a narrower version of the ruled-out option unless the PM asks for one: a
pre-offered fallback turns a settled point into a negotiation.

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
  existed). Most answers belong in the PRD instead. A decision that needs someone else's
  agreement (a past decision to supersede, an exception) is written with `Status: proposed`
  and becomes `accepted` when they agree.
- **Prototype decision:** capture it word for word; `write-prd` puts it in §6.3 and
  `build-prototype` builds one variant per side.

Never write to the glossary or the decision log without the PM approving the exact text.

## Stop and hand over

Before you hand over, run two short checks and settle or record what they find:

1. **Scope against capacity.** List what is now in scope and compare it with the capacity in
   `context/strategy.md` or the sources (people, weeks, other commitments of the teams named).
   If it does not fit, recommend what to cut first.
2. **Pre-mortem.** "It is 30 days after launch and this failed or was abused. What happened?"
   Name the top three answers: abuse and fraud paths, a constraint broken, adoption that never
   came. Each becomes a settled point, an open question or a risk for the PRD.

When the PM is ready to stop (or the riskiest ambiguities are settled), write
`work/<item>/01-grill.md`. If there is no item yet, run `capture-idea` first so the grill has a
home; if the request may never become an item (a stakeholder ask you are only exploring), write
`signals/YYYY-MM-DD-explore-<topic>.md` instead and link it from the item if one follows.

```
# <Title> · Grill (YYYY-MM-DD)
**Phase:** <recommended or agreed phase, and why>
**Prototype decision:** <the trade-off, both sides named>

## Settled
- <point> (→ PRD §<n>)
## Directions explored (if explore mode ran)
- <direction>: <taken / not taken, and why> · riskiest assumption and its test

## Scope and capacity
<what is in scope · the capacity it needs · the cut order if it does not fit>
## Pre-mortem
- <failure or abuse path> → <settled / open question / PRD risk>

## Still open
| Question | Owner |
## Glossary and decisions
- <added / proposed / declined>
```

Then recommend one next step: the `write-prd` skill, the `desktop-research` or
`opportunity-brief` skill if evidence is missing, or pausing for a decision-maker.
