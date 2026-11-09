---
name: capture-idea
description: Use when the user has a new product idea, feature request or "what if we…", or wants to start the PM pipeline. Step 1 of the pipeline - turns a one-liner into an evidence-graded idea card and checks it against past decisions.
---

# Step 1 · Capture the idea

Turns a loose idea into an idea card the rest of the pipeline can build on. Read
`../../reference/evidence-rules.md` first.

## Steps

1. **Restate** the idea in one sentence and ask the PM to confirm or correct it. Ask at most
   two clarifying questions: who it is for, and what prompted it.
2. **Name the item** with a short kebab-case slug (`price-alerts`) and create `work/<slug>/`.
   If the folder exists, stop and ask whether to continue that item instead.
   **Next phase of a launched item** (a launch readout said continue): create a new item named
   `<slug>-<phase>` (`price-alerts-mmp`) with `lineage: <slug>` and `phase: <phase>` in its
   front matter. Its evidence is the readout and the previous PRD's *Later* list and open
   questions; its history is the previous item. The previous item stays as it was.
3. **Check history.** Search `decisions/decision-log.md`, `signals/` and other `work/` items
   for the same or a similar idea. If it was rejected or parked before, quote the decision and
   its "revisit if" condition, and ask whether that condition is now met.
4. **Find evidence.** Search the sources in `context/tools.md` (meeting notes, chat, support,
   analytics) for evidence of the underlying problem. Spend a few searches, not an hour; this
   is a first look.
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

Ask the PM which way to go:

- **Continue:** run the `product-grill` skill if the actors, states, scope or trade-offs are
  still fuzzy, otherwise go straight to the `write-prd` skill.
- **Size it first** with the `opportunity-brief` skill, or **research it** with the
  `desktop-research` skill.
- **Park it:** log a decision with a "revisit if" condition and set `stage: parked`.
