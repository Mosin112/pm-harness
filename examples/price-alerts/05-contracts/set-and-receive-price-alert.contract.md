Contract: set-and-receive-price-alert (seam: end to end, on a test build with a simulated price feed)

when a verified investor sets a price alert from an asset page
  then the price alert appears as active in the investor's alerts list
when the asset's price reaches the price alert's target
  then the investor receives a push notification naming the asset and the target price
  and the price alert is shown as triggered in the alerts list
when the investor taps the price alert notification
  then the asset page opens

Non-goals: Percentage-move alerts and recurring alerts; Placing an order from the notification
Source: PM Harness item price-alerts, 03-trees/journey/set-and-receive-price-alert_TEST_TREES.md, PRD §6.1
