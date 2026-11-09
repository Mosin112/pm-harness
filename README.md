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
| 3 | Behaviour trees | `write-behaviour-trees` | `03-trees/journey/`, `03-trees/functional/`, `03-trees-view.html` | `pm_check.py trees` and `prd` (PRD ↔ trees) | PM reviews the diagram and approves |
| 4 | Prototype | `build-prototype` + `review-prototype` | `04-prototype/index.html`, `amendments.md` | `pm_check.py prototype` | variant chosen, no open amendments |
| 5 | Eng-ready tickets | `create-eng-tickets` | `05-tickets.md` + tracker, `05-contracts/` | `pm_check.py tickets` (with the PRD's metrics) | approval before anything is created |

`python3 .pm-harness/pm_check.py item work/<item>` runs every check that applies to an item, and
the pipeline board at the start of each session flags any item whose checks fail.

**Run it by hand or in one go.** Every step is its own skill: run them one at a time, in any
session, and the files carry the state between them. Or run `one-shot`, which goes through all
the steps in order and stops at every gate for you. Either way a step is approved only when its
check passes and you say so.

Around the pipeline:

- **Share:** `publish` puts the PRD on Confluence and the prototype and trees view up as Claude
  artifacts, and brings comments back as proposed changes
- **Discover:** `synthesize-signals` (your customers' evidence), `desktop-research` (the web:
  communities, app reviews, competitors, news, regulators), `opportunity-brief` (sizing), and
  `product-grill`, which explores an open problem (How Might We, opportunity solution tree,
  riskiest assumption) before it converges
- **Plan:** `roadmap` keeps a Now / Next / Later view in step with the items, their evidence and
  stages, and logs every move as a decision
- **Deliver and learn:** `stakeholder-update`, `metrics-review` (weekly, monthly or quarterly
  review of the metric hierarchy from governed numbers), `launch-readout`
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

## The PRD: eight sections, under change control

1 TL;DR · 2 Product shape · 3 Problem and job to be done · 4 Goals and non-goals ·
5 Requirements · 6 Experience and journey · 7 Success metrics and launch gates ·
8 Risks, constraints and open questions.

Each capability in §5 names the behaviour tree that will hold its exact behaviour
(`Tree: functional/price-alert-creation`), and §6.3 names the one trade-off the prototype
variants will argue about. The checker enforces the structure, the phase rules and the link
between PRD and trees in both directions. Once approved, every change is a row in the PRD's change
log with its source (an amendment, a Confluence comment, a meeting), and changes to scope,
requirements or metrics are re-reviewed. See [`reference/prd-guide.md`](reference/prd-guide.md).

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
acceptance criteria, and the checker proves it. See
[`reference/tree-grammar.md`](reference/tree-grammar.md).

**Review them as a diagram.** `pm_check.py view work/<item>` draws every tree left to right
(event → state → condition → outcome) with the PRD section, the prototype screen and the ticket
for each outcome. Published as a Claude artifact, the PM clicks **Comment** on any line and sends
it to Claude in the same session; Claude changes the tree file, re-runs the checks and
republishes the view. Outside Claude, the page collects notes to paste into the chat.

**Hand them to engineering as contracts.** `pm_check.py contracts work/<item>` writes one
contract per tree in the [engineering harness](https://github.com/Mosin112/engineering-harness)
format (`Contract: <subject> (seam: …)` and the same lines) to `05-contracts/`, ready for the
service repository's `contracts/` folder, where each clause is implemented test-first.

## Prototype variants and the review loop

The prototype is one self-contained HTML file with **two or three design variants**, each
testing one hypothesis about the PRD's prototype decision ("set an alert in one step" versus
"see exactly what will be sent"). Every tree outcome must be demonstrable in every variant.
Screens keep the same id across variants, so switching variants keeps your place, and any state
has a deep link (`index.html#guided--set-alert--err-full`). Every prototype starts from the shell
in `templates/prototype/`, whose shared runtime handles variants, deep links, the coverage panel
and review notes, so only the screens and their behaviour are written per item.

**Designed, not generated.** Prototypes take their colours, type and components from the
workspace's `DESIGN.md` (the [DESIGN.md format](https://github.com/google-labs-code/design.md),
filled at setup from Figma, the app's theme or the brand guide) and follow
[`reference/prototype-craft.md`](reference/prototype-craft.md), adapted from
[Impeccable](https://github.com/pbakaus/impeccable): screens built for a task, variants that differ
in their hypothesis rather than decoration, a craft floor and a list of generated-design tells to
refuse. Each variant gets a heuristic design review before the PM sees it
(`design-review.md`), and the checker flags emoji icons, gradient text and missing focus styles.

Reviewers leave notes from inside the prototype: as a Claude artifact, **Comment on this screen**
sends the note to Claude; from a file, the review card copies an amendment. Each note is pinned
to a variant, screen and scenario and lands in `amendments.md`. `review-prototype` walks every note on its screen and
classifies it: **PRD change**, **tree change**, **polish**, **later** or **dismiss**. Behaviour
changes go to the PRD and trees first, then the prototype. The prototype cannot be approved
while any amendment is open. The PM records which variant won, and why, in PRD §6.3; the others
are archived, so only the chosen one has to stay complete.

## Publishing and feedback

`publish` puts the PRD on Confluence (in the space and under the page named in
`context/tools.md`) and the prototype and trees view up as private Claude artifacts. The
workspace stays the source of truth: Confluence comments become proposed PRD changes, artifact
comments become amendments or tree changes, and the published copies are republished after
each change.

## Definition of done

`context/definition-of-done.md` holds the team's checklist for a finished story (tests for every
tree line, analytics, accessibility, constraints signed off, feature flag and monitoring, PM
acceptance in staging), plus extra items per phase. `create-eng-tickets` copies it into every
ticket set, and the checker refuses tickets without one. Analytics events live in their own
story, and the checker makes sure every metric in PRD §7 is named there.

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

Skills never name a tool. Each `SKILL.md` has a **Needs** block (governed metrics, product
analytics, web research, a design source, an issue tracker…, each required or optional), and
`context/tools.md` maps every need to the tools your team uses, several per need if you like:

```
| Need | Tool | Role | Source | Trusted for | Notes |
| governed-metrics | Metabase | main | internal | every metric in metrics.md | collection "Product KPIs" |
| product-analytics | Mixpanel | main | internal | events, funnels | project "App" |
| product-analytics | Amplitude | also | internal | events before 2025 | |
| web-research | Firecrawl | main | external | | |
| web-research | web search | fallback | external | | built into the AI tool |
| design-source | Figma | main | internal | tokens, components, screens | |
| design-source | Google Drive | also | internal | brand guide | folder "Brand" |
```

Before a skill starts, `pm_check.py needs <skill>` lists what it needs and which tools serve it;
the skill confirms each tool answers with one read call and says what is missing before doing the
work (`one-shot` checks every step up front). External numbers, from Firecrawl or any outside
source, are kept apart as labelled benchmarks and never stand in for your own metrics. The
plugin ships no connectors: `setup` maps the ones you have and suggests what to add
(`reference/connectors.md`).

The workspace's `.claude/settings.json` makes Claude ask before any tool writes to the tracker,
wiki, chat or email. Tool names depend on how each connector is installed; adjust the server
names in that file to match yours.

## Repository layout

```
.claude-plugin/        plugin.json and marketplace.json
skills/<name>/SKILL.md 22 skills
agents/                5 reviewer definitions used by spec-review
hooks/                 SessionStart hook: pipeline board + keeps .pm-harness/ current
scripts/pm_check.py    the checker behind the gates, plus the trees view, contracts and artifact generators (stdlib Python)
bin/pm-harness.mjs     the installer for any AI tool (no dependencies)
reference/             PRD guide, phases, prototype craft, connectors, tree grammar, evidence rules, JTBD cheat sheet
templates/workspace/   the PM workspace that setup and the installer create
templates/prototype/   the prototype shell with the shared runtime
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
[Anthropic's product-management plugin](https://github.com/anthropics/knowledge-work-plugins/tree/main/product-management)
(the roadmap, metrics review and explore mode, Apache-2.0),
Paul Bakaus's [Impeccable](https://github.com/pbakaus/impeccable) (the prototype craft rules and
design review, Apache-2.0),
David Henry's [Product Owner Toolkit](https://github.com/davidjwhenry/productownertoolkit) (product
grill, phase-aware PRDs, prototype variants and amendments, the session retrospective, desktop
research and the multi-tool installer),
[Superpowers](https://github.com/obra/superpowers),
[Teresa Torres's context library](https://www.chatprd.ai/how-i-ai/teresa-torres-claude-code-obsdian-task-management),
[Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills) and
[pm-skills](https://github.com/phuryn/pm-skills).

The worked example uses illustrative sample data.

## License

MIT
