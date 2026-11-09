---
name: stakeholder-update
description: Use when the user wants a status update, weekly update, roadmap update or progress summary for stakeholders or leadership. Drafts a short update from the tracker, work items and decision log, leading with what the reader needs to do.
---

# Stakeholder update

## Steps

1. Ask (or infer from `context/stakeholders.md`) the **audience** and **period**.
2. Gather: the board (`python3 .pm-harness/pm_check.py board .`) for each item's stage, phase
   and open findings; ticket progress from the tracker connector; new decisions in the
   decision log; launch readouts and gate results; the chosen prototype variant; and blockers.
   Link the published PRD (Confluence) and prototype (artifact) from each PRD's `Links:` line.
   Use `roadmap.md` for what moved between Now, Next and Later, and the latest metrics review
   in `updates/` for the numbers.
3. **Keep stages true:** if the tracker shows work started on an item at `tickets`, propose
   `stage: building`; if its epic has shipped, propose `stage: launched` and a date for the
   launch readout (the end of the gate window in PRD §7). Change `01-idea.md` only on approval.
4. Write for the audience in `context/writing-style.md`. Default shape, under 200 words:

```
**Needs from you:** <decision or help needed, with a date> (or "Nothing this week")
**Shipped / moved:** 2–4 bullets, each with its impact
**Next:** 2–3 bullets
**Risks:** only real ones, each with a mitigation
**Numbers:** 1–3 metrics with their source
```

5. Every claim traces to a ticket, item file or metric source. No filler, no vague
   "progressing well".
6. Save the draft to `updates/YYYY-MM-DD-<audience>.md`.
7. **Never post or send automatically.** Show the draft; post to chat or email only after the
   PM approves the exact text.
