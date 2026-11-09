---
name: review-prototype
description: Use when a prototype has review notes or amendments to work through, when stakeholders have sent feedback on a prototype, or when asked to close the loop between prototype review and the PRD and trees. Walks each open amendment on its pinned screen, classifies it, proposes the change to the PRD or trees, and resolves it once the PM decides.
---

# Prototype review loop

Close the loop from prototype feedback back into the requirements. The amendments file is the
audit trail: every piece of feedback ends up as a PRD change, a tree change, a prototype fix, a
*Later* item, or a reasoned dismissal. Nothing is resolved silently.

Read first: `work/<item>/04-prototype/amendments.md`, the prototype's `prototype-variants` and
`tree-coverage` blocks, the PRD and the trees.

## Amendment format

Feedback arrives from the walkthrough, from the prototype's review-note card, or pasted from
chat or meeting notes. Write each one into `amendments.md`, numbered `A1`, `A2`… in the order
received:

```
## A3 · <short title>
- Status: open
- Variant: guided
- Screen: set-alert
- Demo: err-full                       (optional: the scenario it was seen in)
- Tree line: then the price alert is…  (optional: the exact tree line it concerns)
- From: <name> · YYYY-MM-DD
- Note: <the feedback, in the reviewer's words>
- Class: <set when classified>
- Section: <PRD section affected, e.g. §5.1>
- Resolution: <set when resolved or dismissed>
```

## The walk

For each open amendment, oldest first:

1. **Open it where it was seen:** `index.html#variant=<variant>&screen=<screen>&demo=<demo>`.
   Look at the screen; do not judge from memory.
2. **Judge it** against the tree line, the PRD section and the variant's hypothesis.
3. **Classify it:**

   | Class | When | What changes |
   |---|---|---|
   | `prd change` | A requirement is wrong, missing or ambiguous | PRD §5 (or §4, §6) first, then the trees, then the prototype |
   | `tree change` | New or different behaviour under an existing requirement | The trees, then the prototype |
   | `polish` | Presentation only; no behaviour changes | The prototype |
   | `later` | Valid, but outside this phase | PRD §4 *Later* |
   | `dismiss` | Already satisfied, out of scope, or withdrawn | Nothing; the reason is recorded |

4. **Present the classification with evidence** (quote the tree line or PRD section) and the
   exact proposed change. Wait for the PM's decision.

## Apply and close

After the PM decides:

1. Apply the change in order: PRD → trees → prototype. Keep PRD section numbers stable (add,
   never renumber).
2. Re-run the checks that the change touches:
   - `pm_check.py prd work/<item>/02-prd.md work/<item>/03-trees`
   - `pm_check.py trees work/<item>/03-trees`
   - `pm_check.py prototype work/<item>/03-trees work/<item>/04-prototype/index.html`
3. Set the amendment's `Class`, `Section` and `Resolution`, and its `Status` to `resolved`
   (or `dismissed` for class `dismiss`). An amendment stays `open` until its change has landed
   and the checks pass.
4. Summarise: resolved, dismissed, still open, and which files changed.

The prototype cannot be approved while any amendment is open; the prototype check enforces it.
If tickets already exist, a `prd change` or `tree change` also needs the tickets updated and
re-checked with `pm_check.py tickets`.
