---
item: price-alerts
title: Price alerts
stage: tickets
owner: Example PM
created: 2026-11-02
updated: 2026-11-04
evidence: some
---
# Price alerts

> **Worked example.** This item was produced with the PM Harness to show each pipeline step.
> The feature, the evidence counts and the quotes are illustrative sample data, not real
> customer data.

**One-liner:** Let investors set a price alert on any asset so they hear about the move
without watching the chart.
**Prompted by:** Recurring requests in support and in customer calls during a volatile month.
**Who it is for:** Active retail investors waiting to buy or sell at a specific price.

## Evidence
- Investors ask to be told when a price is reached (6 customer calls, 23 support tickets
  over 8 weeks), e.g. "I keep the app open all day just to catch the dip."
- Investors check prices many times a day without trading (product analytics: sessions that
  view an asset page without a trade; sample figure for the example).
- Some investors use a separate alerts app and then switch to us to trade (3 calls).

Evidence grade: **some**. Several sources and one behavioural signal, but no test yet of
whether alerts lead to action.

## History
No related decision in the decision log. A "watchlist notifications" idea was discussed
informally last year but never specified.

## Opportunity
| Input | Value | Source |
|---|---|---|
| Reach | 18,000 investors / month view an asset 5+ times without trading | sample figure |
| Impact | 1 (medium) | assumption: alerts convert some watching into acting |
| Confidence | 80% | evidence grade: some, two source types agree |
| Effort | 3 person-weeks | engineering estimate (sample) |
| **RICE** | **4,800** | |

Strategy fit: supports the engagement goal (more active investors, fewer idle sessions).

## Open questions
- Should a triggered alert re-arm automatically? (decided in concept: no)
- Which price feed decides that a target was "reached"? (engineering)
