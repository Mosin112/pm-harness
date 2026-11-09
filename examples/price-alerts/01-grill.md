# Price alerts · Grill (2026-11-02)
**Phase:** MVP. Evidence is *some* (calls and tickets, no behavioural test yet), so learn
whether alerts lead to action before building more alert types.
**Prototype decision:** setting an alert in one quick step (speed) versus seeing exactly what
will be sent before saving (confidence that it is a fact, not advice, and fires once).

> Worked example.

## Settled
- The actor is a **verified investor**; unverified investors are asked to verify first (→ PRD §5.1).
- An alert fires **once**; a triggered alert does not re-arm (→ PRD §5.2).
- Notification copy states the fact only, never a suggestion to trade (→ PRD §5.2, §8.1).
- Percentage-move and recurring alerts are out of the MVP (→ PRD §4).
- Cap of 20 active alerts per investor (→ PRD §5.1).

## Still open
| Question | Owner |
|---|---|
| Which price feed defines "reached"? | Engineering lead |

## Glossary and decisions
- Added to the glossary: **price alert** (a one-time notification when an asset reaches a
  target price). Avoid: "alert", "watch".
- Decision log: none. The single-notification rule lives in the PRD.
