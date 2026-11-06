---
name: meeting-to-decisions
description: Use after a meeting when the user wants notes turned into decisions, action items, owners or follow-ups, or says "process my meeting". Extracts decisions, actions and risks from meeting notes or transcripts and proposes decision-log and item updates.
---

# Meeting → decisions

## Steps

1. Find the meeting's notes or transcript with the meeting-notes connector from
   `context/tools.md` (or use what the PM pastes). Prefer the transcript for exact numbers,
   names and commitments; the summary leaves details out.
2. Extract:
   - **Decisions:** what was decided and by whom. A suggestion nobody agreed to is not a
     decision.
   - **Actions:** owner, due date (or "none set"), linked item
   - **Risks and open questions** raised
   - **Customer evidence** mentioned (route it to the relevant `work/` item or `signals/`)
3. Report what you could not determine (an unclear owner, an ambiguous agreement) instead of
   guessing.
4. Write `meetings/YYYY-MM-DD-<meeting>-decisions.md`.
5. **Propose** updates: new decision-log entries, changes to affected `work/` items, and any
   context-file updates. Apply only what the PM approves.
6. Offer to draft follow-up messages for the actions. Draft only; never send without approval.
