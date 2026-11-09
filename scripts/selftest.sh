#!/usr/bin/env bash
# Self-test: the worked example must pass every gate, and known-bad drafts must fail.
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
$C tickets $E/03-trees $E/05-tickets.md
$C board templates/workspace >/dev/null

expect_fail() {
  local what="$1"; shift
  if "$@" >/dev/null; then echo "FAIL  the checker accepted $what"; exit 1; fi
  echo "PASS  checker rejects $what"
}
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
sed '/^## Definition of done/,$d' $E/05-tickets.md > "$tmp/tickets-no-dod.md"

expect_fail "a known-bad tree" $C trees $F/bad-trees
expect_fail "a known-bad PRD" $C prd $F/bad-prd.md $E/03-trees
expect_fail "a prototype missing a variant's screen and with open amendments" \
  $C prototype $E/03-trees $F/bad-prototype/index.html
expect_fail "tickets without a Definition of done" $C tickets $E/03-trees "$tmp/tickets-no-dod.md"

bash -n hooks/session-start.sh && echo "PASS  hook script syntax"
echo "All self-tests passed."
