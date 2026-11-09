---
name: publish
description: Use when the PM wants to publish or share an item's PRD (to Confluence), its prototype or its behaviour-tree view (as a Claude artifact or a link), or wants to pull stakeholders' comments from those places back into the PRD, trees or amendments.
---

# Publish and collect feedback

Stakeholders read the PRD in Confluence and click through the prototype as a Claude artifact.
The workspace files stay the source of truth: publishing copies them out, and feedback comes back
in through change control or `amendments.md`, never by editing the published copy.

Read first: `context/tools.md` (the `prd-publishing` row: Confluence space and parent page;
the `artifact-sharing` row: how prototypes and trees views are shared), `context/stakeholders.md` (who reviews what), and the item's files.

**Every publish writes to an external tool, so show the PM what will be published and where,
and wait for approval.** That includes updating a page that already exists.

## Needs

Before starting, run `python3 .pm-harness/pm_check.py needs publish` and confirm each tool
answers (preflight in `../../reference/connectors.md`).

- `prd-publishing` · required · publishing a PRD and reading its comments (check it only for that
  job)
- `artifact-sharing` · required · publishing a prototype or trees view and reading their comments
  (check it only for that job)

## PRD → Confluence

1. Run `python3 .pm-harness/pm_check.py prd work/<item>/02-prd.md` first; do not publish a PRD
   that fails its check.
2. If the PRD's `Links:` line already has a Confluence URL, this is an update: read the current
   page and its comments first (step 5), so nothing a stakeholder wrote is lost.
3. Convert the PRD to the page body: keep the eight numbered sections, headings, tables and
   section numbers as they are; turn `Tree:` lines into links to the trees (or the trees view
   artifact) and keep the change log at the end. Add one line at the top: *Source of truth:
   PM workspace `work/<item>/02-prd.md`. Comment here; edits to this page are not copied back.*
4. Create the page in the space and under the parent from `context/tools.md` with the
   `prd-publishing` tool (or update it). Title: `<Title> · PRD (<Phase>)`.
5. Record the URL in the PRD's `Links:` line (`Links: Confluence <url> · Prototype <url> ·
   Trees <url>`) and set `Updated:`.

**Pulling Confluence feedback back:** read the page's footer and inline comments. For each one
that asks for a change, propose it under the PRD's change control (`write-prd`, "After
approval"): the exact edit, the section, and the comment as its source. Apply only what the PM
approves, then republish and reply on the comment with what changed. If someone edited the page
body directly, show the PM the difference and treat it the same way: a proposal, not a merge.

## Prototype → Claude artifact

Use this when the tool has Claude's Artifact tool (Claude apps, Claude Code on claude.ai).
Elsewhere, attach `04-prototype/index.html` to the ticket or share the file; it opens from disk.

1. Run `python3 .pm-harness/pm_check.py prototype work/<item>/03-trees work/<item>/04-prototype/index.html`.
2. Make the artifact page: `python3 .pm-harness/pm_check.py artifact work/<item>/04-prototype/index.html work/<item>/04-prototype/artifact.html`.
3. Publish `artifact.html` with the Artifact tool, declaring
   `capabilities: {"comments": {"composer_only": true}}` so the prototype's
   **Comment on this screen** button opens the comment composer. Give it a description naming
   the decision the variants test. Republish to the same URL after every change.
4. Record the URL in the PRD's `Links:` line as `Prototype <url>`, and tell the PM it is private
   until they share it.

**Pulling prototype feedback back:** where this session is notified of comments a reviewer
sends to Claude, act on them as they arrive; where it is not (Claude's cloud sessions, for now),
read the artifact's comment threads with the artifact comments tool when the PM asks. Replies and
resolving work only on threads someone sent to Claude; leave plain comments open and say so. Each comment's
anchor names the screen it was left on: `#screen-<variant>-<screen>` or `#screen-<screen>`. Turn
each into an amendment in `04-prototype/amendments.md` (variant, screen, the reviewer's words,
`From:` the commenter), then run the `review-prototype` skill. Reply on the thread with the
amendment number, and resolve it once the amendment is resolved or dismissed.

## Trees view → Claude artifact

1. Run `python3 .pm-harness/pm_check.py view work/<item>`, which writes
   `work/<item>/03-trees-view.html` (open it from disk in any tool), then
   `python3 .pm-harness/pm_check.py artifact work/<item>/03-trees-view.html work/<item>/03-trees-view.artifact.html`.
2. Publish the `.artifact.html` file with the Artifact tool, declaring
   `capabilities: {"comments": {"composer_only": true}}`, and open it for the PM.
3. Read comments as for the prototype (above). Each comment's anchor is the line's id
   (`functional-<subject>--<words>-<hash>`); the page's `data-tree` and `data-text` for that id
   give the tree and the exact line. Change the tree file (never the view), re-run the trees
   and PRD checks, regenerate the view and republish to the same URL, then reply on the thread
   with what changed and resolve it.
4. Record the URL in the PRD's `Links:` line as `Trees <url>`.

## Finish

Summarise what was published, where, and what feedback was turned into changes or amendments.
Never post the links in chat channels or email without the PM approving the exact message.
