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
   - Write the job statement as *When…, I want to…, so I can…*; offer a second framing if the
     situation could be read differently, and let the PM pick.
   - In §5, one subsection per capability with a priority, the rules that shape it and a
     `Tree: functional/<subject>` line naming the tree that will hold its behaviour.
   - In §6.3, state the prototype decision: the one trade-off the prototype variants will
     argue about. Take it from `01-grill.md` when the grill settled it.
   - In §7, define each metric with `context/metrics.md` and take baselines from data where
     available, showing the source.
   - In §8, go through every item in `context/constraints.md` and say how the PRD respects it.
4. **Cut to the phase.** Remove anything that does not change a decision for this phase. Keep
   within the phase's length guide; one line is enough for a section that barely applies.
5. **Check:** run `python3 .pm-harness/pm_check.py prd work/<item>/02-prd.md`. Fix every error;
   resolve or justify every warning.

## Output

`work/<item>/02-prd.md`, following the template in `prd-guide.md` exactly: the header line, the
eight numbered `##` sections, numbered `###` subsections, and section numbers that stay stable
once reviewed (add `5.4`, never renumber).

## Gate

1. Run the `spec-review` skill on the PRD (independent reviewers in fresh contexts; which
   reviewers depends on the phase).
2. Revise the PRD to address every **blocking** finding, or record why not, and re-run the
   check.
3. Ask the PM to approve. On approval set `stage: prd` and `updated:` in `01-idea.md`, set the
   PRD's status to `approved`, and offer the `write-behaviour-trees` skill.
