---
name: write-prd
description: Use when the user wants a PRD, product spec, concept doc, one-pager, problem statement or jobs-to-be-done for an idea. Step 2 of the pipeline - writes an eight-section PRD whose depth follows the phase (MVP, MMP, MLP, Enhancement), checks it, then sends it for independent review.
---

# Step 2 · PRD

The PRD is the *why* and the *what at the level of capabilities*. It must be strong enough that
a sceptical engineer, designer and executive would all agree the problem is real and worth
solving. The exact behaviour comes next, as behaviour trees; the PRD names the tree for each
capability.

Read first: `../../reference/prd-guide.md` (the eight sections), `../../reference/phases.md`,
`../../reference/jtbd.md`, `../../reference/evidence-rules.md`; the item's
`work/<item>/01-idea.md`, `01-grill.md` if it exists, and any research or signals it links;
from the workspace `context/users.md`, `strategy.md`, `metrics.md`, `constraints.md`,
`glossary.md`, `writing-style.md` and `decisions/decision-log.md`.

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs write-prd` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `governed-metrics` or `product-analytics` · optional · baselines for §7; without them a baseline
  is marked *to measure*
- `docs` · optional · related specs and past PRDs to link

If `python3 .pm-harness/pm_check.py workspace .` reports context files that are still the
blank template, stop and offer the `setup` skill (quick mode) before drafting.

## Steps

1. **Settle the phase.** If the PM has not said, recommend `MVP`, `MMP`, `MLP` or
   `Enhancement` with one line of reasoning and ask them to confirm. The phase sets the depth
   of every section (`phases.md`).
2. **Challenge the problem first.** If the actors, states, scope or the problem itself are
   vague, solution-shaped or a hunch, and there is no `01-grill.md`, run the `product-grill`
   skill before drafting. Do not polish a weak problem into a confident document. If the PM
   wants to skip the grill, ask at most three sharp questions instead.
3. **Draft the eight sections** in order, using the template in `prd-guide.md`:
   1. TL;DR · 2. Product shape · 3. Problem and job to be done · 4. Goals and non-goals ·
   5. Requirements · 6. Experience and journey · 7. Success metrics and launch gates ·
   8. Risks, constraints and open questions.
   - **Carry the grill over first.** Walk every line under *Settled*, *Scope and capacity*,
     *Pre-mortem* and *Still open* in `01-grill.md` and put it where its arrow points
     (`→ PRD §5.2`) or in §8.3. Anything agreed there (a test before build, a caveat on the
     evidence, a cut) must appear in the PRD. The checker warns when an arrow points to a
     section the PRD does not have.
   - Write the job statement as *When…, I want to…, so I can…*. Offer a second framing only if
     the grill has not settled the job and the situation could be read differently.
   - **Propose, don't leave blank.** When a decision is missing, write your recommended answer
     marked `Proposed — <owner> to confirm by <date>` and list it in §8.3. Leave a question
     open without a proposal only when no sound default exists, and say why. Never ask the
     PM again about a point the grill settled.
   - In §2, say where it launches and in which languages, and what differs by region.
   - In §5, one subsection per capability with a priority, the rules that shape it, a
     `Seam:` line (where engineering will test it) and a `Tree: functional/<subject>` line
     naming the tree that will hold its behaviour.
   - In §6.3, state the prototype decision: the one trade-off the prototype variants will
     argue about. Take it from `01-grill.md` when the grill settled it.
   - In §7, define each metric with `context/metrics.md` and take baselines from the tool
     trusted for that metric where available, showing the source; mark the rest *to measure*.
     An outside benchmark may justify a target only when labelled external with its URL and
     date (evidence rule 9).
   - In §8, go through every item in `context/constraints.md` and say how the PRD respects it.
     Keep each control a source document requires (a post-mortem recommendation, a compliance
     rule) in its own words, or say `replaces …`, why, and who must agree (evidence rule 10).
   - In §8.2, give a dated path from decision to launch, the last safe date to call it off,
     and the cut order if time runs short.
4. **Cut to the phase.** Remove anything that does not change a decision for this phase. Keep
   within the phase's length guide; one line is enough for a section that barely applies.
   States, edge cases and exact copy belong in the trees, not in §5: §5 says what each
   capability does and the rules that shape it. If the PRD is still more than 1.5 times the
   guide, or has more P0 capabilities than the phase allows, the scope does not fit the phase:
   cut it, or recommend changing the phase (a logged decision). If the PM keeps it as it is,
   add an `Over length: <reason>` line to §2.
5. **Check:** run `python3 .pm-harness/pm_check.py prd work/<item>/02-prd.md`. Fix every error;
   resolve or justify every warning.

## Output

`work/<item>/02-prd.md`, following the template in `prd-guide.md` exactly: the header line, the
eight numbered `##` sections, numbered `###` subsections, and section numbers that stay stable
once reviewed (add `5.4`, never renumber).

## Gate

1. Run the `spec-review` skill on the PRD (independent reviewers in fresh contexts; which
   reviewers depends on the phase).
2. **Put the decisions on one sheet.** Collect every PM decision the findings need into one
   table: the decision, the finding numbers, the options, your recommendation and what it
   changes. The PM accepts or edits the sheet in one pass. This is not the grill: do not ask
   the decisions one at a time, and do not re-ask a point the grill settled unless a finding
   brings new evidence.
3. Revise the PRD to address every **blocking** finding, or record why not. Findings marked
   `→ trees` become tree lines, not PRD text. Add a change-log row for each batch of fixes
   (source: review round and finding numbers), and re-run the check.
4. **Re-review a material revision.** If the revision added a capability, changed §4, §5 or §7
   beyond what the findings asked for, or grew the PRD by more than a third, run `spec-review`
   on the changed sections only, with the reviewers they affect, before asking for approval.
5. Ask the PM to approve. On approval set `stage: prd` and `updated:` in `01-idea.md` and set
   the PRD's status:
   - `pm-approved` while a decision named in §1 still sits with someone else (an exception to
     a past decision, a fee, a regulator's or board's sign-off). Trees can start.
   - `approved` once those decision-makers have agreed; add a change-log row saying who agreed
     and when, and mark any `proposed` decision-log entry `accepted`.

   Offer the `write-behaviour-trees` skill, and the `publish` skill if stakeholders should
   read it in Confluence now.

## After approval: change control

An approved PRD changes only through its change log (`prd-guide.md`):

1. Make the edit and add a row to `## Change log`: date, section, what changed, its source
   (an amendment, a Confluence comment, a meeting, a readout) and who re-reviewed it.
2. If the change touches §4 scope, §5 requirements or §7 metrics and gates, set the status to
   `in review` and run `spec-review` on the changed sections only; it appends a dated round to
   `02-prd-review.md`. Back to `pm-approved` or `approved` once no blocking finding is open.
3. Follow it through: trees first, then the prototype, then tickets if they exist. Re-run
   `python3 .pm-harness/pm_check.py item work/<item>`. If the PRD is on Confluence, republish it.
