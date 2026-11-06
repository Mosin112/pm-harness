# Price alerts · Engineering tickets

> Worked example. Drafted by `create-eng-tickets`, checked with
> `pm_check.py tickets`, approved by the PM, then created in the tracker. Ticket keys are
> placeholders.

## Epic PA-0 · Price alerts
**Job:** When I'm waiting for an asset to reach a price I've decided on, I want to be told the
moment it gets there, so I can act on my plan without watching the chart all day.
**Links:** concept `02-concept.md` · trees `03-trees/` · prototype `04-prototype/index.html`
**Success metrics:** alert adoption (primary), alert-to-action, notification opt-out rate
(guardrail). Events in PA-4.

---

## PA-1 · Set a price alert
**Goal:** A verified investor can set a price alert on any asset, with clear errors when they can't.
**Tree:** `functional/price-alert-creation_TEST_TREES.md`
**Prototype screens:** set-alert, alerts, verify

**Acceptance criteria**
```
when an investor submits a price alert for an asset
  while the investor is verified
    if the target price is above zero and differs from the current price
      then the price alert is saved as active
      and the direction is set to "above" when the target is higher than the current price, otherwise "below"
    if the target price is zero or below
      then the price alert is rejected with the message "Enter a price above zero"
    if the target price equals the current price
      then the price alert is rejected with the message "Choose a price different from the current price"
    if the investor already has 20 active price alerts
      then the price alert is rejected with the message "You can have up to 20 active price alerts"
  while the investor is unverified
    then the investor is asked to complete verification before setting price alerts
```
**Out of scope:** percentage-move alerts, recurring alerts.

## PA-2 · Trigger price alerts and notify
**Goal:** When a target is reached, the investor hears about it once, and the alert's state is clear.
**Tree:** `functional/price-alert-trigger_TEST_TREES.md`
**Prototype screens:** lock, alerts (plus System events for "no notification" outcomes)

**Acceptance criteria**
```
when a new price is received for an asset
  while an active price alert's target has been reached in its direction
    if the investor has push notifications enabled
      then one push notification is sent with the text "<Asset> reached <target price>"
      and the price alert is marked as triggered
    if the investor has push notifications disabled
      then no push notification is sent
      and the price alert is marked as triggered
  while no active price alert's target has been reached
    then no push notification is sent
when the price crosses a triggered price alert's target again
  then no further notification is sent for that price alert
```
**Notes:** notification copy states facts only (risk review finding 1). Engineering to confirm
which price feed defines "reached".

## PA-3 · End-to-end journey test
**Goal:** The whole job works in a production-like environment.
**Tree:** `journey/set-and-receive-price-alert_TEST_TREES.md`

**Acceptance criteria**
```
when a verified investor sets a price alert from an asset page
  then the price alert appears as active in the investor's alerts list
when the asset's price reaches the price alert's target
  then the investor receives a push notification naming the asset and the target price
  and the price alert is shown as triggered in the alerts list
when the investor taps the price alert notification
  then the asset page opens
```

## PA-4 · Analytics for success metrics
**Goal:** We can measure the concept's success metrics from launch day.
- [ ] Event `price_alert_created` (asset, direction) for alert adoption
- [ ] Event `price_alert_triggered` (asset, push_sent) for alert-to-action
- [ ] Event `price_alert_notification_opened` (asset, minutes_since_trigger) for alert-to-action
- [ ] Dashboard tile for weekly notification opt-out rate (guardrail)

---

## Definition of ready (all stories)
- [x] Behaviour trees approved by the PM (2026-11-04)
- [x] Prototype reviewed; every tree outcome demonstrated (`pm_check.py prototype` passes)
- [x] Risk review blocking findings resolved
- [ ] Price feed confirmed (owner: engineering lead)

## Handoff
Copy `03-trees/journey/` and `03-trees/functional/` into the service repository's
`test-trees/journey/` and `test-trees/functional/`. The engineering harness implements each
line test-first and updates the coverage labels from `none` as tests and code land.
