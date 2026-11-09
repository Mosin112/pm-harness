# Tools and connectors

Which tools serve each need in this workspace. Skills name needs, never tools; this file maps
them (`.pm-harness/reference/connectors.md` explains every need and column).

- One row per tool: add a row for each extra tool a need uses (Mixpanel and Amplitude; Confluence,
  Notion and Google Drive).
- **Role:** `main` is used first, `also` is read as well when gathering, `fallback` only when no
  `main` tool answers.
- **Source:** `internal` or `external`. External numbers are benchmarks, never our values.
- Leave **Tool** empty for a need you do not have.

See what a skill needs: `python3 .pm-harness/pm_check.py needs <skill>` (or `needs all`).

| Need | Tool | Role | Source | Trusted for | Notes (projects, channels, spaces, folders) |
|---|---|---|---|---|---|
| meeting-notes | | main | internal | | |
| team-chat | | main | internal | | |
| support-feedback | | main | internal | | |
| product-analytics | | main | internal | | |
| governed-metrics | | main | internal | | |
| web-research | | main | external | | |
| market-data | | main | external | | |
| docs | | main | internal | | |
| design-source | | main | internal | | |
| issue-tracker | | main | internal | | |
| prd-publishing | | main | internal | | Confluence space and parent page |
| artifact-sharing | | main | internal | | |
| calendar | | main | internal | | |
| email | | main | internal | | |
