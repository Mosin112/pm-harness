---
name: update-context
description: Use at the end of a useful session, or when the user says "remember this", "update the context" or "what did we learn". Proposes small, specific edits to the PM workspace's context files and decision log, and applies only the ones the PM approves.
---

# Update the context library

The harness gets better only if what it learns is written down. This skill is the memory
layer: it turns a session's lessons into durable, reviewable edits.

## Steps

1. Review the session: decisions made, facts learned about users, metrics, stakeholders or
   constraints, corrections the PM made to your output, and repeated instructions the PM had
   to give you.
2. For each lesson, pick the one file it belongs in (see the routing index in `AGENTS.md`).
   Decisions go to `decisions/decision-log.md`; new terms to `context/glossary.md`; anything
   engineering asked for at handoff to `context/definition-of-done.md`. A correction to how a
   skill behaves goes to `context/writing-style.md` or is reported as a suggested skill change.
3. Present the proposals as a numbered list. For each: the file, the exact text to add or
   replace, and one line on why. Keep each edit small.
4. **Wait for approval.** Apply only the items the PM approves, exactly as approved. Never
   rewrite a context file silently, and never delete content without explicit approval.
5. If a file now exceeds ~150 lines, propose a split and a routing-index update.

To look for patterns across several sessions rather than this one, use the `done` skill.

## Decision log entry format

```
## YYYY-MM-DD: <decision in one line>
- **Context:** why this came up (link to item, meeting or signal)
- **Decision:** what was decided, by whom
- **Alternatives considered:** …
- **Revisit if:** the condition that would reopen it
```
