# PM Harness

A product-management harness for AI tools. It takes an idea from a one-liner to
engineering-ready tickets, and a person approves every step. It runs as a Claude plugin, and an
installer puts the same skills into Codex, Cursor, GitHub Copilot, Gemini CLI or any tool that
reads `AGENTS.md`.

```
Idea → (Grill) → PRD → Behaviour trees → Prototype variants → Eng-ready tickets
                (5 reviewers) (checked)    (checked + review loop)  (checked + DoD)
```

**Website and live demo:** https://mosin112.github.io/pm-harness/

## What is a harness?

An AI model on its own only turns text into text. A **harness** is everything you build around
it so it can do real work reliably: the context it reads, the procedures (skills) it follows,
the tools it can reach, the reviewers and checks its work must pass, and the memory it keeps.

> Agent = Model + Harness

This harness is built for product managers. It is made of plain files: Markdown skills,
reviewer definitions, a session-start hook, a Python checker and a small installer. There is
no server.

## The pipeline

| # | Step | Skill | Output | Checked by | Gate |
|---|---|---|---|---|---|
| 1 | Idea | `capture-idea` | `01-idea.md` (evidence counted and graded) | evidence rules | continue / grill / size / park |
| · | Grill (optional) | `product-grill` | `01-grill.md`: phase, settled points, the prototype decision | — | PM ends the grill |
| 2 | PRD | `write-prd` + `spec-review` | `02-prd.md`, `02-prd-review.md` | `pm_check.py prd` + 5 reviewers in fresh contexts | no open blocking findings |
| 3 | Behaviour trees | `write-behaviour-trees` | `03-trees/journey/`, `03-trees/functional/` | `pm_check.py trees` and `prd` (PRD ↔ trees) | PM approves |
| 4 | Prototype | `build-prototype` + `review-prototype` | `04-prototype/index.html`, `amendments.md` | `pm_check.py prototype` | variant chosen, no open amendments |
| 5 | Eng-ready tickets | `create-eng-tickets` | `05-tickets.md` + tracker | `pm_check.py tickets` | approval before anything is created |

**Run it by hand or in one go.** Every step is its own skill: run them one at a time, in any
session, and the files carry the state between them. Or run `one-shot`, which goes through all
the steps in order and stops at every gate for you. Either way a step is approved only when its
check passes and you say so.

Around the pipeline:

- **Discover:** `synthesize-signals` (your customers' evidence), `desktop-research` (the web:
  communities, app reviews, competitors, news, regulators), `opportunity-brief` (sizing)
- **Deliver and learn:** `stakeholder-update`, `launch-readout`
- **Everyday:** `meeting-prep`, `meeting-to-decisions`
- **Workspace:** `setup`, `update-context`, `done` (a session retrospective that turns repeated
  corrections into context and skill fixes)

## Phases: depth that fits the work

Every PRD declares a phase, and every later step sizes itself to it
([`reference/phases.md`](reference/phases.md)):

| Phase | Use it when | PRD | Prototype |
|---|---|---|---|
| `MVP` | The job or solution is unproven | ~2 pages, P0 only, continue / stop gate | 2 variants |
| `MMP` | It worked; now roll it out | ~3 pages, P0 + P1, launch gate per stage | 2 variants |
| `MLP` | Make people love it | ~3 pages, polish criteria, quality gate | 2–3 variants, high fidelity |
| `Enhancement` | Change something shipped | ~1.5 pages, the change + must-not-regress | 1 variant is fine |

## The PRD: eight sections

1 TL;DR · 2 Product shape · 3 Problem and job to be done · 4 Goals and non-goals ·
5 Requirements · 6 Experience and journey · 7 Success metrics and launch gates ·
8 Risks, constraints and open questions.

Each capability in §5 names the behaviour tree that will hold its exact behaviour
(`Tree: functional/price-alert-creation`), and §6.3 names the one trade-off the prototype
variants will argue about. The checker enforces the structure, the phase rules and the link
between PRD and trees in both directions. See [`reference/prd-guide.md`](reference/prd-guide.md).

## Behaviour trees: the contract

Trees describe observable behaviour in a strict, checkable grammar. Every line starts with
`when`, `while`, `if`, `then` or `and`, and every `then` becomes a test:

```
Functional: price-alert-creation (src: none; functional: none)
  when an investor submits a price alert for an asset
    while the investor is verified
      if the target price is zero or below
        then the price alert is rejected with the message "Enter a price above zero"
    while the investor is unverified
      then the investor is asked to complete verification before setting price alerts
```

The same lines appear word for word in the prototype's coverage map and the tickets'
acceptance criteria, and the checker proves it. Engineering copies the tree files into the
repository's `test-trees/` folder, where an engineering harness implements them test-first.
See [`reference/tree-grammar.md`](reference/tree-grammar.md).

## Prototype variants and the review loop

The prototype is one self-contained HTML file with **two or three design variants**, each
testing one hypothesis about the PRD's prototype decision ("set an alert in one step" versus
"see exactly what will be sent"). Every tree outcome must be demonstrable in every variant.
Screens keep the same id across variants, so switching variants keeps your place, and any state
has a deep link (`index.html#variant=guided&screen=set-alert&demo=err-full`).

Reviewers leave notes from inside the prototype; each note is pinned to a variant, screen and
scenario and lands in `amendments.md`. `review-prototype` walks every note on its screen and
classifies it: **PRD change**, **tree change**, **polish**, **later** or **dismiss**. Behaviour
changes go to the PRD and trees first, then the prototype. The prototype cannot be approved
while any amendment is open, and the PM records which variant won, and why, in PRD §6.3.

## Definition of done

`context/definition-of-done.md` holds the team's checklist for a finished story (tests for every
tree line, analytics, accessibility, constraints signed off, feature flag and monitoring, PM
acceptance in staging), plus extra items per phase. `create-eng-tickets` copies it into every
ticket set, and the checker refuses tickets without one.

## Install

### Claude Code and the Claude desktop app (plugin)

```
/plugin marketplace add mosin112/pm-harness
/plugin install pm-harness@pm-harness
```

Claude desktop app (Cowork): Customize → Browse plugins → Add marketplace from GitHub →
`mosin112/pm-harness`.

Then, in the folder you want to use as your PM workspace:

```
/pm-harness:setup
/pm-harness:one-shot <your idea>
```

### Any AI tool (installer)

In the folder you want to use as your PM workspace (needs Node 18+ and Python 3.8+):

```
npx github:Mosin112/pm-harness init
```

It asks which tools you use, shows the full plan and writes nothing until you agree.

| Tool | What it gets |
|---|---|
| Claude Code | the plugin (recommended), or the skills in `.claude/skills/` and reviewers in `.claude/agents/` |
| Codex | skills in `.agents/skills/` (run them as `$setup`, `$write-prd`…) |
| Cursor, GitHub Copilot | skills in `.agents/skills/` |
| Gemini CLI | skills in `.agents/skills/`, plus `GEMINI.md` importing `AGENTS.md` |
| Anything else | `AGENTS.md`, which lists every skill and where to find it |

Every tool shares the same workspace: `AGENTS.md` (rules and routing; `CLAUDE.md` imports it),
`context/`, `decisions/`, `work/` and `.pm-harness/` (checker, reference files, reviewers).
Your files are created once and never overwritten.

```
npx github:Mosin112/pm-harness update   # replace harness files, keep your work and local edits
npx github:Mosin112/pm-harness doctor   # check the installation and the workspace
```

Add `--tools codex,cursor --yes` to skip the questions, `--dry-run` to see the plan only.

### Connectors

Skills use whichever connectors you have for meeting notes, team chat, support, product
analytics, web research, your data warehouse, issue tracker, wiki, design and calendar. `setup`
records which tool to use for each need in `context/tools.md`.

The workspace's `.claude/settings.json` makes Claude ask before any tool writes to the tracker,
wiki, chat or email. Tool names depend on how each connector is installed; adjust the server
names in that file to match yours.

## Repository layout

```
.claude-plugin/        plugin.json and marketplace.json
skills/<name>/SKILL.md 19 skills
agents/                5 reviewer definitions used by spec-review
hooks/                 SessionStart hook: pipeline board + keeps .pm-harness/ current
scripts/pm_check.py    the checker behind the verification gates (stdlib Python)
bin/pm-harness.mjs     the installer for any AI tool (no dependencies)
reference/             PRD guide, phases, tree grammar, evidence rules, JTBD cheat sheet
templates/workspace/   the PM workspace that setup and the installer create
examples/price-alerts/ a complete worked example through all five steps
tests/                 checker fixtures and installer tests
site/                  website source
docs/                  built website (GitHub Pages)
```

## Verify

```
bash scripts/selftest.sh       # checker against the example and known-bad fixtures
npm test                       # installer
```

CI runs both on every push.

## Credits

Built by Mohsin Hafeez with Claude. Ideas borrowed with thanks from
[Anthropic's Product Management plugin](https://github.com/anthropics/knowledge-work-plugins/tree/main/product-management),
[Superpowers](https://github.com/obra/superpowers),
[Teresa Torres's context library](https://www.chatprd.ai/how-i-ai/teresa-torres-claude-code-obsdian-task-management),
[Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills),
[pm-skills](https://github.com/phuryn/pm-skills) and David Henry's
[Product Owner Toolkit](https://github.com/davidjwhenry/productownertoolkit) (product grill,
phase-aware PRDs, prototype variants and amendments, the session retrospective, desktop research
and the multi-tool installer).

The worked example uses illustrative sample data.

## License

MIT
