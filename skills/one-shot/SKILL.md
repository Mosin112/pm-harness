---
name: one-shot
description: Use only when the PM explicitly asks to run the whole PM pipeline, "one-shot" an idea, or go from idea to tickets in one sitting. Orchestrates capture-idea, write-concept, spec-review, write-behaviour-trees, build-prototype and create-eng-tickets in order, pausing at every approval gate.
disable-model-invocation: true
---

# One-shot pipeline

Runs the five pipeline steps in one session, in order, with the same gates as running them
one by one. One-shot means one sitting, not no checks.

```
Idea → Concept + JTBD → Behaviour trees → Prototype → Eng-ready tickets
  1          2         (review)    3            4              5
```

## Rules

1. **Resume, don't restart.** If `work/<item>/01-idea.md` exists, read its `stage` and continue
   from the next step.
2. **Follow each step's skill exactly,** including its checks. Do not skip a check because the
   session is long.
3. **Stop at every gate** and wait for the PM:
   - after step 1: continue, size first, or park
   - after step 2 + review: approve the concept (no open blocking findings)
   - after step 3: approve the trees
   - after step 4: approve the prototype
   - before step 5 creates anything in the tracker
4. **Keep the PM oriented.** At each gate show a one-line status:
   `price-alerts · step 3/5 trees · 3 trees, 21 outcomes, checker passed · waiting for approval`
5. **Manage context.** After each approved step, write everything needed to the item folder so
   that a new session can resume from files alone. If the conversation is long, suggest
   continuing in a fresh session; the files carry the state.
6. **Budget.** If a step needs evidence that is not available (a connector is down, data access
   is refused), stop at that step, say what is missing, and offer to continue with the gap
   clearly labelled.

## Finish

Summarise: item, files created, checker results, ticket keys, open questions and their owners,
and the next action (engineering handoff, stakeholder update, date for the launch readout).
Then offer `/pm-harness:update-context` to capture what was learned.
