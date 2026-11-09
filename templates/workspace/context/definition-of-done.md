# Definition of done
Every engineering story meets this list before it is closed. `create-eng-tickets` copies it into
the tickets and adds the items for the item's phase. Edit it to match how your team works.

## Every story
- [ ] Every acceptance-criteria line has a passing automated test, and the tree's coverage labels are updated from `none`
- [ ] Copy matches the trees and the chosen prototype variant exactly
- [ ] Analytics events for the story fire and are visible in the analytics tool
- [ ] Works at phone width, with keyboard and screen-reader access and checked contrast
- [ ] Every error and empty state in the trees is handled
- [ ] Constraints in PRD §8.1 confirmed by their owner (risk, compliance, legal)
- [ ] Released behind a feature flag, with monitoring on the guardrail metric
- [ ] Support notes updated if the change is visible to customers
- [ ] PM accepted it in staging against the Journey tree

## Added by phase
- **MMP:** a rollout plan for each launch gate, and a dashboard for every gate metric
- **MLP:** polish accepted by the PM and the designer on a real device
- **Enhancement:** a regression test for every must-not-regress line
