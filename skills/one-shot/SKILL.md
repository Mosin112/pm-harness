---
name: one-shot
description: Use only when the PM explicitly asks to run the whole PM pipeline, "one-shot" an idea, or go from idea to tickets in one sitting. Runs capture-idea, product-grill (when needed), write-prd with spec-review, write-behaviour-trees, build-prototype with review-prototype, and create-eng-tickets in order, stopping at every approval gate.
disable-model-invocation: true
---

# One-shot pipeline

Runs the five pipeline steps in one session, in order, with the same gates and checks as
running each skill by hand. One-shot means one sitting, not fewer checks. The PM can leave
one-shot at any gate and carry on step by step; the files carry the state either way.

```
Idea → (grill) → PRD → Behaviour trees → Prototype variants → Eng-ready tickets
  1                2          3            4 (+ review loop)          5
```

## Rules

1. **Resume, don't restart.** If `work/<item>/01-idea.md` exists, read its `stage` and continue
   from the next step.
2. **Follow each step's skill exactly,** including its checks. Do not skip a check because the
   session is long.
3. **Respect the phase.** Once the PRD sets `Phase:`, every later step uses its depth from
   `../../reference/phases.md`.
4. **Stop at every gate** and wait for the PM:

   | After | Gate | Check |
   |---|---|---|
   | 1 `capture-idea` | continue, grill, size first, or park | — |
   | `product-grill` (if the idea is fuzzy) | PM ends the grill; phase and prototype decision agreed | — |
   | 2 `write-prd` + `spec-review` | PRD approved; no open blocking findings | `pm_check.py prd` |
   | 3 `write-behaviour-trees` | trees approved | `pm_check.py trees` and `prd` with trees |
   | 4 brief for `build-prototype` | variants and hypotheses approved | — |
   | 4 `build-prototype` + `review-prototype` | variant chosen; no open amendments | `pm_check.py prototype` |
   | 5 `create-eng-tickets` | draft approved before anything is created in the tracker | `pm_check.py tickets` |

5. **Keep the PM oriented.** At each gate show a one-line status:
   `price-alerts · MVP · step 4/5 prototype · 2 variants, 16/16 outcomes, 0 open amendments · waiting for your choice`
6. **Manage context.** After each approved step, write everything needed to the item folder so
   that a new session can resume from files alone. If the conversation is long, suggest
   continuing in a fresh session; the files carry the state.
7. **Budget.** If a step needs evidence that is not available (a connector is down, data access
   is refused), stop at that step, say what is missing, and offer to continue with the gap
   clearly labelled.

## Finish

Summarise: item and phase, files created, checker results, the chosen prototype variant,
ticket keys, open questions and their owners, and the next action (engineering handoff,
stakeholder update, date for the launch readout and its gate). Then offer the `done` skill to
capture what this run taught.
