# PRD guide: eight sections, nothing more

The PRD is the *why* and the *what at the level of capabilities*. The exact behaviour lives in
the behaviour trees; the PRD names which tree covers each capability. Eight fixed sections keep
every PRD comparable and checkable. How deep each section goes depends on the phase
(`phases.md`).

Check a PRD with `python3 .pm-harness/pm_check.py prd work/<item>/02-prd.md` (add the trees
folder once trees exist to check the links both ways).

## Template

```
# <Title> · PRD
Phase: MVP · Status: draft · Owner: <PM> · Updated: YYYY-MM-DD · Evidence: some

## 1. TL;DR
## 2. Product shape
## 3. Problem and job to be done
### 3.1 Problem
### 3.2 Job to be done
### 3.3 Forces and today's alternatives
### 3.4 Evidence and why now
## 4. Goals and non-goals
## 5. Requirements
### 5.1 <Capability> (P0)
Tree: functional/<capability-subject>
## 6. Experience and journey
### 6.1 Core journey
### 6.2 States to design
### 6.3 Prototype decision
## 7. Success metrics and launch gates
## 8. Risks, constraints and open questions
```

Header values: `Phase` is `MVP`, `MMP`, `MLP` or `Enhancement`. `Status` is `draft`,
`in review` or `approved`. `Evidence` is the grade from the idea card.

## Sections

### 1. TL;DR
Three to five bullets a busy reader can act on: the problem, who has it, what will be built,
how success is measured, and what is being asked of the reader. Not a mini-PRD.

### 2. Product shape
A short table: phase and why this phase now; lineage (new, extends, replaces or depends on
another item); entry points (where users start); platforms. Then **Assumptions to test**, the
two or three beliefs that would change the plan if wrong.

### 3. Problem and job to be done
- **3.1 Problem:** what is hard today, for whom, in their terms. No solution words.
- **3.2 Job to be done:** *When…, I want to…, so I can…* (see `jtbd.md`).
- **3.3 Forces and today's alternatives:** push, pull, anxiety, habit; what people hire today,
  including doing nothing.
- **3.4 Evidence and why now:** source counts and grade (`evidence-rules.md`), links to
  `signals/` and research files, and why this matters this quarter.

### 4. Goals and non-goals
- **Goals:** two to four, each tied to the job's outcome, not to shipping the feature.
- **Non-goals:** concrete temptations this phase will not take on ("recurring alerts"), not
  boilerplate ("we won't boil the ocean").
- **Later:** what the next phase should pick up.

### 5. Requirements
One subsection per **capability**, numbered `5.1`, `5.2`… with a priority in the heading:
`P0` (must have for this phase), `P1` (should have), `P2` (could have; usually belongs in
*Later*). Each subsection:

- one line on what the capability lets the user do;
- the rules that shape it, in plain language (limits, eligibility, timing, wording rules);
- `Tree: functional/<subject>`: the Functional tree that will hold its exact behaviour. One
  capability, one tree. The subject is kebab-case and becomes the tree's file name.

For an `Enhancement`, add a **Must not regress** list: existing behaviour that has to keep
working. Each item becomes a `then` line in a tree and a regression test.

Requirements state *what*, not screens or implementation. Section numbers stay stable once the
PRD is reviewed: add `5.4`, never renumber, because trees, prototype notes and amendments cite
them.

### 6. Experience and journey
- **6.1 Core journey:** the user's path, as numbered steps, from entry point to job done.
  End with `Tree: journey/<subject>`.
- **6.2 States to design:** empty, loading, error, first-time, limit reached, permission denied,
  offline: whichever apply.
- **6.3 Prototype decision:** the one design question the prototype variants will argue about,
  naming both sides and the tension: *"set an alert in one step (speed) versus seeing exactly
  what will be sent (confidence)"*. Usually settled in `product-grill`. List the variants to
  try, one hypothesis each. For an `Enhancement` with one variant, say what it is compared
  against.

### 7. Success metrics and launch gates
| Metric | Definition | Baseline | Target | Source |

One primary metric tied to the job's outcome, one or two guardrails, defined using
`context/metrics.md`. Then the gate for this phase: **continue / stop** for an MVP; a
**launch gate** per rollout stage for MMP and MLP (what must be true to go from 5% to 50%, say).

### 8. Risks, constraints and open questions
- **8.1 Constraints:** each item in `context/constraints.md` that applies, and how the PRD
  respects it.
- **8.2 Risks and dependencies:** product, technical, adoption and third-party risks; other
  teams or systems this depends on. If AI is part of the behaviour, add its failure modes and
  guardrails here.
- **8.3 Open questions:** | Question | Owner | Due |. Every question has an owner.

## Writing rules
- Lead with what to do, then why. Short sentences. Tables for anything with more than two
  attributes.
- Use the canonical terms in `context/glossary.md`; one name per concept.
- Respect accepted decisions in `decisions/decision-log.md`. If the PRD changes one, say so.
- Every number names its source (`evidence-rules.md`, rule 5).
- Avoid "easy", "simple", "quickly", "seamless": say what the user sees.
