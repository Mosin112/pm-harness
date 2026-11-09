# Price alerts · Prototype amendments

> Worked example. Review notes from the prototype walkthrough on 2026-11-04, walked with
> `review-prototype`. Each note is pinned to a variant and screen; open it with
> `index.html#variant=<variant>&screen=<screen>&demo=<demo>`.

## A1 · The 20-alert cap gives the investor no way out
- Status: resolved
- Variant: guided
- Screen: set-alert
- Demo: err-full
- Tree line: then the price alert is rejected with the message "You can have up to 20 active price alerts"
- From: Design reviewer · 2026-11-04
- Note: An investor at the cap is told no, but cannot remove an old alert to make room.
- Class: later
- Section: §4
- Resolution: Deleting price alerts added to PRD §4 Later. Few investors are expected to reach 20 in the MVP; revisit at the launch readout.

## A2 · Preset chips might read as advice to buy
- Status: dismissed
- Variant: guided
- Screen: set-alert
- From: Risk reviewer · 2026-11-04
- Note: "−5%" next to the asset could look like a suggestion to buy the dip.
- Class: dismiss
- Resolution: Risk confirmed presets are neutral input shortcuts, not advice, provided the line "It states the price only; it is not advice." stays under the form. No change.
