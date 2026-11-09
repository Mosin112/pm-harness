---
name: build-prototype
description: Use when the user wants a prototype, mockup, clickable demo, design options or "something to show" for an item with approved behaviour trees. Step 4 of the pipeline - builds one self-contained clickable HTML file with two or three hypothesis-led design variants, where every tree branch can be demonstrated in every variant, and proves that coverage with the checker.
---

# Step 4 · Clickable prototype with variants

The prototype lets stakeholders *feel* the behaviour trees before engineering starts, and it
settles the PRD's prototype decision by putting two designs side by side. It must show every
branch, including errors and edge cases, in every variant, not just the happy path.

Read first: the approved trees in `work/<item>/03-trees/`, the PRD (especially §5, §6.2 and
§6.3), `../../reference/phases.md`, `context/product.md` and `context/writing-style.md`. Start
from the shell `../../templates/prototype/index.html`; the worked example
`../../examples/price-alerts/04-prototype/index.html` shows a finished prototype built on it.

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

Copy the shell to `work/<item>/04-prototype/index.html`. It already has the phone frame, the side
panel and the **PM Harness runtime** (`<script id="pm-runtime">`), which runs the variant
switcher, deep links, the coverage panel and review notes. Leave the runtime exactly as it is,
so every prototype behaves the same and the checker can rely on it. You write four things:

1. **Screens,** inside `.phone`: each distinct state is an element with `data-screen="<id>"`;
   one is visible at a time and navigation happens through the product's own buttons. A screen
   that differs by variant is written once per variant with the **same id** plus
   `data-variant="<id>"`; shared screens have no `data-variant`. Same id means switching
   variants keeps the reviewer on the equivalent screen.
2. **Variants manifest** (`<script type="application/json" id="prototype-variants">`): the
   decision, and for each variant an `id`, `label`, `hypothesis` and `tradeOffs`. Ids are short
   kebab-case words; avoid `settings`, `sidebar`, `customize`, `upgrade` and `downloads`, which
   claude.ai links reserve.
3. **Coverage map** (`<script type="application/json" id="tree-coverage">`): every `then` and
   `and` line of every tree, mapped to the screen that demonstrates it and a `demo` that puts
   the prototype into that state:
   ```json
   { "trees": { "functional/price-alert-creation": [
       { "line": "then the price alert is saved as active", "screen": "alerts", "demo": "create-ok" } ] } }
   ```
   `screen: null` is allowed only with a `reason` (backend-only or "nothing happens" outcomes).
   The screen must exist in **every** variant.
4. **Product code,** in the last `<script>`: scenario toggles in the side panel for every
   `while` state and `if` condition in the trees (changing one must change what the product
   does), and one call to `PMH.start({start, reset, render, demos})` with the starting screen,
   a reset, a render function that fills a screen from state, and one demo per coverage line.
   Navigate with `PMH.show(id)`, write to the event log with `PMH.log(text)`, find a part of a
   variant's screen with `PMH.part(screen, class)`, and call `PMH.userAction()` when a
   scenario control changes.

Rules: use the exact messages from the trees in every variant, and mark sample data. Follow any
design tokens in `context/product.md`; otherwise a neutral, accessible style. Works at phone
width; keyboard focus visible. Deep links look like `index.html#guided--set-alert--err-full`
(variant, screen, demo): plain names, so they also work in a Claude artifact link.

## 3. Check

Run `python3 .pm-harness/pm_check.py prototype work/<item>/03-trees work/<item>/04-prototype/index.html`.
It fails if the variants manifest is incomplete, a tree line is missing from the coverage map,
a screen is missing from a variant still in play, the PRD and manifest disagree about the chosen
variant, or an amendment is malformed or still open. Then open the
file in a browser and click through every coverage line in every variant; the checker proves
structure, not that the design works.

## 4. Gate: walkthrough, review notes, choice

1. Walk the PM through the Journey tree in each variant, then any branch they choose.
2. Record every piece of feedback in `work/<item>/04-prototype/amendments.md`: the PM's,
   artifact comments sent to Claude, notes copied from the review card, and prototype feedback
   from meetings. Then run the `review-prototype` skill to classify and resolve each one. **If
   feedback changes behaviour, the PRD and trees change first.**
3. Ask the PM to choose: **one variant**, a **merge** (named parts of each, recorded as
   amendments and rebuilt into one variant), or **both as an experiment** (PRD §7 gets an
   Experiment block, and the tickets include the experiment flag and analytics). Record the
   choice and the reason under PRD §6.3 (`**Chosen at the prototype gate (date):** …`), and in
   the decision log if it is durable.
4. **Archive the others.** Set `"chosen": "<variant id>"` in the manifest. The other variants
   stay viewable, labelled archived, but are no longer checked or maintained: from now on only
   the chosen variant must demonstrate every outcome, and review notes apply to it. (For an
   experiment, leave `chosen` out so both stay complete.)
5. The prototype is approved only when the check passes with no open amendments. Then set
   `stage: prototype` in `01-idea.md` and offer the `create-eng-tickets` skill. If the team
   uses Figma for final design, say which screens of the chosen variant a designer should take
   forward.

**Sharing it:** stakeholders can click through it as a Claude artifact (`publish` skill,
"Prototype"), where **Comment on this screen** sends their notes to Claude; or open the file
from disk, where the review-note card copies an amendment to paste in.
