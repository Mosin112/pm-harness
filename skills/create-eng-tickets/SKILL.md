---
name: create-eng-tickets
description: Use only when the PM explicitly asks to create engineering tickets, an epic or Jira stories for an item with an approved prototype. Step 5 of the pipeline - drafts tickets whose acceptance criteria are the behaviour tree lines, adds the Definition of done, checks traceability, and creates them in the tracker only after approval.
disable-model-invocation: true
---

# Step 5 · Engineering-ready tickets

Tickets carry the contract to engineering unchanged. Acceptance criteria are the tree lines
themselves, so nothing is lost or reworded between product and test. The Definition of done
says what "finished" means for every story.

Read first: `work/<item>/02-prd.md` (phase, §6.3 chosen variant, §7 metrics, §8 constraints),
every tree in `work/<item>/03-trees/`, the prototype and its `amendments.md`,
`context/definition-of-done.md`, `../../reference/phases.md` and `context/tools.md` (which
tracker and project to use).

Before starting, confirm the prototype check passes with no open amendments. If it does not,
stop and offer the `review-prototype` skill.

## Steps

1. **Draft the epic:** title, phase, the job statement, links to the PRD, prototype (with the
   chosen variant) and trees, success metrics and their events, and the phase's gate from §7.
2. **Draft one story per Functional tree** (split a very large tree by its top-level `when`).
   Each story contains:
   - **Goal:** one line in user terms, citing its PRD section (§5.1)
   - **Acceptance criteria:** the tree's lines copied *verbatim*, in a fenced block, with the
     tree file path
   - **Prototype:** the screens of the chosen variant that demonstrate it, as deep links
     (`index.html#guided--set-alert`, or the published artifact URL with the same `#…`)
   - **Out of scope:** from the PRD's non-goals
3. **Draft one story for the Journey tree(s)** as the end-to-end acceptance test.
4. **Draft one analytics story** listing the events needed to measure each success metric and
   gate, naming the metric each event serves (`for alert adoption`). Analytics lives here, not
   in the trees. If the PM chose to ship two variants as an experiment, add the experiment flag,
   assignment and the comparison metric here.
5. **Definition of ready** for all stories: trees approved, prototype approved with no open
   amendments, open questions resolved or owned, dependencies named.
6. **Definition of done** for all stories: copy `context/definition-of-done.md` (every item
   under *Every story*), then add the items for this phase. Add story-specific items only
   where a story needs more (a migration, a third-party sign-off).
7. **Check traceability:** write the draft to `work/<item>/05-tickets.md` and run
   `python3 .pm-harness/pm_check.py tickets work/<item>/03-trees work/<item>/05-tickets.md work/<item>/02-prd.md`.
   It fails if a tree outcome is missing from every ticket, a ticket contains a `then`/`and`
   line that is not in a tree (an invented requirement), a PRD §7 metric is not named in the
   analytics story, or there is no Definition of done with at least three items. Fix until it
   passes, then run `python3 .pm-harness/pm_check.py item work/<item>` for the whole item.
8. **Show the PM the full draft and ask for approval** to create the tickets.
9. **Only after approval,** create the epic and stories with the tracker connector, attaching
   or linking the trees and prototype. Record the created ticket keys in `05-tickets.md`.
   If creation partly fails, report exactly which tickets exist and which do not.

## Handoff to engineering

1. Run `python3 .pm-harness/pm_check.py contracts work/<item>`. It writes one contract per tree
   to `work/<item>/05-contracts/<subject>.contract.md` in the engineering harness's format:
   `Contract: <subject> (seam: <PRD Seam line>)`, the tree's lines unchanged, the PRD's
   non-goals and the source. If it warns that a capability has no `Seam:`, confirm the seam with
   the engineering lead and add it to the PRD (change control) before handing over.
2. Tell the PM how engineering picks this up: copy `05-contracts/` into the service
   repository's `contracts/` folder; the engineering harness implements each clause
   test-first and keeps code, tests and contracts in sync. Link the contracts from the epic.
3. Set `stage: tickets` in `01-idea.md`, log the decision to build in
   `decisions/decision-log.md`, and offer the `stakeholder-update` skill.
