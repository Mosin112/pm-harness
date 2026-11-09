# Connectors: needs, the registry and the preflight

Skills never name a tool. Each one says which **needs** it has (governed metrics, a design
source, an issue tracker…), and `context/tools.md` says which tools serve each need in this
workspace. The same skill then works with Metabase or Looker, Mixpanel or Amplitude, Claude or
Codex, and a team changes a tool in one row instead of in every skill.

## 1. Needs

| Need | What it is for | Typical tools | Usual source |
|---|---|---|---|
| `meeting-notes` | Notes and transcripts: interviews, customer and sales calls, team meetings | Granola, Gong, Otter, Fireflies | internal |
| `team-chat` | Channels where feedback, incidents and decisions are discussed | Slack, Microsoft Teams | internal |
| `support-feedback` | Support tickets, feedback forms, NPS, app reviews | Zendesk, Intercom, Freshdesk; app store reviews (external) | internal |
| `product-analytics` | Events, funnels, retention, cohorts, experiments | Mixpanel, Amplitude, PostHog | internal |
| `governed-metrics` | The governed definition and value of every metric in `context/metrics.md` | Metabase, Looker, a warehouse, a semantic layer | internal |
| `web-research` | Searching and reading the public web | Firecrawl, the AI tool's web search and fetch | external |
| `market-data` | Structured outside data: traffic, downloads, market sizes, prices | Similarweb, Sensor Tower, Statista, a market-data API | external |
| `docs` | Company documents: strategy, specs, research, past PRDs | Confluence, Notion, Google Drive, SharePoint | internal |
| `design-source` | The design system and the current screens | Figma, a brand guide in Google Drive, the app's theme or token files | internal |
| `issue-tracker` | Epics, stories, status and dates | Jira, Linear, GitHub Issues | internal |
| `prd-publishing` | Where stakeholders read PRDs | Confluence (space and parent page), Notion | internal |
| `artifact-sharing` | Sharing prototypes and trees views, with comments | Claude artifacts | internal |
| `calendar` | Finding meetings and attendees | Google Calendar, Outlook | internal |
| `email` | Sending approved updates and follow-ups | Gmail, Outlook | internal |

## 2. The registry: `context/tools.md`

One row per tool, so a need can have several:

| Column | Meaning |
|---|---|
| **Need** | One id from the table above |
| **Tool** | The connector or tool as the PM knows it. Empty means the need has no tool yet |
| **Role** | `main` is used first. `also` is read as well when a task wants coverage (gathering evidence or context). `fallback` is used only when no `main` tool answers |
| **Source** | `internal` (the company's own data) or `external` (the public web, data providers). External numbers follow evidence rule 9 |
| **Trusted for** | What this tool is the source of truth for. When two tools disagree on a number, the one trusted for it wins and the gap is reported |
| **Notes** | Projects, channels, spaces, folders, files: whatever a skill needs to find the right place |

A filled example:

```
| Need | Tool | Role | Source | Trusted for | Notes |
|---|---|---|---|---|---|
| governed-metrics | Metabase | main | internal | every metric in metrics.md | collection "Product KPIs" |
| product-analytics | Mixpanel | main | internal | events, funnels, retention | project "App" |
| product-analytics | Amplitude | also | internal | events before 2025 | |
| web-research | Firecrawl | main | external | | |
| web-research | web search | fallback | external | | built into the AI tool |
| market-data | CoinGecko API | main | external | asset prices and volumes | |
| docs | Confluence | main | internal | specs, past PRDs | space "PROD" |
| docs | Google Drive | also | internal | strategy decks, research | folder "Product" |
| design-source | Figma | main | internal | tokens, components, current screens | file "App design system" |
| design-source | Google Drive | also | internal | brand guide | folder "Brand" |
```

**Using several tools for one need.** When gathering (signals, research, context), read the
`main` and `also` tools and count each source separately (evidence rule 1). For a number, use
the tool trusted for that metric and name it as the source; if two internal tools disagree,
show both and say which one is governed. Never average them.

## 3. Preflight: before a skill starts

1. **Resolve.** Run `python3 .pm-harness/pm_check.py needs <skill>`. It reads the skill's
   `## Needs` block and `context/tools.md` and lists, for each need, whether it is required or
   optional and the tools that serve it in order. A skill with several jobs (`publish`,
   `setup`) checks the needs of the job the PM asked for. If the script cannot find the skill,
   pass the path to its `SKILL.md`, or read the block and the registry yourself.
2. **Confirm each tool answers** with one harmless read call. Never write during a preflight,
   and probe each tool once per session.

   | Need | Probe |
   |---|---|
   | `meeting-notes` | search or list one recent meeting |
   | `team-chat` | search one channel named in Notes |
   | `support-feedback` | read one recent ticket |
   | `product-analytics` | list projects or open one saved report |
   | `governed-metrics` | open one metric definition or dashboard from `metrics.md` |
   | `web-research`, `market-data` | one search or one lookup |
   | `docs`, `prd-publishing` | read the space, folder or parent page in Notes (never create a test page) |
   | `design-source` | read the design file's variables, or list the brand folder |
   | `issue-tracker` | read one issue in the project |
   | `artifact-sharing` | list the PM's artifacts |
   | `calendar` | list today's events |
   | `email` | search one thread (never draft or send) |

3. **Decide.**
   - A **required** need is met when at least one of its tools answers; prefer `main`, and say
     when a fallback is used instead. A line that joins needs (`market-data` or
     `web-research`) is met by either.
   - A required need with no answering tool: before doing the work that needs it, tell the PM
     the need, the tools tried, and the choices: connect a tool, paste or attach the data, or
     carry on with that part marked *not measured* or finished by hand. Then wait.
   - An **optional** need with no answering tool: carry on, and list it under the output's
     *Not reachable* or *Not measured* line (evidence rule 6).
4. **Report in one line** before the work starts, for example:
   `Sources · governed-metrics: Metabase ok · product-analytics: Mixpanel ok, Amplitude not connected · market-data: none configured`

`one-shot` runs the preflight for every step at the start, so a missing tracker shows up
before the PRD is written, not at step 5.

## 4. Suggest, don't bundle

The plugin and the installer ship no connectors: every team's tools and credentials differ.
`setup` compares what the skills need (`pm_check.py needs all`) with what is connected and
suggests what to add for each uncovered need: in Claude, a connector from the directory; in
other tools, an MCP server in that tool's settings. Nothing is installed or authorised without
the PM.

## 5. Writing a Needs block

Every `SKILL.md` has a `## Needs` section that `pm_check.py plugin` checks:

```
## Needs

- `governed-metrics` · required · current values and targets
- `market-data` or `web-research` · optional · external benchmarks, kept apart and labelled
```

Each line is the need ids (several joined by commas or `or` mean "any one of these"), then
`required` or `optional`, then what the skill uses them for. A skill with no outside needs says
`None: works from the workspace files.` A skill that runs others lists them on an `Includes:`
line, and its needs are theirs.
