# Price alerts · Review (2026-11-03)
Reviewers: engineering, design, risk, exec, customer advocate (independent subagents)

> Worked example.

| # | Severity | Reviewer | Finding | Suggested change | Resolution |
|---|---|---|---|---|---|
| 1 | blocking | risk | Draft notification text "Bitcoin hit your target, buy now?" reads as advice. | State the fact only: asset and price. | changed |
| 2 | blocking | engineering | No rule for an alert whose target is crossed again after it fires; could notify repeatedly. | One notification per alert; triggered alerts don't re-arm. | changed |
| 3 | important | design | No message when the target equals the current price. | Reject with "Choose a price different from the current price". | changed |
| 4 | important | customer advocate | Users with push turned off would never learn an alert fired. | Show triggered alerts in the alerts list regardless of push. | changed |
| 5 | important | exec | Primary metric didn't say what "adoption" means. | Define as % of weekly active investors with an active alert. | changed |
| 6 | important | engineering | Unlimited alerts per user is an abuse and cost risk. | Cap at 20 active alerts. | changed |
| 7 | nit | design | "Alert" vs "price alert" used inconsistently. | Use "price alert" in UI copy. | changed |

All blocking findings resolved. Concept approved 2026-11-03.
