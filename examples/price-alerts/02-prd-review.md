# Price alerts · Review (2026-11-03)
Reviewers: engineering, design, risk, exec, customer advocate (independent subagents)

> Worked example.

| # | Severity | Reviewer | Section | Finding | Suggested change | Resolution |
|---|---|---|---|---|---|---|
| 1 | blocking | risk | §5.2 | Draft notification text "Bitcoin hit your target, buy now?" reads as advice. | State the fact only: asset and price. | changed |
| 2 | blocking | engineering | §5.2 | No rule for an alert whose target is crossed again after it fires; could notify repeatedly. | One notification per alert; triggered alerts don't re-arm. | changed |
| 3 | important | design | §6.2 | No message when the target equals the current price. | Reject with "Choose a price different from the current price". | changed |
| 4 | important | customer advocate | §5.2 | Users with push turned off would never learn an alert fired. | Show triggered alerts in the list regardless of push. | changed |
| 5 | important | exec | §7 | Primary metric didn't say what "adoption" means. | Define as % of weekly active investors with an active alert. | changed |
| 6 | important | engineering | §5.1 | Unlimited alerts per user is an abuse and cost risk. | Cap at 20 active alerts. | changed |
| 7 | important | exec | §2 | Phase unclear: the draft read like a full rollout on *some* evidence. | Make it an MVP with a continue / stop gate. | changed |
| 8 | nit | design | §6.1 | "Alert" vs "price alert" used inconsistently. | Use "price alert" in UI copy. | changed |

All blocking findings resolved. PRD approved 2026-11-03.

## Round 2 (2026-11-04)
Reviewers: design, exec · Scope: §4 only (change log row 1, from prototype amendment A1)

| # | Severity | Reviewer | Section | Finding | Suggested change | Resolution |
|---|---|---|---|---|---|---|

No findings. The PRD stays approved.
