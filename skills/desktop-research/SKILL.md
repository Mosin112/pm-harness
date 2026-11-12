---
name: desktop-research
description: Use when the user wants to research a product, feature, competitor, market or regulation on the public web, asks "what do people online say about X", "how do competitors do X", "look into X" or wants market evidence before writing a PRD (for the company's own customer evidence, use synthesize-signals). Runs time-boxed web research (quick ~10 min, standard ~20, thorough ~30–40 with parallel researchers) and writes an evidence-counted research report with cited sources and stated gaps.
---

# Desktop research

Builds a factual, cited view of a product, feature, competitor set, market or rule from the
public web, ready to feed `capture-idea`, `opportunity-brief` or PRD §3. Read
`../../reference/evidence-rules.md` first; web evidence follows the same rules as customer
evidence.

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs desktop-research` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `web-research` · required · searching and reading public pages (Firecrawl, or the AI tool's own
  web search)
- `market-data` · optional · structured outside figures when numbers are in scope; they stay
  external (evidence rule 9)

## Time boxes

Research is time-boxed. Pick the depth with the PM; each has a budget of searches, pages read
and time, and the search stops when the budget or the time box runs out, whichever comes first.

| Depth | Use when | Source types | Searches | Pages read | Time box |
|---|---|---|---|---|---|
| `quick` | A fast read before a grill or one PRD section | 1–2 | ≤ 6 | ≤ 5 | ~10 min |
| `standard` (default) | Pre-PRD discovery | up to 3 | ≤ 12 | ≤ 10 | ~20 min |
| `thorough` | A competitor teardown, or a decision that needs the depth | up to 6, in parallel | ≤ 6 per type | ≤ 5 per type | ~30–40 min |

Never extend a budget silently. If the evidence is thin when it runs out, say so in the report
and offer another round after the PM has seen the TL;DR.

## 1. Agree the brief

Propose the whole brief in **one** message, filled in from the request (topic, goal, source
types, depth with its time box, exclusions), and ask the PM to confirm or change it. If the
request already settles all of it, confirm in one line and start.

- **Topic:** the product, feature, competitor set, market or regulation.
- **Goal:** why: pre-PRD discovery, a competitor teardown, testing a hypothesis, user pains,
  a regulatory check.
- **Sources:** the types that answer the goal, no more than the depth allows. Recommend them:
  user pains → 1 and 2; positioning and pricing → 3; a rule → 5.

| # | Source type | Reveals | Misses |
|---|---|---|---|
| 1 | Community: Reddit, Hacker News, forums, X | Unfiltered pains, workarounds, users' own words | Quiet majority; skews to enthusiasts |
| 2 | Reviews: App Store, Google Play, Trustpilot, G2 | Specific praise and complaints, by feature | Depth; review campaigns skew scores |
| 3 | Competitors: product pages, pricing, help centres, release notes | What exists, how it is positioned and priced | Whether users like it |
| 4 | News and analysts | Market moves, launches, funding, trends | User reality; vendor spin |
| 5 | Regulators and official data: regulators' sites, central banks, statistics offices | Rules, licences, official figures | How rules are applied in practice |
| 6 | Research: papers, surveys, industry reports | Systematic data | Recency; often paywalled |

- **Depth:** `quick`, `standard` or `thorough` (the time boxes above).
- **Exclusions:** competitors, regions or angles to leave out.

**Reuse before you search.** Look in `signals/` for research on the same topic from the last 90
days. If there is some, offer to update it (only the gaps it lists, and anything newer than its
date) instead of starting again.

## 2. Search

Use the `web-research` tools in `context/tools.md` (for example Firecrawl as `main` and the AI
tool's own web search as `fallback`), and the `market-data` tools when figures are in scope; if
none is configured, the web search and fetch tools available in this session. If no web tool
answers, stop and say so instead of answering from memory. Every figure you report follows
evidence rule 9: URL, publication date, date read, labelled external.

1. **Plan the queries first.** Write two or three queries per source type: product names,
   category terms, the pain in users' words, competitor names, and site-scoped searches where
   they help (`site:reddit.com <topic>`, `site:apps.apple.com <competitor>`).
2. **Run a source type's searches together,** in one turn, not one after another. Use the
   search tool's normal mode; use a slower, deeper mode only for a query whose results come
   back thin or stale.
3. **Triage from the results.** Pick the pages worth reading from titles, snippets and dates.
   Read only pages you expect to cite, each once. Prefer pages that gather many data points (a
   review listing sorted by most recent, a pricing page, a regulator's notice) over many single
   items. For reviews, read both positive and critical ones. A snippet can decide what to
   read; it is never cited. Only pages you read are sources.
4. **Stop early.** Stop a source type when two pages in a row add nothing new, or its budget is
   used. Stop the search when every theme has sources of at least two types, or 75% of the
   time box has gone: then synthesise with what you have.
5. **Thorough depth runs in parallel.** If your tool can start subagents, start one
   `web-researcher` (`../../agents/web-researcher.md`) per source type, all at once, each
   with the brief, its queries and its share of the budget. Each returns an evidence log;
   you synthesise. If your tool cannot start subagents, run the source types one after another
   with the same budgets.

Keep one evidence log for the whole run (in memory or one scratch file) and write the report
once, at the end: source type, name and URL, date, one or two takeaways, and any quote or
number worth citing. Prefer recent sources unless history is the point, and note every
source's date. Do not use content you were refused or that sits behind a login you were not
given.

## 3. Synthesise

- Find the three to five strongest themes. Name each after the insight ("pricing confusion
  drives switching"), not the topic ("pricing").
- **Count sources** for each theme by type, e.g. `(4 Reddit threads, 9 app reviews, 1 article)`.
  A theme seen across several source types is stronger; one seen in a single source is a
  **weak signal** and is labelled as one.
- Grade the report overall: `strong`, `some` or `hunch` (`evidence-rules.md`).
- Note where sources conflict and where evidence is thin.
- Quote sparingly and exactly, only where the words carry signal.
- Separate fact ("reviewers say…", "the regulator's notice states…") from inference ("this
  suggests…").

## 4. Write the report

`signals/YYYY-MM-DD-research-<topic>.md`:

```
# Research: <topic> (YYYY-MM-DD)
**Goal:** <one sentence> · **Depth:** quick | standard | thorough · **Evidence:** strong | some | hunch
**Budget used:** 11 of 12 searches · 9 of 10 pages · ~18 min (stopped: themes covered | budget | time box)
**Sources read:** 6 Reddit threads, 14 app reviews, 4 competitor sites, 2 articles
**Not reachable:** <anything blocked, paywalled or missing>

## TL;DR
- <3–5 findings a PM could act on; written last>

## Themes
### 1. <insight> (4 threads, 9 reviews, 1 article)
<2–4 sentences>
> "<exact quote>" (<source, date>)

## Competitors            (only if in scope)
| Competitor | Positioning | Strengths (from users) | Weaknesses (from users) | Price |

## Rules and official data (only if in scope)
- <rule or figure> (<source, date>)

## Evidence gaps
- <what was searched for and not found>

## Sources
- <title> — <URL> (<date>)
```

## 5. Hand over

Summarise the TL;DR in chat and suggest one next step: turn a theme into an idea with the
`capture-idea` skill, add the findings to an item's PRD §3.4 and §8, size it with the
`opportunity-brief` skill, or challenge it with the `product-grill` skill.
