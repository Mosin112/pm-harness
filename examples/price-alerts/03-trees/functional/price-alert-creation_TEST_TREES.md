Functional: price-alert-creation (src: none; functional: none)
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
