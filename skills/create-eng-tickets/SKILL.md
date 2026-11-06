---
name: create-eng-tickets
description: Use only when the PM explicitly asks to create engineering tickets, an epic or Jira stories for an item with an approved prototype. Step 5 of the one-shot pipeline - drafts tickets whose acceptance criteria are the behaviour tree lines, checks traceability, and creates them in the tracker only after approval.
disable-model-invocation: true
---

# Step 5 · Engineering-ready tickets

Tickets carry the contract to engineering unchanged. Acceptance criteria are the tree lines
themselves, so nothing is lost or reworded between product and test.

Read first: `work/<item>/02-concept.md`, every tree in `work/<item>/03-trees/`, the prototype
and `context/tools.md` (which tracker and project to use).

## Steps

1. **Draft the epic:** title, the job statement, link to the concept, prototype and trees,
   success metrics and their events.
2. **Draft one story per Functional tree** (split a very large tree by its top-level `when`).
   Each story contains:
   - **Goal:** one line in user terms
   - **Acceptance criteria:** the tree's lines copied *verbatim*, in a fenced block, with the
     tree file path
   - **Prototype:** the screens that demonstrate it
   - **Out of scope:** from the concept's non-goals
3. **Draft one story for the Journey tree(s)** as the end-to-end acceptance test.
4. **Draft one analytics story** listing the events needed to measure each success metric.
5. **Definition of ready** for each story: trees approved, prototype linked, open questions
   resolved or owned, dependencies named.
6. **Check traceability:** write the draft to `work/<item>/05-tickets.md` and run
   `python3 .pm-harness/pm_check.py tickets work/<item>/03-trees work/<item>/05-tickets.md`.
   It fails if a tree outcome is missing from every ticket, or a ticket contains a `then`/`and`
   line that is not in a tree (an invented requirement). Fix until it passes.
7. **Show the PM the full draft and ask for approval** to create the tickets.
8. **Only after approval,** create the epic and stories with the tracker connector, attaching
   or linking the trees and prototype. Record the created ticket keys in `05-tickets.md`.
   If creation partly fails, report exactly which tickets exist and which do not.

## Handoff to engineering

Tell the PM how engineering picks this up: copy `03-trees/journey/` and `03-trees/functional/`
into the repository's `test-trees/` folders, where an engineering harness can implement them
test-first. Set `stage: tickets` in `01-idea.md`, log the decision to build in
`decisions/decision-log.md`, and offer `/pm-harness:stakeholder-update`.
