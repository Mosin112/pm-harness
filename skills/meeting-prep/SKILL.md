---
name: meeting-prep
description: Use when the user is preparing for a meeting, review, 1:1 or stakeholder conversation, or asks "prep me for…". Produces a one-page brief with context, each attendee's likely priorities, the PM's ask and a fallback.
---

# Meeting prep

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs meeting-prep` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `calendar` · optional · the meeting, its time and attendees (or the PM gives them)
- `meeting-notes` · optional · what the attendees said and asked for last time

## Steps

1. Find the meeting with the `calendar` tool (or ask for the title, time and attendees).
2. For each attendee, read `context/stakeholders.md` and recent meeting notes with them.
   Note what they care about and what they last asked for. Use only information from work
   sources; do not profile people beyond their work role and stated priorities.
3. Find related items: `work/` items, open decisions, recent signals, open questions owned by
   attendees.
4. Ask the PM one question: **what do you need from this meeting?** Do not guess the ask.
5. Write `meetings/YYYY-MM-DD-<meeting>-brief.md`, one page maximum:

```
# Brief: <meeting> (<date, time>)
**My ask:** <one sentence>  ·  **Fallback:** <acceptable smaller outcome>

## Context in 3 bullets
## Attendees
| Who | Cares about | Likely question or objection | My answer |
## Decisions needed
## Numbers I may need (with sources)
```

Label predicted objections as preparation, not fact.
