# Behaviour tree grammar

Behaviour trees are the contract between product and engineering. A PM writes them; an
engineering harness turns each line into a test. The format is deliberately strict so a
machine can check it and a person can read it aloud.

## Files

- One tree per file, named `<test-subject>_TEST_TREES.md`, where the subject is lowercase
  kebab-case (`price-alert-creation_TEST_TREES.md`).
- Product work lives under `work/<item>/03-trees/journey/` and `work/<item>/03-trees/functional/`.
- At handoff, `pm_check.py contracts work/<item>` turns each tree into an engineering-harness
  contract (`05-contracts/<subject>.contract.md`, first line `Contract: <subject> (seam: …)`,
  the same clause lines). Engineering copies those into the repository's `contracts/` folder.
- `pm_check.py view work/<item>` draws the trees as a diagram for review
  (`03-trees-view.html`).

## First line

```
<Kind>: <test-subject> (<coverage>)
```

- `Kind` is `Functional` or `Journey` for product work (`Integration` and `Unit` belong to
  engineering).
- `test-subject` repeats the file name's subject unchanged.
- `coverage` lists where the behaviour is implemented and tested, in the canonical order
  `src`, `functional`, `journey`, `integration`, `unit`, separated by `; `. Use `none` for
  coverage that is expected but does not exist yet. Product trees normally start as
  `(src: none; functional: none)` or `(src: none; journey: none)`.

## Requirement lines

One clause per line, indented two spaces per level, nested by causation. Every line starts
with one of five words:

| Word | Means | Example |
|---|---|---|
| `when` | an event or action that starts the behaviour | `when a user submits a price alert` |
| `while` | a state that holds during the event | `while the user is verified` |
| `if` | a condition that splits the outcome | `if the target price is zero or below` |
| `then` | an observable outcome (always a leaf) | `then the alert is rejected with the reason "Enter a price above zero"` |
| `and` | a further outcome of the same branch (a leaf, after `then`) | `and the alert is marked as triggered` |

Rules:

1. Top-level lines (two spaces) start with `when`.
2. `then` and `and` lines are leaves: nothing nests under them.
3. An `and` line follows a `then` or `and` line at the same depth.
4. Every branch ends in at least one `then`.
5. Outcomes are observable by the person or system on the other side of the seam: what
   the user sees, receives or can do, or what another system receives. Never internal
   implementation ("the cache is updated").
6. Outcomes are testable. Avoid words a test cannot check: *should, properly, correctly,
   appropriately, fast, easily, user-friendly, etc.* Name the number, the message, the state.

## Journey vs Functional

- **Journey**: one broad, production-like path through the user's lifecycle across
  capabilities. Not exhaustive. Write one per job-to-be-done.
- **Functional**: exhaustive behaviour of one capability at its public seam: every
  observable branch, including failure and edge cases. Every user-visible behaviour needs
  Functional coverage; a Journey never replaces it.

## Example

```
Functional: price-alert-creation (src: none; functional: none)
  when a user submits a price alert
    while the user is verified
      if the target price is above zero and differs from the current price
        then the alert is saved as active
      if the target price is zero or below
        then the alert is rejected with the reason "Enter a price above zero"
    while the user is unverified
      then the user is asked to complete verification before setting alerts
```

Check any tree with `python3 .pm-harness/pm_check.py trees <folder>`.
