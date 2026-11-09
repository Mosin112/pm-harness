#!/usr/bin/env bash
# Self-test: the worked example must pass every gate, the generators must reproduce what is
# committed, and known-bad drafts must fail.
set -euo pipefail
cd "$(dirname "$0")/.."
C="python3 scripts/pm_check.py"
E=examples/price-alerts
F=tests/fixtures

$C plugin .
$C workspace templates/workspace
$C prd $E/02-prd.md $E/03-trees
$C trees $E/03-trees
$C prototype $E/03-trees $E/04-prototype/index.html
$C tickets $E/03-trees $E/05-tickets.md $E/02-prd.md
$C item $E | tail -n 1
$C board templates/workspace >/dev/null
$C design templates/workspace/DESIGN.md >/dev/null
$C needs one-shot --tools $F/tools.md >/dev/null
$C needs all --tools $F/tools.md | grep -q 'required  issue-tracker .*Jira (main)' \
  || { echo "FAIL  needs all does not resolve issue-tracker from the registry"; exit 1; }
$C needs launch-readout --tools $F/legacy-tools.md | grep -q 'Mixpanel (main), Amplitude (also)' \
  || { echo "FAIL  needs does not read a 0.4 tools.md"; exit 1; }
echo "PASS  needs resolves skills against the tools registry (new and 0.4 formats)"
if $C prototype $E/03-trees $E/04-prototype/index.html | grep -q '^  ! '; then
  echo "FAIL  the worked example prototype has craft or coverage warnings"; exit 1
fi
echo "PASS  worked example prototype has no warnings"

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

# generators: the committed view and contracts are exactly what the checker produces
cp -r $E "$tmp/price-alerts"
rm -rf "$tmp/price-alerts/05-contracts" "$tmp/price-alerts/03-trees-view.html"
$C view "$tmp/price-alerts" >/dev/null
$C contracts "$tmp/price-alerts" >/dev/null
diff -q "$tmp/price-alerts/03-trees-view.html" $E/03-trees-view.html >/dev/null \
  || { echo "FAIL  03-trees-view.html is stale: run pm_check.py view $E"; exit 1; }
diff -rq "$tmp/price-alerts/05-contracts" $E/05-contracts >/dev/null \
  || { echo "FAIL  05-contracts/ is stale: run pm_check.py contracts $E"; exit 1; }
echo "PASS  trees view and contracts are up to date"

# the prototype runtime is the same in the shell template and the worked example
runtime() { python3 -c "import re,sys; print(re.search(r'<script id=\"pm-runtime\">.*?</script>', open(sys.argv[1]).read(), re.S).group(0))" "$1"; }
[[ "$(runtime templates/prototype/index.html)" == "$(runtime $E/04-prototype/index.html)" ]] \
  || { echo "FAIL  the pm-runtime script differs between the shell and the example"; exit 1; }
echo "PASS  prototype runtime matches the shell template"

# artifact fragments carry no document skeleton
$C artifact $E/04-prototype/index.html "$tmp/proto.artifact.html" >/dev/null
if grep -qiE '<!doctype|<html|<body' "$tmp/proto.artifact.html"; then
  echo "FAIL  artifact fragment still has a document skeleton"; exit 1
fi
echo "PASS  artifact fragment has no document skeleton"

expect_fail() {
  local what="$1"; shift
  if "$@" >/dev/null; then echo "FAIL  the checker accepted $what"; exit 1; fi
  echo "PASS  checker rejects $what"
}
sed '/^## Definition of done/,$d' $E/05-tickets.md > "$tmp/tickets-no-dod.md"
grep -v 'alert adoption' $E/05-tickets.md > "$tmp/tickets-no-metric.md"
sed 's/"chosen": "guided",/"chosen": "quick",/' $E/04-prototype/index.html > "$tmp/price-alerts/04-prototype/index.html"

expect_fail "a known-bad tree" $C trees $F/bad-trees
expect_fail "a DESIGN.md with broken token references and section order" $C design $F/bad-design.md
expect_fail "a known-bad PRD" $C prd $F/bad-prd.md $E/03-trees
expect_fail "a prototype missing a variant's screen and with open amendments" \
  $C prototype $E/03-trees $F/bad-prototype/index.html
expect_fail "a manifest whose chosen variant disagrees with the PRD" \
  $C prototype $E/03-trees "$tmp/price-alerts/04-prototype/index.html"
expect_fail "tickets without a Definition of done" $C tickets $E/03-trees "$tmp/tickets-no-dod.md"
expect_fail "tickets that miss a PRD metric" $C tickets $E/03-trees "$tmp/tickets-no-metric.md" $E/02-prd.md

expect_fail "a tools registry with an unknown need, role and source" \
  $C needs metrics-review --tools $F/bad-tools.md
expect_fail "a required need with no tool" $C needs create-eng-tickets --tools templates/workspace/context/tools.md
mkdir -p "$tmp/skill/skills/broken"
printf -- '---\nname: broken\ndescription: Use when testing.\n---\n# Broken\n\n## Needs\n\n- `analytics` · required · nothing\n' \
  > "$tmp/skill/skills/broken/SKILL.md"
{ $C needs broken --skills "$tmp/skill/skills" --tools $F/tools.md || true; } | grep -q "unknown need 'analytics'" \
  || { echo "FAIL  needs accepted a skill that names an unknown need"; exit 1; }
echo "PASS  checker rejects a skill whose Needs block names an unknown need"

bash -n hooks/session-start.sh && echo "PASS  hook script syntax"
echo "All self-tests passed."
