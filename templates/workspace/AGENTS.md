<!-- pm-harness-workspace -->
# PM workspace

This folder is a PM Harness workspace. AI tools read this file at the start of every session
(Claude Code through `CLAUDE.md`, Gemini CLI through `GEMINI.md`). Keep it short: it routes to
detail instead of containing it.

## What this workspace is for

Product work for **<team / product area>**, owned by **<PM name>**. Ideas move through a
pipeline, one folder per idea under `work/`:

```
01-idea.md → 01-grill.md → 02-prd.md (+ review) → 03-trees/ → 04-prototype/ (+ amendments)
→ 05-tickets.md → 06-launch-readout.md
```

## Routing index (read only what the task needs)

| When the task involves… | Read |
|---|---|
| Company, market, business model | `context/company.md` |
| Product areas, flows, recent launches, design tokens | `context/product.md` |
| Goals, OKRs, priorities | `context/strategy.md` |
| Users, segments, known jobs and pains | `context/users.md` |
| Any number or metric | `context/metrics.md` |
| Who decides, who reviews, how they like updates | `context/stakeholders.md` |
| Regulatory, legal, risk, brand or platform limits | `context/constraints.md` |
| Which connector to use for what | `context/tools.md` |
| Internal terms | `context/glossary.md` |
| Tone, length, formats | `context/writing-style.md` |
| What "done" means for engineering tickets | `context/definition-of-done.md` |
| Past decisions | `decisions/decision-log.md` |
| Past session reviews | `sessions/` |

## Rules

1. Follow the evidence rules in `.pm-harness/reference/evidence-rules.md`: count sources, quote
   real customer words only, grade evidence, take numbers from governed metric definitions and
   show where every number came from.
2. Never write to an external tool (tracker, wiki, chat, email) without the PM approving the
   exact content first.
3. Never rewrite a context file silently. Propose edits; apply only approved ones.
4. Keep each item's state in its files so any new session can resume from them.
5. When something is unclear, ask one sharp question rather than guessing.

<!-- pm-harness:begin -->
## PM Harness

This block is managed by PM Harness; an update replaces it. Put your own notes above it.

**At the start of a session,** unless a session-start hook has already shown it, run
`python3 .pm-harness/pm_check.py board .` and show the board in a few lines.

**Skills.** Each skill is a `SKILL.md` with its own instructions. Claude Code loads them from the
PM Harness plugin (`/pm-harness:<skill>`) or `.claude/skills/` (`/<skill>`); Codex, Cursor,
GitHub Copilot and Gemini CLI load them from `.agents/skills/` (Codex: `$<skill>`; others: ask
to "use the <skill> skill"). If a tool does not load skills, read
`.agents/skills/<skill>/SKILL.md` and follow it exactly.

| Group | Skills |
|---|---|
| Pipeline | `capture-idea` → `product-grill` (optional) → `write-prd` + `spec-review` → `write-behaviour-trees` → `build-prototype` + `review-prototype` → `create-eng-tickets` |
| Whole pipeline | `one-shot`: runs the steps in order and stops at every gate |
| Discover | `synthesize-signals`, `desktop-research`, `opportunity-brief` |
| Deliver and learn | `stakeholder-update`, `launch-readout` |
| Everyday | `meeting-prep`, `meeting-to-decisions` |
| Workspace | `setup`, `update-context`, `done` |

Every step can be run on its own, by hand, or all together with `one-shot`. Either way, a step
is approved only when its check passes and the PM says so.

**Reviewers** for `spec-review` are defined in `.pm-harness/agents/` (and registered as
subagents in Claude Code). Tools without subagents run them one at a time.

**Checks** (`python3 .pm-harness/pm_check.py <command>`): `prd`, `trees`, `prototype`,
`tickets`, `workspace`, `board`. Run the one for the step you are on; never call a step done
while its check fails.
<!-- pm-harness:end -->
