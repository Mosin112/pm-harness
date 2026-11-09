---
name: setup
description: Use when the user wants to set up, initialise or repair a PM Harness workspace, or says "set up the PM harness". Creates the context library, decision log, work folders, approval rules and the checker, then interviews the PM to fill the context files.
disable-model-invocation: true
---

# Set up a PM Harness workspace

The workspace is the harness's memory. Every other skill reads it, so a good setup is the
single biggest lever on output quality. Take the time to do it properly.

## 1. Find or create the workspace

- If the current folder's `AGENTS.md` or `CLAUDE.md` contains `<!-- pm-harness-workspace -->`,
  this is an existing workspace: switch to **repair mode** (step 5). If the PM Harness
  installer (`npx github:Mosin112/pm-harness init`) has just run, the files are already in
  place: go straight to step 3.
- Otherwise ask where the workspace should live (default: the current folder) and confirm
  before writing anything.

## 2. Copy the template

If the workspace has `.pm-harness/install.json`, the npx installer manages these files: skip
this step (refresh them with `npx github:Mosin112/pm-harness update`). Otherwise copy
everything under `../../templates/workspace/` (relative to this skill) into the workspace,
without overwriting any file that already exists. Then create `.pm-harness/` with
the checker and the shared reference files:

- `../../scripts/pm_check.py` → `.pm-harness/pm_check.py`
- `../../reference/*.md` → `.pm-harness/reference/`
- `../../agents/*.md` → `.pm-harness/agents/`

Resulting layout:

```
AGENTS.md                  rules + routing index, read by every AI tool
CLAUDE.md                  imports AGENTS.md for Claude Code
context/                   small, focused context files (loaded only when relevant)
decisions/decision-log.md  every product decision, newest first
signals/                   dated evidence syntheses and research
work/<item>/               one folder per idea, numbered by pipeline step
meetings/  updates/        meeting briefs, decisions, stakeholder updates
sessions/                  session reviews written by the done skill
.claude/settings.json      asks before any tool writes to Jira, Slack, Confluence or email
.pm-harness/               the checker, reference files and reviewer definitions
```

To use the workspace from Codex, Cursor, GitHub Copilot or Gemini CLI as well, tell the PM to
run `npx github:Mosin112/pm-harness init` in the workspace and pick those tools; it adds the
skills to `.agents/skills/` without touching their context.

## 3. Interview the PM to fill the context

Fill the `context/` files through a short conversation, **one file at a time**, asking at most
three questions per file. Prefer pulling from existing sources (wiki pages, strategy docs,
metric dictionaries) over asking: ask the PM where those live and read them.

| File | What it must contain |
|---|---|
| `company.md` | What the company does, for whom, markets, business model, stage |
| `product.md` | Product areas, platforms, key flows, what shipped recently, design tokens |
| `strategy.md` | Current goals or OKRs, this quarter's bets, what is explicitly not a priority |
| `users.md` | Segments, top jobs-to-be-done already known, key pains |
| `metrics.md` | Each metric: plain definition, owner, where its governed definition or query lives |
| `stakeholders.md` | Who decides what, who must review what, how each person likes updates |
| `constraints.md` | Regulatory, risk, legal, brand and platform constraints every PRD must respect |
| `tools.md` | Which connector to use for meetings, chat, analytics, research, warehouse, tracker, wiki, design |
| `glossary.md` | Internal terms and acronyms, and the words to avoid |
| `writing-style.md` | Tone, length limits, formats the team expects |
| `definition-of-done.md` | The team's checklist for a finished engineering story; start from the template and ask engineering what to add |

Keep each file under ~150 lines. If a file grows past that, split it and add the new file to
the routing index in `AGENTS.md` (above the managed block).

## 4. Connectors and approval rules

1. **Start from what is connected.** List the connectors (MCP servers) and tools available in
   this session and propose a row of `context/tools.md` for each need they cover, for example:
   Jira → issue tracker; Confluence → wiki and **PRD publishing** (ask for the space and parent
   page); Granola or another notetaker → meeting notes; Slack → team chat; Mixpanel or Amplitude
   → product analytics; a warehouse or metrics connector → governed metrics (and link each
   metric in `context/metrics.md` to its definition there); Figma → design; web search or
   Firecrawl → research; the Artifact tool → **prototype and trees sharing**. Confirm each row
   with the PM rather than guessing what they use.
2. **Verify each one** with one harmless read call (search one meeting, read one ticket, list
   one dashboard, run one web search). Report which work and which need connecting. Do not write
   anything to an external tool during setup.
3. **Approval rules (Claude Code).** List every connected tool whose name says it creates,
   updates, sends, posts, publishes, moves or deletes something (`createJiraIssue`,
   `updateConfluencePage`, `slack_send_message`, `send_message`, `create_event`, `update_file`,
   `notion-create-pages`, `Create-Cohort`, `publish_artifact`…). Show the list, and on approval
   write the exact tool names (`mcp__<server>__<tool>`, matching case) to `permissions.ask` in
   `.claude/settings.json`, keeping what is already there. Other tools rely on rule 2 in
   `AGENTS.md`: never write externally without the PM approving the exact content.

## 5. Repair mode

On an existing workspace: report missing folders or files and restore them from
`../../templates/workspace/` without overwriting; refresh `.pm-harness/` (step 2, or
`npx github:Mosin112/pm-harness update` for an installer-managed workspace); list context
files older than 90 days and offer to review them with the PM; run
`python3 .pm-harness/pm_check.py workspace .`.

A workspace from PM Harness 0.1 keeps everything in `CLAUDE.md`. Offer to move that content
into `AGENTS.md` (so other tools can read it) and leave `CLAUDE.md` as the two-line import from
the template. Do it only with the PM's approval.

## 6. Finish

Print a short summary: what was created, which context files are still thin, which connectors
work. Suggest the first move: the `synthesize-signals` or `desktop-research` skill if there is
evidence to gather, or the `capture-idea` skill if the PM already has an idea.
