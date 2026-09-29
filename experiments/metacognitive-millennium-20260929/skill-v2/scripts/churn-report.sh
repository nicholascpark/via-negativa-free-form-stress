#!/usr/bin/env bash
set -euo pipefail

# churn-report.sh — Identify fragile, frequently-changed areas
#
# Shows commit frequency, distinct authors, and velocity on changed files.
# High churn = fragile area that keeps getting patched.
# Answers: "Is this a fragile area that keeps getting patched?"
#
# Usage:
#   ./churn-report.sh                          # auto-detect from staged/uncommitted changes
#   ./churn-report.sh --base main              # diff against a branch
#   ./churn-report.sh file1.py file2.ts        # explicit file list

if ! git rev-parse --show-toplevel &>/dev/null; then
    echo "Error: not inside a git repository."; exit 1
fi

cd "$(git rev-parse --show-toplevel)"

BASE_BRANCH=""
CHANGED_FILES=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --base) BASE_BRANCH="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: churn-report.sh [--base <branch>] [file1 ...]"
            exit 0 ;;
        *) CHANGED_FILES+=("$1"); shift ;;
    esac
done

if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
    if [[ -n "$BASE_BRANCH" ]]; then
        mapfile -t CHANGED_FILES < <(git diff --name-only "$BASE_BRANCH"...HEAD 2>/dev/null)
    else
        mapfile -t CHANGED_FILES < <(git diff --cached --name-only 2>/dev/null)
        [[ ${#CHANGED_FILES[@]} -eq 0 ]] && mapfile -t CHANGED_FILES < <(git diff --name-only HEAD~1 2>/dev/null)
    fi
fi

[[ ${#CHANGED_FILES[@]} -eq 0 ]] && { echo "No changed files detected."; exit 0; }

echo "═══════════════════════════════════════════════════════"
echo "  CHURN REPORT"
echo "═══════════════════════════════════════════════════════"
echo ""

FLAGS=""

for FILE in "${CHANGED_FILES[@]}"; do
    if ! git log --oneline -1 -- "$FILE" &>/dev/null; then
        echo "  ⚠ $FILE — no git history (new file?)"
        echo ""
        continue
    fi

    echo "┌─────────────────────────────────────────────────────"
    echo "│ $FILE"
    echo "└─────────────────────────────────────────────────────"

    TOTAL=$(git log --oneline -- "$FILE" | wc -l | tr -d ' ')
    RECENT=$(git log --oneline --since="90 days ago" -- "$FILE" | wc -l | tr -d ' ')
    MONTH=$(git log --oneline --since="30 days ago" -- "$FILE" | wc -l | tr -d ' ')
    AUTHORS=$(git log --format="%aN" -- "$FILE" | sort -u | grep -c . || echo 0)
    RECENT_AUTHORS=$(git log --format="%aN" --since="90 days ago" -- "$FILE" | sort -u | grep -c . || echo 0)
    LAST_MOD=$(git log -1 --format="%ar" -- "$FILE")

    echo "  Total commits:    $TOTAL"
    echo "  Last 90 days:     $RECENT commits"
    echo "  Last 30 days:     $MONTH commits"
    echo "  Authors:          $AUTHORS (all time), $RECENT_AUTHORS (90 days)"
    echo "  Last modified:    $LAST_MOD"
    echo ""

    if [ "$RECENT" -ge 8 ]; then
        echo "  🔴 HIGH CHURN — $RECENT changes in 90 days."
        echo "     This area is being patched frequently. Consider whether"
        echo "     the underlying design needs attention, not just another fix."
        echo ""
        FLAGS="${FLAGS}HIGH "
    elif [ "$RECENT" -ge 4 ]; then
        echo "  🟡 MODERATE CHURN — $RECENT changes in 90 days."
        echo ""
        FLAGS="${FLAGS}MOD "
    fi

    echo "  Recent commits:"
    git log --oneline --since="90 days ago" -10 -- "$FILE" | sed 's/^/    /'
    RC=$(git log --oneline --since="90 days ago" -- "$FILE" | wc -l | tr -d ' ')
    [ "$RC" -gt 10 ] && echo "    ... and $((RC - 10)) more"
    echo ""
done

echo "═══════════════════════════════════════════════════════"
echo "  SUMMARY"
echo "═══════════════════════════════════════════════════════"
if echo "$FLAGS" | grep -q "HIGH"; then
    echo "  ⚠ High-churn files detected. This PR touches code that"
    echo "  changes frequently — structural attention may be needed."
elif echo "$FLAGS" | grep -q "MOD"; then
    echo "  Moderate churn detected. Worth monitoring."
else
    echo "  No unusual churn."
fi
echo ""
