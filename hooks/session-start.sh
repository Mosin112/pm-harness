#!/usr/bin/env bash
# PM Harness SessionStart hook (Claude Code plugin).
# In a PM workspace (AGENTS.md or CLAUDE.md contains the pm-harness-workspace marker) it:
#   1. keeps .pm-harness/ (checker, reference files, reviewer definitions) in step with the
#      installed plugin, so every tool working in the workspace uses the same version, and
#   2. prints the pipeline board so every session starts knowing what is in flight.
# Anywhere else it prints nothing.
set -u

dir="${CLAUDE_PROJECT_DIR:-$PWD}"
grep -qs 'pm-harness-workspace' "$dir/AGENTS.md" "$dir/CLAUDE.md" || exit 0

root="${CLAUDE_PLUGIN_ROOT:-}"
if [[ -n "$root" && -f "$root/scripts/pm_check.py" ]]; then
  mkdir -p "$dir/.pm-harness/reference" "$dir/.pm-harness/agents"
  sync() { cmp -s "$1" "$2" || cp "$1" "$2"; }
  sync "$root/scripts/pm_check.py" "$dir/.pm-harness/pm_check.py"
  for f in "$root"/reference/*.md; do sync "$f" "$dir/.pm-harness/reference/$(basename "$f")"; done
  for f in "$root"/agents/*.md; do sync "$f" "$dir/.pm-harness/agents/$(basename "$f")"; done
fi

checker="$dir/.pm-harness/pm_check.py"
if command -v python3 >/dev/null 2>&1 && [[ -f "$checker" ]]; then
  python3 "$checker" board "$dir"
else
  echo "## PM Harness"
  echo "Python 3 is needed for the pipeline board and checks. Install it, then run the setup skill in repair mode."
fi
exit 0
