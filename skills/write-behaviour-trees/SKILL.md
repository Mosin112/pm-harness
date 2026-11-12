---
name: write-behaviour-trees
description: Use when the user wants acceptance criteria, requirements, edge cases or behaviour trees for an approved PRD, or wants to turn a PRD into something engineering can test. Step 3 of the pipeline - writes Journey and Functional trees in the strict when/while/if/then grammar and checks them against the grammar and the PRD.
---

# Step 3 · Behaviour trees

Trees are the *what*: the contract between product and engineering. Every line becomes a test
in the engineering harness, so every line must be observable and testable.

Read first: `../../reference/tree-grammar.md`, `../../reference/phases.md`, the approved
(`pm-approved` or `approved`) `work/<item>/02-prd.md` and its review, including every finding
marked `→ trees`, and `context/constraints.md` and `context/glossary.md`.

## Needs

None: works from the workspace files.

## Steps

1. **Take the capabilities from the PRD.** Each `### 5.N` capability names its tree with
   `Tree: functional/<subject>`; write exactly those Functional trees, with those subjects.
   §6.1 names the Journey tree. If a capability seems to need two trees, change the PRD first
   (split the capability) rather than drifting from it.
2. **Scope by phase** (`phases.md`): an MVP covers its P0 capabilities; MMP and MLP cover P0
   and P1, and an MLP adds polish outcomes (exact copy, every state); an Enhancement covers
   the changed branches plus a `then` line for every item on the PRD's **Must not regress** list.
3. **Write one Journey tree per job-to-be-done** in `03-trees/journey/`: the broad happy path
   across capabilities, in the order the user lives it (§6.1). Not exhaustive.
4. **Write one Functional tree per capability** in `03-trees/functional/`: exhaustive at the
   capability's public seam. For every event, walk through:
   - each relevant user or account **state** (`while`): signed in/out, verified/unverified,
     permissions, empty/full, first time/returning
   - each **condition** (`if`): valid/invalid input, limits reached, duplicates, timing
   - **failure** of anything outside the system: network, a third-party service, a timeout
   - every rule in the capability's §5 subsection and every applicable constraint (§8.1)
   - every state listed in §6.2
5. **Make outcomes exact.** Name the message text, the number, the state. Use the glossary's
   terms. Replace untestable words (should, properly, fast…) with something a test can check.
6. **Trace back.** Every rule in §5, every state in §6.2 and every constraint in §8.1 appears in
   at least one tree. List any that do not, and either add lines or say why. Analytics events
   for §7 metrics do **not** go in the trees; `create-eng-tickets` puts them in the analytics
   story, and its check confirms every metric is covered there.
7. **Check both ways:**
   - `python3 .pm-harness/pm_check.py trees work/<item>/03-trees` (grammar, testability)
   - `python3 .pm-harness/pm_check.py prd work/<item>/02-prd.md work/<item>/03-trees` (every
     tree the PRD names exists, and every Functional tree belongs to a capability)

   Fix every error. Resolve or justify every warning.
8. **Review:** for anything beyond a small Enhancement, run the `spec-review` skill on the
   trees, focusing on missing branches. Its findings go to `03-trees-review.md`.

## Output

```
work/<item>/03-trees/
  journey/<job-subject>_TEST_TREES.md
  functional/<capability-subject>_TEST_TREES.md
```

## Gate: review the trees as a diagram

1. **Make the view:** `python3 .pm-harness/pm_check.py view work/<item>` writes
   `work/<item>/03-trees-view.html`: every tree drawn left to right (event → state →
   condition → outcome), with the PRD section, seam, and later the prototype screen and ticket
   for each outcome, and a flag on anything hard to test.
2. **Show it to the PM** in the same session:
   - **Claude app or claude.ai:** publish it as an artifact (`publish` skill, "Trees view") and
     open it. The PM clicks **Comment** on any line and chooses **Send to Claude**. Where this
     session is notified of such comments it picks them up at once; where it is not (Claude's
     cloud sessions, for now), the PM says "check my comments" and you read the artifact's
     comment threads.
   - **Any other tool:** open the file in a browser. The PM clicks **Comment** on any line,
     adds notes, then **Copy for Claude** and pastes them into the chat.
3. **For each comment,** change the tree file (never the view), and the PRD first if the
   comment changes a requirement (change control in `write-prd`). Re-run both checks above,
   regenerate the view, republish to the same artifact, and reply on the thread (or in chat)
   saying what changed. Resolve the thread once the PM is satisfied.
4. Highlight the branches most likely to be argued about and ask for approval. On approval set
   `stage: trees` in `01-idea.md` and offer the `build-prototype` skill.
