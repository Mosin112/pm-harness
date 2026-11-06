Journey: set-and-receive-price-alert (src: none; journey: none)
  when a verified investor sets a price alert from an asset page
    then the price alert appears as active in the investor's alerts list
  when the asset's price reaches the price alert's target
    then the investor receives a push notification naming the asset and the target price
    and the price alert is shown as triggered in the alerts list
  when the investor taps the price alert notification
    then the asset page opens
