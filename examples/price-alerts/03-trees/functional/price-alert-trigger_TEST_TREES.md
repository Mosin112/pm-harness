Functional: price-alert-trigger (src: none; functional: none)
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
