# Prototype craft

Rules for how a prototype looks and behaves. `build-prototype` reads this before building any
screen and again before the design review. Adapted from
[Impeccable](https://github.com/pbakaus/impeccable) by Paul Bakaus (Apache-2.0): its craft floor,
Operate mode and review playbooks, condensed for prototypes built from behaviour trees.

## 1. Design source

- **`DESIGN.md` is normative.** Its tokens (colours, type, radii, spacing, components) are the
  product's design system; use them as CSS custom properties in the product screens and do not
  invent alternatives. Its prose (Do's and Don'ts, named rules) is binding too.
- If `DESIGN.md` is still the blank template, use a restrained neutral system, say so in the
  brief, and mark every choice as provisional. Never promote prototype choices into `DESIGN.md`.
- The side panel (variants, scenarios, coverage, review note) is harness chrome. It keeps its own
  style and is out of scope for these rules and for the design review.

## 2. Mode: Operate

App screens are where people complete a task, so the bar is *earned familiarity*: a fluent user
trusts the screen at once and never pauses at a subtly odd component.

- Standard affordances and platform patterns. Same button shape, control vocabulary and icon
  style on every screen.
- One type family is usually right. A fixed rem scale with a 1.125–1.2 step; display faces never
  in labels, buttons or data.
- Restrained colour: the accent marks the primary action, the current selection and state, not
  decoration. A full semantic set: hover, focus, active, disabled, selected, loading, error,
  warning, success.
- Motion only conveys state (feedback, loading, reveal), 150–250 ms, never a load sequence.
- Inline or progressive before modal; a modal only when the task needs interruption.

## 3. Variants

Variants differ in their **hypothesis**, not their decoration. They share one design system, and
the difference shows on the screens the decision is about. A variant that differs only in colour
or radius tests nothing.

## 4. Craft floor: check on the rendered screens

- **Contrast:** body and placeholder text at least 4.5:1, large text 3:1; secondary text on a
  coloured surface is tinted from that surface, never plain grey.
- **States:** every interactive element has default, hover, focus, active and disabled; every
  screen that loads or fails has loading, error and empty states (they are tree branches too).
- **Copy:** the exact words from the trees. Controls name their action; errors say what went
  wrong and how to recover.
- **Spacing and type:** tight groups, generous separation, more space above a heading than below;
  body measure 65–75 characters; numbers in tabular figures where they line up.
- **Keyboard and screen:** visible focus everywhere; works at phone width without sideways scroll.
- **Browser surfaces:** focus rings, selection colour and numerals follow the palette, not
  browser defaults.

## 5. Harden

Run the real content through each screen, using the PRD's markets and languages (§2):

- very long and very short text, large numbers and amounts, many items, no items;
- offline, slow and failed requests, permission errors (each should be a tree branch);
- translations about 30% longer, right-to-left layout for Arabic or Hebrew markets, local date,
  number and currency formats.

## 6. Refuse: the tells of generated design

Reach for one of these only when `DESIGN.md` or the brief asks for it:

- emoji or Unicode symbols standing in for icons (draw them: inline SVG, one stroke weight);
- gradient text; glass and blur as decoration;
- identical icon-heading-text cards as the page structure; cards nested in cards;
- a coloured left or right border thicker than 1px on cards, list items or alerts;
- a hero-metric block (big number, small label, supporting stats) where content belongs;
- a small label or "eyebrow" above a heading;
- monospace as a "technical" costume instead of for code, data or measurement;
- grey text on coloured backgrounds; decorative motion; a modal as the first idea.

## 7. Design review, before the PM walkthrough

For each variant in play, review the screens on the decision path, then the unhappy paths:

1. **Heuristics:** score Nielsen's ten heuristics 0–4 (visibility of status, match with the real
   world, user control, consistency, error prevention, recognition over recall, flexibility,
   minimalism, error recovery, help). Note the two weakest.
2. **Cognitive load:** count choices per screen, things the user must remember between screens,
   and jargon; flag any screen that asks for more than one decision at a time.
3. **Craft floor and refuse list:** go through sections 4–6.
4. **Rank findings** P0 (blocks the task or access) to P3 (polish). Fix every P0 and P1 before
   the walkthrough; list the rest.

Write the result to `04-prototype/design-review.md`: per variant, the heuristic scores, what was
fixed and what remains. Keep it short; it is evidence for the walkthrough, not a report.
