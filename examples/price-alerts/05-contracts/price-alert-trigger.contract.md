Contract: price-alert-trigger (seam: the price-alert service, observed through push notifications and the Price alerts list)

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

Non-goals: Percentage-move alerts and recurring alerts; Placing an order from the notification
Source: PM Harness item price-alerts, 03-trees/functional/price-alert-trigger_TEST_TREES.md, PRD §5.2
