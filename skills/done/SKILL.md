---
name: done
description: Use when the PM says "done", "wrap up", "close the session", "what should we learn from this" or asks for a session retrospective. Reviews this session and recent ones for repeated corrections, re-explained facts and friction, then proposes context updates, Definition of done changes, skill improvements and open threads; applies only what the PM approves.
---

# Done: session retrospective

One correction is a task instruction; the same correction across sessions is a gap in the
context or in a skill. This skill finds those gaps and proposes the smallest fix for each.
`update-context` captures what one session learned; `done` looks across sessions for patterns.

## 1. Load what is already recorded

Read `AGENTS.md` (or a 0.1 workspace's `CLAUDE.md`), every file in `context/` (including
`definition-of-done.md`) and the newest entries in `decisions/decision-log.md`, so nothing
already recorded is suggested again. List the harness skills and what each is for.

## 2. Set the review window

1. Find the newest `sessions/*-done.md`. Its `Reviewed to:` line is the cutoff. Read its
   **Declined** list and do not raise those again without new evidence.
2. Review this conversation plus earlier ones from this workspace, newest first, stopping at
   the cutoff or after five earlier conversations, whichever comes first.

## 3. Gather earlier conversations

This conversation is already in context. Earlier ones are local transcript files, if the tool
keeps them:

| Tool | Where | Scope to this workspace by |
|---|---|---|
| Claude Code | `~/.claude/projects/<workspace path with "/" as "-">/*.jsonl` | the folder name |
| Codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | `cwd` in the first line |
| Cursor | `~/.cursor/projects/<workspace path with "/" as "-">/agent-transcripts/` | the folder name |

- Take the newest files first and skip this session's own file.
- Transcripts are large. Extract only the PM's messages and your final replies; skip tool calls
  and results. For Claude Code, for example:
  `jq -r 'select(.type=="user" and (.isMeta|not)) | .message.content | if type=="string" then . else (map(select(.type=="text").text)|join("\n")) end | select(length>0)' <file>.jsonl`
- If no transcripts are reachable (a cloud session, or a tool that does not keep them), say so
  and review this conversation only. Do not guess at earlier sessions.
- Transcripts stay on the machine. Never copy long excerpts, secrets or personal details about
  named people into the log.

## 4. Look for patterns

Read for evidence, not impressions:

- **Repeated corrections:** the PM fixed the same thing twice (tone, length, structure, naming).
- **Re-explained facts:** the PM supplied the same fact about the company, users, metrics,
  stakeholders or constraints again.
- **Gate friction:** a gate or check the PM skipped, overrode or had to rescue; a reviewer
  finding that keeps coming back across items.
- **Manual workflows:** the same multi-step request made without a skill, or a skill always
  followed by the same extra steps.
- **Definition of done gaps:** something engineering or the PM asked for at handoff that the
  Definition of done does not list.
- **Open threads:** work started and not finished; a decision deferred and never recorded.

A pattern needs two occurrences, or one explicit "always" or "never" from the PM. Cite the
evidence for each (date and a one-line paraphrase). If nothing qualifies, say so; do not pad.

## 5. Route each pattern to the smallest fix

| Pattern | Fix | Where |
|---|---|---|
| Tone, length, format preference | A rule | `context/writing-style.md` |
| Missing fact about company, product, users, metrics, constraints, stakeholders | An addition | the matching `context/` file |
| Term used inconsistently or re-explained | A row | `context/glossary.md` |
| Decision made but not logged | An entry | `decisions/decision-log.md` |
| Handoff item engineering keeps asking for | An item | `context/definition-of-done.md` |
| A harness skill missed a step or asked the wrong thing | A skill improvement | see below |
| Recurring workflow with no skill | A new skill idea | see below |
| Unfinished work | An open question with an owner | the item's `01-idea.md` or PRD §8.3 |

Prefer a context entry over a skill change, and a skill change over a new skill.

**Skill improvements and new skills:** the harness's skills are managed files that updates
replace, so do not edit them in an installed workspace. Instead, if the fix can live in
context (most can), put it there. Otherwise append the suggestion to
`.pm-harness/skill-feedback.md` and offer to draft an issue for the PM Harness repository. Edit
skill files directly only when working in a clone of the PM Harness repository itself.

## 6. Play back before writing

```
## Session review
**Reviewed:** this conversation plus <n> earlier, <start date> to <end date>

### Context updates
1. `context/writing-style.md`: <rule>. *Evidence: <date>: <one line>; <date>: <one line>.*
### Definition of done
2. …
### Skill improvements
3. `write-prd`: <change>. *Evidence: …*
### Open threads
4. <thread>: <owner and next step>

Which should I apply? (numbers, "all" or "none")
```

Leave out empty sections. Number suggestions continuously.

## 7. Apply and log

1. Apply only the accepted suggestions, exactly as approved. Never write to a context file
   silently.
2. Write `sessions/YYYY-MM-DD-HHMM-done.md` (create the folder if needed), even when nothing was
   accepted, because it is the cutoff for the next run:

```
# Session review
Reviewed to: <ISO timestamp of this run>
Conversations reviewed: <n>

## Applied
- <suggestion> → <file>
## Declined
- <suggestion>
## Open threads
- …
```
