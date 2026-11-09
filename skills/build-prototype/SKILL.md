---
name: build-prototype
description: Use when the user wants a prototype, mockup, clickable demo, design options or "something to show" for an item with approved behaviour trees. Step 4 of the pipeline - builds one self-contained clickable HTML file with two or three hypothesis-led design variants, where every tree branch can be demonstrated in every variant, and proves that coverage with the checker.
---

# Step 4 · Clickable prototype with variants

The prototype lets stakeholders *feel* the behaviour trees before engineering starts, and it
settles the PRD's prototype decision by putting two designs side by side. It must show every
branch, including errors and edge cases, in every variant, not just the happy path.

Read first: the approved trees in `work/<item>/03-trees/`, the PRD (especially §5, §6.2 and
§6.3), `../../reference/phases.md`, `context/product.md` and `context/writing-style.md`. Use
`../../examples/price-alerts/04-prototype/index.html` as the reference implementation of the
structure below.

## 1. Brief gate

Before building, show the PM a five-line brief and wait for approval:

- **Decision:** the trade-off from PRD §6.3, both sides named.
- **Variants:** two by default, each with a one-line **hypothesis** and its **trade-offs**. A
  third only when it tests a genuinely different hypothesis, never a cosmetic one. An
  `Enhancement` may use one variant (the change) with a `singleReason` saying what it is
  compared against.
- **Screens:** the screens each variant needs; which are shared and which differ.
- **Scenarios:** every `while` state and `if` condition from the trees that the scenario
  controls will switch.
- **Fidelity:** by phase (`phases.md`); MLP prototypes use the real design tokens and copy.

## 2. Build: `work/<item>/04-prototype/index.html`

1. **One self-contained file.** Inline all CSS and JS. No build step, no external requests
   except optional web fonts, so it opens from disk, attaches to a ticket or publishes as a
   link.
2. **Variants manifest:**
   ```html
   <script type="application/json" id="prototype-variants">
   { "decision": "…", "source": "02-prd.md §6.3",
     "variants": [ { "id": "quick", "label": "Quick set", "hypothesis": "…", "tradeOffs": ["…"] },
                   { "id": "guided", "label": "Guided set", "hypothesis": "…", "tradeOffs": ["…"] } ] }
   </script>
   ```
3. **Screens:** each distinct state is an element with `data-screen="<id>"`; one is visible
   at a time and navigation happens through the product's own buttons. A screen that differs
   by variant is written once per variant with the **same id** plus `data-variant="<id>"`;
   shared screens have no `data-variant`. Same id means switching variants keeps the reviewer
   on the equivalent screen.
4. **Scenario controls:** a side panel, clearly separated from the product UI, with toggles for
   every `while` state and `if` condition in the trees. Changing a toggle must change what the
   product does, so every branch is reachable in every variant.
5. **Variant switcher:** in the side panel, show the decision and each variant's hypothesis and
   trade-offs; switching keeps the current screen. Offer a link that opens the other variant in
   a new tab for side-by-side comparison.
6. **Coverage map:** a `<script type="application/json" id="tree-coverage">` block mapping every
   `then` and `and` line of every tree to the screen that demonstrates it, with a `demo` name
   that puts the prototype into that state:
   ```json
   { "trees": { "functional/price-alert-creation": [
       { "line": "then the price alert is saved as active", "screen": "alerts", "demo": "create-ok" } ] } }
   ```
   `screen: null` is allowed only with a `reason` (backend-only or "nothing happens" outcomes).
   The screen must exist in **every** variant.
7. **Visible coverage panel:** render the map as a checklist of tree lines; clicking a line runs
   its demo in the current variant.
8. **Deep links:** read and keep the URL hash in step, as
   `#variant=<id>&screen=<id>&demo=<demo>`, so any state can be shared and reopened.
9. **Review note:** a panel card where a reviewer types a note and copies it as an amendment
   pinned to the current variant, screen, demo and last tree line clicked (the format in
   `review-prototype`).
10. **Realistic copy:** use the exact messages from the trees in every variant. Mark sample data.
11. **Brand and access:** follow any design tokens in `context/product.md`; otherwise a neutral,
    accessible style. Works at phone width; keyboard focus visible.

## 3. Check

Run `python3 .pm-harness/pm_check.py prototype work/<item>/03-trees work/<item>/04-prototype/index.html`.
It fails if the variants manifest is incomplete, a tree line is missing from the coverage map,
a screen is missing from any variant, or an amendment is malformed or still open. Then open the
file in a browser and click through every coverage line in every variant; the checker proves
structure, not that the design works.

## 4. Gate: walkthrough, review notes, choice

1. Walk the PM through the Journey tree in each variant, then any branch they choose.
2. Record every piece of feedback, from the PM or from stakeholders who used the review-note
   card, in `work/<item>/04-prototype/amendments.md`, then run the `review-prototype` skill to
   classify and resolve each one. **If feedback changes behaviour, the trees change first.**
3. Ask the PM to choose: **one variant**, a **merge** (named parts of each, recorded as
   amendments and rebuilt), or **both as an experiment** (the tickets then include the
   experiment flag and analytics). Record the choice and the reason under PRD §6.3
   (`**Chosen at the prototype gate (date):** …`), and in the decision log if it is durable.
4. The prototype is approved only when the check passes with no open amendments. Then set
   `stage: prototype` in `01-idea.md` and offer the `create-eng-tickets` skill. If the team
   uses Figma for final design, say which screens of the chosen variant a designer should take
   forward.
