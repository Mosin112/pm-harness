---
name: capture-idea
description: Use when the user has a new product idea, feature request or "what if we…", or wants to start the PM pipeline. Step 1 of the pipeline - turns a one-liner into an evidence-graded idea card and checks it against past decisions.
---

# Step 1 · Capture the idea

Turns a loose idea into an idea card the rest of the pipeline can build on. Read
`../../reference/evidence-rules.md` first.

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs capture-idea` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `meeting-notes`, `team-chat` or `support-feedback` · optional · a first look for evidence of the
  problem; without any, the grade rests on what the PM brings
- `product-analytics` · optional · how many users the problem touches
- `docs` · optional · earlier specs and research on the same idea

## Before you start

If `python3 .pm-harness/pm_check.py workspace .` reports context files that are still the
blank template, stop and offer the `setup` skill first (its quick mode asks about eight
questions). An idea card and PRD written on empty context come out generic, and the risk
reviewer has no constraints to check against.

## Steps

1. **Restate** the idea in one sentence, with who it is for and what prompted it, taken from
   the request and any sources the PM pointed to. Ask the PM to confirm or correct it in
   **one** question. Ask a clarifying question only for what the request and sources do not
   already answer.
2. **Name the item** with a short kebab-case slug (`price-alerts`) and create `work/<slug>/`.
   If the folder exists, stop and ask whether to continue that item instead.
   **Next phase of a launched item** (a launch readout said continue): create a new item named
   `<slug>-<phase>` (`price-alerts-mmp`) with `lineage: <slug>` and `phase: <phase>` in its
   front matter. Its evidence is the readout and the previous PRD's *Later* list and open
   questions; its history is the previous item. The previous item stays as it was.
3. **Check history.** Search `decisions/decision-log.md`, `signals/` and other `work/` items
   for the same or a similar idea. If it was rejected or parked before, quote the decision and
   its "revisit if" condition, and check the condition against the workspace before asking.
   - **Condition met:** say so with the evidence and continue.
   - **Condition not met:** say so plainly and recommend one of two routes. **Park** it, with
     the date the condition may be met. Or **continue as a proposal to supersede** the
     decision: the PRD then makes the case (why the decision was made, the risk that remains,
     the cost of waiting, a recommendation and a fallback) and names who must agree, and a
     `Status: proposed` entry goes in the decision log once the PM approves its text.
   - Record the route in the idea card. Later skills build on it rather than raising the same
     decision again, unless something has changed.
4. **Find evidence.** Search the tools for the needs above (the `main` and `also` tools in
   `context/tools.md`: meeting notes, chat, support, analytics) for evidence of the underlying
   problem. Spend a few searches, not an hour; this is a first look. Note any that did not
   answer.
5. **Grade** the evidence `strong`, `some` or `hunch`. A hunch is fine; it is just labelled.
6. **Write** `work/<slug>/01-idea.md` using the format below.

## Output: `work/<slug>/01-idea.md`

```
---
item: <slug>
title: <Title Case name>
stage: idea
owner: <PM name>
created: YYYY-MM-DD
updated: YYYY-MM-DD
evidence: strong | some | hunch
lineage: <previous item, for a next-phase item>   (optional)
phase: <MVP | MMP | MLP | Enhancement>             (optional, settled in the PRD)
---
# <Title>

**One-liner:** <what it lets someone do, for whom>
**Prompted by:** <what triggered the idea>
**Who it is for:** <segment and situation>

## Evidence
- <claim> (<source count and type>) — "<quote>" <source>

## History
<related past decisions or items, or "None found">

## Open questions
- …
```

## Gate

Recommend one option with one line of reasoning (a past decision whose condition is unmet
points to park or supersede, from step 3), then ask the PM which way to go:

- **Continue:** run the `product-grill` skill if the problem is still open (it explores first)
  or the actors, states, scope or trade-offs are fuzzy; otherwise go straight to the `write-prd`
  skill. Offer the `roadmap` skill to place the new item.
- **Size it first** with the `opportunity-brief` skill, or **research it** with the
  `desktop-research` skill.
- **Park it:** log a decision with a "revisit if" condition and set `stage: parked`.
