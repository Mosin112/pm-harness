---
name: desktop-research
description: Use when the user wants to research a product, feature, competitor, market or regulation on the web, asks "what do people say about X", "how do competitors do X", "look into X" or wants market evidence before writing a PRD. Runs scoped web research and writes an evidence-counted research report with cited sources and stated gaps.
---

# Desktop research

Builds a factual, cited view of a product, feature, competitor set, market or rule from the
public web, ready to feed `capture-idea`, `opportunity-brief` or PRD §3. Read
`../../reference/evidence-rules.md` first; web evidence follows the same rules as customer
evidence.

## 1. Agree the brief

Ask for whatever is missing, in one message:

- **Topic:** the product, feature, competitor set, market or regulation.
- **Goal:** why: pre-PRD discovery, a competitor teardown, testing a hypothesis, user pains,
  a regulatory check.
- **Sources:** pick from the menu (default 1–4):

| # | Source type | Reveals | Misses |
|---|---|---|---|
| 1 | Community: Reddit, Hacker News, forums, X | Unfiltered pains, workarounds, users' own words | Quiet majority; skews to enthusiasts |
| 2 | Reviews: App Store, Google Play, Trustpilot, G2 | Specific praise and complaints, by feature | Depth; review campaigns skew scores |
| 3 | Competitors: product pages, pricing, help centres, release notes | What exists, how it is positioned and priced | Whether users like it |
| 4 | News and analysts | Market moves, launches, funding, trends | User reality; vendor spin |
| 5 | Regulators and official data: regulators' sites, central banks, statistics offices | Rules, licences, official figures | How rules are applied in practice |
| 6 | Research: papers, surveys, industry reports | Systematic data | Recency; often paywalled |

- **Depth:** quick scan (3–5 sources) or thorough (8–12+).
- **Exclusions:** competitors, regions or angles to leave out.

Do not start searching until the PM confirms the brief.

## 2. Search

Use the web tool listed for research in `context/tools.md` (for example a Firecrawl connector);
otherwise the web search and fetch tools available in this session. If no web tool is
available, stop and say so instead of answering from memory.

- Run several targeted queries per source type, varying the wording: product names, category
  terms, the pain in users' words, competitor names. Use site-scoped searches where they help
  (`site:reddit.com <topic>`, `site:apps.apple.com <competitor>`).
- For reviews, read both positive and critical ones.
- Prefer recent sources unless history is the point; note every source's date.
- Read the page itself before citing it; a search snippet is not a source.
- Keep an evidence log as you go: source type, name and URL, date, one or two takeaways, and
  any quote or number worth citing.
- Do not use content you were refused or that sits behind a login you were not given.

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
**Goal:** <one sentence> · **Depth:** quick | thorough · **Evidence:** strong | some | hunch
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
