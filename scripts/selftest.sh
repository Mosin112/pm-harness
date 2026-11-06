#!/usr/bin/env bash
# Self-test: the example must pass every gate, and a known-bad draft must fail.
set -euo pipefail
cd "$(dirname "$0")/.."
C="python3 scripts/pm_check.py"
E=examples/price-alerts
$C plugin .
$C workspace templates/workspace
$C trees $E/03-trees
$C prototype $E/03-trees $E/04-prototype/index.html
$C tickets $E/03-trees $E/05-tickets.md
if $C trees tests/fixtures/bad-trees >/dev/null; then
  echo "FAIL  the checker accepted a known-bad tree"; exit 1
fi
echo "PASS  checker rejects the known-bad tree"
bash -n hooks/session-start.sh && echo "PASS  hook script syntax"
echo "All self-tests passed."
