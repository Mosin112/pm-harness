# PM Harness

A product-management harness for Claude. It takes an idea from a one-liner to
engineering-ready tickets in one sitting, and a person approves every step.

```
Idea → Concept + JTBD → Behaviour trees → Prototype → Eng-ready tickets
       (5 independent reviewers)   (checked)     (checked)     (checked)
```

**Website and live demo:** https://__OWNER__.github.io/pm-harness/

## What is a harness?

An AI model on its own only turns text into text. A **harness** is everything you build around
it so it can do real work reliably: the context it reads, the procedures (skills) it follows,
the tools it can reach, the reviewers and checks its work must pass, and the memory it keeps.

> Agent = Model + Harness

This harness is built for product managers. It is a Claude plugin made of plain files:
Markdown skills, reviewer-agent definitions, one session-start hook and a Python checker.
There is no server and no build step.

## The pipeline

| # | Step | Skill | Output | Checked by | Gate |
|---|---|---|---|---|---|
| 1 | Idea | `capture-idea` | `01-idea.md` (evidence counted and graded) | evidence rules | continue / size / park |
| 2 | Concept + JTBD | `write-concept` + `spec-review` | `02-concept.md`, `02-concept-review.md` | 5 reviewer agents in fresh contexts | no open blocking findings |
| 3 | Behaviour trees | `write-behaviour-trees` | `03-trees/journey/`, `03-trees/functional/` | `pm_check.py trees` | PM approves |
| 4 | Prototype | `build-prototype` | `04-prototype/index.html` | `pm_check.py prototype` | PM approves |
| 5 | Eng-ready tickets | `create-eng-tickets` (manual) | `05-tickets.md` + tracker | `pm_check.py tickets` | approval before anything is created |

`/pm-harness:one-shot` runs all five in order and stops at every gate.

Around the pipeline:

- **Discover:** `synthesize-signals`, `opportunity-brief`
- **Deliver and learn:** `stakeholder-update`, `launch-readout`
- **Everyday:** `meeting-prep`, `meeting-to-decisions`
- **Workspace:** `setup`, `update-context`

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

## Install

**Claude Code**

```
/plugin marketplace add __OWNER__/pm-harness
/plugin install pm-harness@pm-harness
```

**Claude desktop app (Cowork):** Customize → Browse plugins → Add marketplace from GitHub →
`__OWNER__/pm-harness`.

Then, in the folder you want to use as your PM workspace:

```
/pm-harness:setup
/pm-harness:one-shot <your idea>
```

### Connectors

Skills use whichever connectors you have for meeting notes, team chat, support, product
analytics, your data warehouse, issue tracker, wiki, design and calendar. `setup` records which
tool to use for each need in `context/tools.md`.

The workspace's `.claude/settings.json` makes Claude ask before any tool writes to the tracker,
wiki, chat or email. Tool names depend on how each connector is installed; adjust the server
names in that file to match yours.

## Repository layout

```
.claude-plugin/        plugin.json and marketplace.json
skills/<name>/SKILL.md 15 skills
agents/                5 reviewer agents used by spec-review
hooks/                 SessionStart hook: pipeline board + keeps the checker current
scripts/pm_check.py    the checker behind the verification gates (stdlib Python)
scripts/build_site.py  builds the website into docs/
reference/             tree grammar, evidence rules, JTBD cheat sheet
templates/workspace/   the PM workspace that setup creates
examples/price-alerts/ a complete worked example through all five steps
site/                  website source
docs/                  built website (GitHub Pages)
```

## Verify

```
python3 scripts/pm_check.py plugin .
python3 scripts/pm_check.py trees examples/price-alerts/03-trees
python3 scripts/pm_check.py prototype examples/price-alerts/03-trees examples/price-alerts/04-prototype/index.html
python3 scripts/pm_check.py tickets examples/price-alerts/03-trees examples/price-alerts/05-tickets.md
bash scripts/selftest.sh
```

CI runs the same checks on every push.

## Credits

Built at Fasset by Mohsin Hafeez with Claude. Ideas borrowed with thanks from
[Anthropic's Product Management plugin](https://github.com/anthropics/knowledge-work-plugins/tree/main/product-management),
[Superpowers](https://github.com/obra/superpowers),
[Teresa Torres's context library](https://www.chatprd.ai/how-i-ai/teresa-torres-claude-code-obsdian-task-management),
[Product-Manager-Skills](https://github.com/deanpeters/Product-Manager-Skills) and
[pm-skills](https://github.com/phuryn/pm-skills).

The worked example uses illustrative sample data.

## License

MIT
