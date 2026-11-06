---
name: build-prototype
description: Use when the user wants a prototype, mockup, clickable demo or "something to show" for an item with approved behaviour trees. Step 4 of the one-shot pipeline - builds a self-contained clickable HTML prototype where every tree branch can be demonstrated, and proves that coverage with the checker.
---

# Step 4 · Clickable prototype

The prototype lets stakeholders *feel* the behaviour trees before engineering starts. It is a
demonstration of the contract, not a design spec: it must show every branch, including errors
and edge cases, not just the happy path.

Read first: the approved trees in `work/<item>/03-trees/`, the concept, `context/product.md`
and `context/writing-style.md`. Use `../../examples/price-alerts/04-prototype/index.html`
(relative to this skill) as the reference implementation of the structure below.

## Requirements

1. **One self-contained file:** `work/<item>/04-prototype/index.html`. Inline all CSS and JS.
   No build step, no external requests except optional web fonts, so it can be opened from
   disk, attached to a ticket or published as a link.
2. **Screens:** each distinct state is an element with `data-screen="<id>"`. Only one is visible
   at a time. Navigation happens through the prototype's own buttons, like the real product.
3. **Scenario controls:** a side panel, clearly separated from the product UI, with toggles for
   every `while` state and `if` condition in the trees (verified/unverified, limit reached,
   notifications off, simulate a price move…). Changing a toggle must change what the product
   UI does, so every branch is reachable.
4. **Coverage map:** a `<script type="application/json" id="tree-coverage">` block that maps
   every `then` and `and` line of every tree to the screen that demonstrates it:

   ```json
   {
     "trees": {
       "functional/price-alert-creation": [
         { "line": "then the alert is saved as active", "screen": "alerts" },
         { "line": "and the alert's direction is set to above or below the current price", "screen": "alerts" }
       ],
       "functional/price-alert-trigger": [
         { "line": "then no further notification is sent", "screen": null, "reason": "Not visible: absence of a notification" }
       ]
     }
   }
   ```

   `screen: null` is allowed only with a `reason` (backend-only or "nothing happens" outcomes).
5. **Visible coverage panel:** render the coverage map in the side panel as a checklist of tree
   lines; clicking a line jumps to its screen with the right scenario set. This is what makes
   the prototype a review tool.
6. **Realistic copy:** use the exact messages from the trees. Mark sample data as sample data.
7. **Brand:** follow any design tokens in `context/product.md`; otherwise use a neutral,
   accessible style. Works at phone width. Keyboard focus visible.

## Check

Run `python3 .pm-harness/pm_check.py prototype work/<item>/03-trees work/<item>/04-prototype/index.html`.
It fails if any tree line is missing from the coverage map or points at a screen that does not
exist. Fix until it passes.

## Gate

Walk the PM through the Journey tree in the prototype, then any branch they choose. Collect
feedback. **If feedback changes behaviour, update the trees first**, re-run the tree check, then
update the prototype. When the PM approves, set `stage: prototype` in `01-idea.md` and offer
`/pm-harness:create-eng-tickets`. If the PM's team uses Figma for final design, say which
screens a designer should take forward.
