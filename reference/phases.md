# Phases: how much depth each step needs

Every item has one **phase**, set in the PRD header (`Phase: MVP`). The phase decides how much
each step has to cover, so an MVP stays lean and an enhancement only describes what changes.
Pick the phase with the PM before writing the PRD; recommend one and say why.

| Phase | Use it when | The question it answers |
|---|---|---|
| `MVP` | The job or the solution is still unproven | Is this worth building properly? |
| `MMP` | The MVP worked; now it has to be good enough to roll out and market | Can we launch this to everyone? |
| `MLP` | The capability exists; the goal is that users love it | Will people choose it and tell others? |
| `Enhancement` | Changing something already shipped | What changes, and what must not break? |

## Depth by step

| Step | MVP | MMP | MLP | Enhancement |
|---|---|---|---|---|
| PRD length (guide) | ~2 pages, ≤ 1,200 words | ~3 pages, ≤ 1,800 words | ~3 pages, ≤ 1,800 words | ~1.5 pages, ≤ 900 words |
| §3 Problem and job | Full job statement, forces, evidence | Same, plus market and competitor context | Same, plus the emotional side of the job | What changed since launch: usage data, complaints, requests |
| §5 Requirements | P0 only; P1 goes to §4 Later | P0 and P1 | P0 and P1, each with polish criteria | The change only, plus a **Must not regress** list |
| §6 Experience | One core journey, key error states | Core plus supporting journeys | Emotional moments, exact copy, accessibility | Changed steps only |
| §7 Metrics and gates | 1 primary metric, 1 guardrail, a continue / stop gate | Plus a **launch gate** for each rollout stage | Plus a quality gate (satisfaction, polish) | Before / after on the changed metric |
| Trees | P0 capabilities | All P0 and P1 capabilities | Plus polish outcomes (exact copy, every state) | Changed branches, plus `then` lines for behaviour that must not regress |
| Prototype | 2 variants | 2 variants, supporting journeys included | 2–3 variants at high fidelity | 1 variant is fine: the change against today |
| Review | All five reviewers | All five | All five; design findings on polish count as blocking | Engineering, design and risk; exec and customer advocate if the change is visible |
| Definition of done | Team DoD | Plus rollout and monitoring items | Plus polish acceptance by the PM and designer | Plus regression tests for every must-not-regress line |

## Rules

1. **Cut, don't pad.** If a section does not change a decision for this phase, keep it to one
   line ("Not needed for an MVP: …"). Never fill a section to make the document look complete.
2. **Changing phase is a decision.** Moving an item from MVP to MMP is logged in
   `decisions/decision-log.md` with the evidence that justified it.
3. **Later is a list, not a graveyard.** Everything pushed out of scope for this phase goes to
   §4 *Later*, so the next phase starts from it.
