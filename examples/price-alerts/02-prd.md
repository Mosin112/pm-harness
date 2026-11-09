# Price alerts · PRD
Phase: MVP · Status: approved · Owner: Example PM · Updated: 2026-11-03 · Evidence: some

> Worked example with illustrative sample data.

## 1. TL;DR
- Investors waiting for a price watch the chart all day or use a separate alerts app, and
  often act late or not at all (6 calls, 23 support tickets).
- Build price alerts: set a target from any asset page, get one push notification when it is
  reached, see active and triggered alerts in one list.
- MVP for verified investors only, capped at 20 active price alerts.
- Success: 15% of weekly active investors with an active price alert after 8 weeks, with no
  rise in push opt-outs.
- Ask: engineering to confirm which price feed defines "reached".

## 2. Product shape
| | |
|---|---|
| Phase | MVP: the evidence is *some*; first learn whether alerts turn watching into acting |
| Lineage | New capability. Uses existing asset pages, push notifications and verification |
| Entry points | **Set price alert** on every asset page; the **Price alerts** list |
| Platforms | iOS and Android app |
| Markets and languages | Every market where the app trades; the app's existing languages. No regional differences |

**Assumptions to test**
- Investors act when an alert fires (alert-to-action of 40% or more).
- One notification per alert is enough; repeat alerts are not requested in the first 8 weeks.

## 3. Problem and job to be done
### 3.1 Problem
Investors who are waiting for a specific price have no way to be told when it arrives. They
watch the chart, use a separate alerts app, or miss the moment. Watching is tiring; switching
apps means acting late.

### 3.2 Job to be done
> **When** I'm waiting for an asset to reach a price I've decided on, **I want to** be told the
> moment it gets there, **so I can** act on my plan without watching the chart all day.

### 3.3 Forces and today's alternatives
| Push | Pull | Anxiety | Habit |
|---|---|---|---|
| Watching the chart all day; missing moves while busy | "The app will tell me" | Too many notifications; an alert that fires late or reads like advice | Keeping the app open; a separate alerts app that already works |

Alternatives: checking the app repeatedly · third-party alert apps · market-wide price
notifications that are not personal · doing nothing and missing the move.

### 3.4 Evidence and why now
- Requests to be told when a price is reached: 6 customer calls and 23 support tickets over
  8 weeks, e.g. "I keep the app open all day just to catch the dip." Grade: **some**.
- Sessions that view an asset page five or more times without trading: 18,000 investors a
  month (sample figure).
- Why now: requests rose in a volatile month, and this quarter's goal is more active investors.

## 4. Goals and non-goals
**Goals**
1. Investors hear about the price they are waiting for without watching the chart.
2. Learn whether alerts lead to action, to decide on the next phase.

**Non-goals**
- Percentage-move alerts and recurring alerts.
- Placing an order from the notification.

**Later**
- Alerts that suggest a limit order (needs its own risk review).
- An expiry date for alerts (decide after the launch readout).
- Deleting price alerts from the list (prototype review, A1).

## 5. Requirements
### 5.1 Set a price alert (P0)
From any asset page, a verified investor sets a target price; the direction (above or below
the current price) is set automatically and the alert is listed as active.
- Only verified investors can set price alerts (constraint: regulatory).
- The target must be above zero and different from the current price.
- Up to 20 active price alerts per investor.

Seam: the app's asset page and Price alerts list
Tree: functional/price-alert-creation

### 5.2 Trigger and notify (P0)
When the price reaches a target in its direction, the investor gets one push notification and
the alert moves to triggered in the list.
- The notification states the fact only: "<Asset> reached <target price>" (constraint: wording).
- One notification per alert; a triggered alert does not re-arm.
- With push turned off, the alert still shows as triggered in the list.

Seam: the price-alert service, observed through push notifications and the Price alerts list
Tree: functional/price-alert-trigger

## 6. Experience and journey
### 6.1 Core journey
1. On an asset page the investor taps **Set price alert**.
2. They enter a target; the app shows whether it is above or below today's price.
3. The alert appears as active in **Price alerts**.
4. When the price reaches the target, a push notification arrives.
5. Tapping it opens the asset page; the alert shows as triggered.

Seam: end to end, on a test build with a simulated price feed
Tree: journey/set-and-receive-price-alert

### 6.2 States to design
Unverified investor · target zero or below · target equal to the current price · 20 active
alerts · push turned off · no alerts yet · nothing triggered yet.

### 6.3 Prototype decision
Setting an alert in one quick step (**speed**) versus seeing exactly what will be sent before
saving (**confidence** that it is a fact, not advice, and fires once).
- **Quick set:** one field in a sheet. Hypothesis: fewer steps means more alerts set.
- **Guided set:** preset targets and a preview of the notification. Hypothesis: seeing the
  exact message builds the trust that leads to action.

**Chosen at the prototype gate (2026-11-04):** Guided set. Reviewers trusted the preview, and
the extra step cost little.

## 7. Success metrics and launch gates
| Metric | Definition | Baseline | Target | Source |
|---|---|---|---|---|
| **Alert adoption** (primary) | % of weekly active investors with at least one active price alert | 0% | 15% after 8 weeks | sample |
| Alert-to-action | % of triggered alerts followed by opening the asset within 1 hour | n/a | 40% | sample |
| Guardrail: notification opt-out | % of investors turning off push in a week | 0.8% | no increase | sample |

**Gate (continue / stop):** after 8 weeks, move to an MMP (more alert types) if alert adoption
is 10% or more and alert-to-action is 30% or more with no guardrail breach. Otherwise stop and
record why in the launch readout.

## 8. Risks, constraints and open questions
### 8.1 Constraints
- **Wording:** notifications state facts, never "time to buy" (§5.2).
- **Regulatory:** only verified investors can set price alerts (§5.1).

### 8.2 Risks and dependencies
- Notification fatigue: capped at 20 active alerts and one notification per alert.
- Price-feed latency could make alerts feel late; depends on the market data service.

### 8.3 Open questions
| Question | Owner | Due |
|---|---|---|
| Which price feed defines "reached"? | Engineering lead | Before build |
| Do alerts need an expiry date? | Example PM | Launch readout |

## Change log
| Date | Section | Change | Source | Re-reviewed by |
|---|---|---|---|---|
| 2026-11-04 | §4 | Added "Deleting price alerts from the list" to Later | Prototype amendment A1 | Design, exec (§4 only): no findings |
