---
name: stakeholder-update
description: Use when the user wants a status update, weekly update, roadmap update or progress summary for stakeholders or leadership. Drafts a short update from the tracker, work items and decision log, leading with what the reader needs to do.
---

# Stakeholder update

## Steps

1. Ask (or infer from `context/stakeholders.md`) the **audience** and **period**.
2. Gather: ticket progress from the tracker connector, `stage` changes in `work/*/01-idea.md`,
   new decisions in the decision log, launch readouts, and blockers.
3. Write for the audience in `context/writing-style.md`. Default shape, under 200 words:

```
**Needs from you:** <decision or help needed, with a date> (or "Nothing this week")
**Shipped / moved:** 2–4 bullets, each with its impact
**Next:** 2–3 bullets
**Risks:** only real ones, each with a mitigation
**Numbers:** 1–3 metrics with their source
```

4. Every claim traces to a ticket, item file or metric source. No filler, no vague
   "progressing well".
5. Save the draft to `updates/YYYY-MM-DD-<audience>.md`.
6. **Never post or send automatically.** Show the draft; post to chat or email only after the
   PM approves the exact text.
