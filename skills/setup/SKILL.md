---
name: setup
description: Use when the user wants to set up, initialise or repair a PM Harness workspace, or says "set up the PM harness". Creates the context library, decision log, work folders, approval rules and the checker script, then interviews the PM to fill the context files.
disable-model-invocation: true
---

# Set up a PM Harness workspace

The workspace is the harness's memory. Every other skill reads it, so a good setup is the
single biggest lever on output quality. Take the time to do it properly.

## 1. Find or create the workspace

- If the current folder's `CLAUDE.md` contains `<!-- pm-harness-workspace -->`, this is an
  existing workspace: switch to **repair mode** (step 5).
- Otherwise ask where the workspace should live (default: the current folder) and confirm
  before writing anything.

## 2. Copy the template

This skill's base directory is shown when it loads. The plugin root is two levels up from it.
Copy everything under `<plugin root>/templates/workspace/` into the workspace, without
overwriting any file that already exists. Then copy `<plugin root>/scripts/pm_check.py` to
`.pm-harness/pm_check.py`.

Resulting layout:

```
CLAUDE.md                  rules + routing index (always loaded)
context/                   small, focused context files (loaded only when relevant)
decisions/decision-log.md  every product decision, newest first
signals/                   dated evidence syntheses
work/<item>/               one folder per idea, numbered by pipeline step
meetings/  updates/        meeting briefs, decisions, stakeholder updates
.claude/settings.json      asks before any tool writes to Jira, Slack, Confluence or email
.pm-harness/pm_check.py    the checker used by the verification gates
```

## 3. Interview the PM to fill the context

Fill the `context/` files through a short conversation, **one file at a time**, asking at most
three questions per file. Prefer pulling from existing sources (wiki pages, strategy docs,
metric dictionaries) over asking: ask the PM where those live and read them.

| File | What it must contain |
|---|---|
| `company.md` | What the company does, for whom, markets, business model, stage |
| `product.md` | Product areas, platforms, key flows, what shipped recently |
| `strategy.md` | Current goals or OKRs, this quarter's bets, what is explicitly not a priority |
| `users.md` | Segments, top jobs-to-be-done already known, key pains |
| `metrics.md` | Each metric: plain definition, owner, where its governed definition or query lives |
| `stakeholders.md` | Who decides what, who must review what, how each person likes updates |
| `constraints.md` | Regulatory, risk, legal, brand and platform constraints every spec must respect |
| `tools.md` | Which connector to use for meetings, chat, analytics, warehouse, tracker, wiki, design |
| `glossary.md` | Internal terms and acronyms |
| `writing-style.md` | Tone, length limits, formats the team expects |

Keep each file under ~150 lines. If a file grows past that, split it and add the new file to
the routing index in `CLAUDE.md`.

## 4. Verify the connectors

For each tool listed in `tools.md`, make one harmless read call (search one meeting, read one
ticket, list one dashboard). Report which work and which need connecting. Do not write
anything to an external tool during setup.

## 5. Repair mode

On an existing workspace: report missing folders or files and restore them from the template
without overwriting; refresh `.pm-harness/pm_check.py`; list context files older than 90 days
and offer to review them with the PM; run `python3 .pm-harness/pm_check.py workspace .`.

## 6. Finish

Print a short summary: what was created, which context files are still thin, which connectors
work. Suggest the first move: `/pm-harness:synthesize-signals` if there is a backlog of
evidence, or `/pm-harness:capture-idea` if the PM already has an idea.
