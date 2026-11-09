---
name: roadmap
description: Use when the PM wants to build, update, reprioritise or present the product roadmap, asks "what's now, next and later", needs to fit a new item in, or has to move dates after a slip. Keeps a Now / Next / Later roadmap in sync with the items in work/, their evidence and stages, and records every reprioritisation as a decision.
---

# Roadmap

The roadmap is a view over the workspace, not a separate plan: every row is an item in `work/`
(or a parked idea), placed by its evidence, stage and fit with strategy. Moves are decisions, so
they are logged. Structure adapted from Anthropic's product-management plugin (Apache-2.0).

Read first: `roadmap.md` (if it exists), every `work/*/01-idea.md` (stage, phase, evidence,
opportunity scores, lineage), each item's PRD §7 gate and §8.2 dependencies, `context/strategy.md`
(themes, bets, what is explicitly not a priority), `decisions/decision-log.md`, and the tracker
(the `issue-tracker` tool in `context/tools.md`) for epics' status and dates.

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs roadmap` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `issue-tracker` · optional · epics' status and dates; without it, dates come from the PM

## What to do

Ask which operation, if the PM has not said:

- **Build** a roadmap from scratch: timeframe (quarter, half), themes from `strategy.md`.
- **Add** an item: where it fits, and what moves to make room.
- **Reprioritise:** what changed (evidence, strategy, a launch readout, capacity).
- **Move** an item: why (scope, a dependency slip, people), and what it pushes downstream.
- **Status:** refresh from the tracker and the items' stages.

## Placing items

| Column | What belongs there |
|---|---|
| **Now** | Items being specified or built: stage `prd` to `building`, with a team committed |
| **Next** | Items with at least *some* evidence and a sizing (`opportunity-brief`), at stage `idea` or `prd`, plus next phases a launch readout said to continue |
| **Later** | Hunches, items waiting on a dependency, and parked ideas with their "revisit if" condition |

- Order within a column by the RICE inputs in each idea card; show the inputs, not just the score.
  If an item has no sizing, say so rather than guessing one.
- Group by strategy theme. An item that serves no current theme is flagged, not hidden.
- Ask the PM (or engineering) for capacity before filling **Now**. More in **Now** than the
  team can carry is a finding to show, not a layout to draw.
- Dates only on **Now** and only from the tracker or the PM; **Later** never has dates.
- Status comes from evidence: `on track`, `at risk` (with the risk), `blocked` (with the blocker
  and its owner), `done`.

## Output: `roadmap.md` (workspace root)

```
# Roadmap · <team> · updated YYYY-MM-DD
Capacity: <who, how much> · Strategy themes: <from strategy.md>

## Now
| Item | Phase · stage | Outcome (PRD §7) | Gate / date | Status | Depends on |
## Next
| Item | Evidence | RICE inputs | Why next |
## Later
| Item | Why later | Revisit if |

## Changes since last update
- <item>: <moved from → to>, because <reason> (decision log YYYY-MM-DD)
```

Link each item to its folder (`work/<item>/`) and, once published, its Confluence PRD.

## Every move is a decision

For each add, reprioritisation or move, propose a decision-log entry (what moved, why, the
alternatives, revisit if), and apply it only on approval. Show a before / after of any column
that changed.

## Sharing

Offer a version for the audience in `context/stakeholders.md` (executives see themes, outcomes
and risks; engineering sees dependencies and dates). Publishing to Confluence follows the
`publish` skill's approval rule; never post without the PM approving the exact page.
`python3 .pm-harness/pm_check.py workspace .` warns about any active item missing from the
roadmap.
