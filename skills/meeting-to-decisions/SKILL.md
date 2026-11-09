---
name: meeting-to-decisions
description: Use after a meeting when the user wants notes turned into decisions, action items, owners or follow-ups, or says "process my meeting". Extracts decisions, actions and risks from meeting notes or transcripts and proposes decision-log and item updates.
---

# Meeting → decisions

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs meeting-to-decisions` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `meeting-notes` · optional · the notes or transcript (or the PM pastes them)

## Steps

1. Find the meeting's notes or transcript with the `meeting-notes` tool from
   `context/tools.md` (or use what the PM pastes). Prefer the transcript for exact numbers,
   names and commitments; the summary leaves details out.
2. Extract:
   - **Decisions:** what was decided and by whom. A suggestion nobody agreed to is not a
     decision.
   - **Actions:** owner, due date (or "none set"), linked item
   - **Risks and open questions** raised
   - **Customer evidence** mentioned (route it to the relevant `work/` item or `signals/`)
   - **Prototype feedback:** add it to that item's `04-prototype/amendments.md` as open
     amendments (variant and screen if they can be told; `From:` the speaker), for
     `review-prototype`
   - **Answers to open questions** in a PRD's §8.3, and **requirement changes**: propose them
     as PRD edits under change control (`write-prd`, "After approval"), with the meeting as
     the source
3. Report what you could not determine (an unclear owner, an ambiguous agreement) instead of
   guessing.
4. Write `meetings/YYYY-MM-DD-<meeting>-decisions.md`.
5. **Propose** updates: new decision-log entries, changes to affected `work/` items, and any
   context-file updates. Apply only what the PM approves.
6. Offer to draft follow-up messages for the actions. Draft only; never send without approval.
