# PM Harness

A Claude plugin that takes a product idea from a one-liner to engineering-ready tickets in one
sitting. A person approves every step.

**Live demo:** https://mosin112.github.io/pm-harness/

```
Idea → Concept + JTBD → Behaviour trees → Prototype → Eng-ready tickets
       (5 reviewers)      (checked)        (checked)     (checked)
```

## Install

```
/plugin marketplace add mosin112/pm-harness
/plugin install pm-harness@pm-harness
```

In the Claude desktop app: Customize → Browse plugins → Add marketplace from GitHub →
`mosin112/pm-harness`.

Then, in your PM workspace folder:

```
/pm-harness:setup                    # creates the context library
/pm-harness:one-shot <your idea>     # runs the whole pipeline
```

## The pipeline

| Step | Skill | Output | Checked by |
|---|---|---|---|
| 1. Idea | `capture-idea` | `01-idea.md` | evidence rules |
| 2. Concept + JTBD | `write-concept`, `spec-review` | `02-concept.md` | 5 reviewer agents |
| 3. Behaviour trees | `write-behaviour-trees` | `03-trees/` | `pm_check.py trees` |
| 4. Prototype | `build-prototype` | `04-prototype/index.html` | `pm_check.py prototype` |
| 5. Tickets | `create-eng-tickets` | `05-tickets.md` + tracker | `pm_check.py tickets` |

Each step ends at an approval gate, and nothing is written to Jira, Slack or email without
approval. Other skills: `synthesize-signals`, `opportunity-brief`, `stakeholder-update`,
`launch-readout`, `meeting-prep`, `meeting-to-decisions`, `update-context`.

## Behaviour trees

The contract between product and engineering. Every line starts with `when`, `while`, `if`,
`then` or `and`, and every `then` becomes a test:

```
when an investor submits a price alert
  while the investor is verified
    if the target price is zero or below
      then the price alert is rejected with the message "Enter a price above zero"
```

The same lines appear word for word in the prototype and in the tickets' acceptance criteria,
and the checker proves it. See [`reference/tree-grammar.md`](reference/tree-grammar.md) and the
full worked example in [`examples/price-alerts/`](examples/price-alerts/).

## Develop

```
bash scripts/selftest.sh                         # all checks, also run in CI
python3 scripts/build_site.py mosin112/pm-harness  # rebuild the site into docs/
```

The worked example uses illustrative sample data. MIT licensed.
