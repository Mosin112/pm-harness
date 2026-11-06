---
name: write-behaviour-trees
description: Use when the user wants acceptance criteria, requirements, edge cases or behaviour trees for an approved concept, or wants to turn a concept into something engineering can test. Step 3 of the one-shot pipeline - writes Journey and Functional trees in the strict when/while/if/then grammar and checks them.
---

# Step 3 · Behaviour trees

Trees are the *what*: the contract between product and engineering. Every line becomes a test
in the engineering harness, so every line must be observable and testable.

Read first: `../../reference/tree-grammar.md`, the approved `work/<item>/02-concept.md` and its
review, and `context/constraints.md`.

## Steps

1. **Find the capabilities.** List each capability in the concept's proposed solution. Each
   becomes one Functional tree. Name each with a kebab-case test subject
   (`price-alert-creation`).
2. **Write one Journey tree per job-to-be-done** in `03-trees/journey/`: the broad happy path
   across capabilities, in the order the user lives it. Not exhaustive.
3. **Write one Functional tree per capability** in `03-trees/functional/`: exhaustive at the
   capability's public seam. For every event, walk through:
   - each relevant user or account **state** (`while`): signed in/out, verified/unverified,
     permissions, empty/full, first time/returning
   - each **condition** (`if`): valid/invalid input, limits reached, duplicates, timing
   - **failure** of anything outside the system: network, a third-party service, a timeout
   - every **constraint** from `context/constraints.md` that applies
4. **Make outcomes exact.** Name the message text, the number, the state. Replace untestable
   words (should, properly, fast…) with something a test can check.
5. **Trace back.** Every job outcome, success metric event and constraint in the concept must
   appear in at least one tree. List any that do not and either add lines or note why.
6. **Check:** run `python3 .pm-harness/pm_check.py trees work/<item>/03-trees`. Fix every
   error. Resolve or justify every warning.
7. **Review:** for non-trivial items, run `/pm-harness:spec-review` on the trees, focusing on
   missing branches.

## Output

```
work/<item>/03-trees/
  journey/<job-subject>_TEST_TREES.md
  functional/<capability>_TEST_TREES.md
```

Add a short `## Behaviour trees` section to `02-concept.md` listing each tree file and what it
covers.

## Gate

Show the PM every tree in full and ask for approval, highlighting the branches most likely to
be argued about. On approval set `stage: trees` in `01-idea.md` and offer
`/pm-harness:build-prototype`.
