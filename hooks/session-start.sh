#!/usr/bin/env bash
# PM Harness SessionStart hook.
# In a PM workspace (CLAUDE.md contains the pm-harness-workspace marker) it:
#   1. keeps .pm-harness/pm_check.py in step with the installed plugin, and
#   2. prints the pipeline board so every session starts knowing what is in flight.
# Anywhere else it prints nothing.
set -u

dir="${CLAUDE_PROJECT_DIR:-$PWD}"
[[ -f "$dir/CLAUDE.md" ]] || exit 0
grep -q 'pm-harness-workspace' "$dir/CLAUDE.md" 2>/dev/null || exit 0

if [[ -n "${CLAUDE_PLUGIN_ROOT:-}" && -f "$CLAUDE_PLUGIN_ROOT/scripts/pm_check.py" ]]; then
  mkdir -p "$dir/.pm-harness"
  if ! cmp -s "$CLAUDE_PLUGIN_ROOT/scripts/pm_check.py" "$dir/.pm-harness/pm_check.py"; then
    cp "$CLAUDE_PLUGIN_ROOT/scripts/pm_check.py" "$dir/.pm-harness/pm_check.py"
  fi
fi

next_step() {
  case "$1" in
    idea) echo "write-concept (or opportunity-brief to size it first)" ;;
    concept) echo "write-behaviour-trees" ;;
    trees) echo "build-prototype" ;;
    prototype) echo "create-eng-tickets" ;;
    tickets|building) echo "stakeholder-update; launch-readout after launch" ;;
    launched) echo "done; run update-context if not yet captured" ;;
    parked) echo "parked; see decision log" ;;
    *) echo "unknown stage; check 01-idea.md" ;;
  esac
}

echo "## PM Harness pipeline board"
found=0
for f in "$dir"/work/*/01-idea.md; do
  [[ -f "$f" ]] || continue
  found=1
  item=$(basename "$(dirname "$f")")
  stage=$(sed -n 's/^stage:[[:space:]]*//p' "$f" | head -n 1)
  updated=$(sed -n 's/^updated:[[:space:]]*//p' "$f" | head -n 1)
  printf -- '- %s | stage: %s | updated: %s | next: %s\n' \
    "$item" "${stage:-?}" "${updated:-?}" "$(next_step "${stage:-}")"
done
if [[ $found -eq 0 ]]; then
  echo "- No items yet. Start with /pm-harness:capture-idea or /pm-harness:synthesize-signals."
fi

if [[ -d "$dir/context" ]]; then
  stale=$(find "$dir/context" -name '*.md' -mtime +90 2>/dev/null | sed "s|^$dir/||" | tr '\n' ' ')
  if [[ -n "$stale" ]]; then
    echo "Context files not updated in 90+ days (offer to review them): $stale"
  fi
fi

echo "Reminders: follow CLAUDE.md and the evidence rules; never write to an external tool without the PM's approval."
exit 0
