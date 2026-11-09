---
name: synthesize-signals
description: Use when the user wants to know what customers are saying, synthesise interviews, meeting transcripts, support tickets, chat threads or feedback, or asks "what are the top problems/themes". Produces evidence-counted themes with real quotes and candidate ideas.
---

# Synthesise signals

Turns scattered evidence into themes a PM can act on, without overstating what the evidence
supports. Read `../../reference/evidence-rules.md` (relative to this skill) before starting.

## Inputs

Ask for the scope if it is not given: **time window**, **sources** and **topic** (or "anything").
Use the connectors listed in `context/tools.md`. Typical sources:

- Meeting notes and transcripts (customer calls, sales calls, user interviews)
- Team chat channels where customer feedback is shared
- Support tickets or feedback tools
- Product analytics for behavioural evidence (drop-offs, unused features)
- Files the PM attaches

## Steps

1. **Gather.** Pull every source in scope. Record what you read: source type, date, count.
   If a source fails or access is refused, note it and continue.
2. **Extract.** For each source, pull out pains, requests, workarounds and moments of delight,
   each with a verbatim quote and its source reference.
3. **Cluster** extracts into themes. A theme is a problem or job, not a feature request:
   "can't tell when a price target is hit" rather than "wants alerts".
4. **Count and grade.** For each theme: number of independent sources by type, segments
   affected, evidence grade (`strong`, `some`, `hunch`), and any behavioural data that
   confirms or contradicts it.
5. **Challenge.** For the top three themes, write the strongest argument that the theme is
   overstated (sampling bias, one loud customer, recency).
6. **Suggest ideas.** For each top theme, one or two candidate ideas, phrased as jobs.

## Output

Write `signals/YYYY-MM-DD-<topic>.md`:

```
# Signals: <topic> (<window>)
Sources read: 12 call transcripts, 34 support tickets, #customer-feedback (2 weeks)
Not reachable: <anything that failed>

## Themes (ranked by evidence)
### 1. <problem, in the customer's terms>  — strong (7 calls, 19 tickets)
- "<verbatim quote>" — <source, date>
- Behavioural data: <metric and where it came from>
- Counter-argument: …
- Candidate ideas: …
```

End by asking which theme, if any, to turn into an idea with the `capture-idea` skill, or to
research further with the `desktop-research` skill.
