# Price alerts · Concept
Status: approved · Owner: Example PM · Updated: 2026-11-03 · Evidence: some

> Worked example with illustrative sample data.

## Problem
Investors who are waiting for a specific price have no way to be told when it arrives. They
either watch the chart, use a separate alerts app, or miss the moment. Watching is tiring and
anxious; switching apps means they often act late or not at all.

## Job to be done
> **When** I'm waiting for an asset to reach a price I've decided on, **I want to** be told the
> moment it gets there, **so I can** act on my plan without watching the chart all day.

## Forces
| Push | Pull | Anxiety | Habit |
|---|---|---|---|
| Watching the chart all day; missing moves while busy | Peace of mind: "the app will tell me" | Too many notifications; an alert that fires late or wrongly | Keeping the app open; a separate alerts app that already works |

## Today's alternatives
Checking the app repeatedly · third-party alert apps · exchange-wide price notifications that
are not personal · doing nothing and missing the move.

## Proposed solution
1. **Set an alert** from any asset page: choose a target price; the direction (above or below
   the current price) is set automatically.
2. **Get notified** once, by push notification, when the price reaches the target.
3. **Act from the notification:** tapping it opens the asset page.
4. **Manage alerts** in an alerts list showing active and triggered alerts.

New: alert creation, trigger service, alerts list. Existing: asset pages, push notifications,
verification flow.

## Success metrics
| Metric | Definition | Baseline | Target | Source |
|---|---|---|---|---|
| **Alert adoption** (primary) | % of weekly active investors with at least one active alert | 0% | 15% after 8 weeks | sample |
| Alert-to-action | % of triggered alerts followed by opening the asset within 1 hour | n/a | 40% | sample |
| Guardrail: notification opt-out rate | % of investors disabling push in a week | 0.8% | no increase | sample |

## Scope
**In:** price alerts on any listed asset; one notification per alert; up to 20 active alerts.
**Not now:** percentage-move alerts, recurring alerts, placing an order from the notification.
**Later:** alerts that suggest setting a limit order (needs separate risk review).

## Risks and constraints
- **Wording must not read as advice.** Notifications state facts ("Bitcoin reached $60,000"),
  never "time to buy". (constraint: brand and wording)
- **Verification:** only verified users can set alerts. (constraint: regulatory)
- **Notification fatigue:** capped at 20 active alerts and one notification per alert.
- **Price-feed latency** could make alerts feel late. Engineering to confirm the feed.

## Open questions
| Question | Owner |
|---|---|
| Which price feed defines "reached"? | Engineering lead |
| Do alerts need an expiry date? | PM, after launch readout |

## Behaviour trees
- `03-trees/journey/set-and-receive-price-alert_TEST_TREES.md`: the full job, end to end
- `03-trees/functional/price-alert-creation_TEST_TREES.md`: setting an alert, every branch
- `03-trees/functional/price-alert-trigger_TEST_TREES.md`: firing and notifying, every branch
