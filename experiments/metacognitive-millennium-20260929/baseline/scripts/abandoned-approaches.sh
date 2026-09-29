#!/usr/bin/env bash
# abandoned-approaches.sh — Find reverted or abandoned work on changed files
#
# Searches git history for reverts, WIP commits, and large deletions that
# touched the same files this PR modifies.
# Answers: "What did previous engineers try and abandon here?"
#
# Usage:
#   ./abandoned-approaches.sh                  # auto-detect from HEAD~1
#   ./abandoned-approaches.sh --base main      # diff against a branch
#   ./abandoned-approaches.sh file1.py         # explicit file list

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

BASE_BRANCH=""
CHANGED_FILES=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --base) BASE_BRANCH="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: abandoned-approaches.sh [--base <branch>] [file1 ...]"
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

[[ ${#CHANGED_FILES[@]} -eq 0 ]] && { echo "No changed files detected."; exit 1; }

echo -e "${CYAN}${BOLD}=== Abandoned Approaches Analysis ===${NC}"
echo ""

TOTAL_REVERTS=0
TOTAL_WIP=0

for file in "${CHANGED_FILES[@]}"; do
    echo -e "${YELLOW}--- $file ---${NC}"
    FOUND=0

    # 1. Explicit reverts
    REVERTS=$(git log --oneline --all --grep="[Rr]evert" -- "$file" 2>/dev/null || true)
    if [[ -n "$REVERTS" ]]; then
        echo -e "  ${RED}Reverted commits:${NC}"
        while IFS= read -r line; do
            echo "    $line"
            FOUND=$((FOUND + 1))
            TOTAL_REVERTS=$((TOTAL_REVERTS + 1))
        done <<< "$REVERTS"
    fi

    # 2. WIP / experimental commits
    EXPERIMENTS=$(git log --oneline --all -- "$file" 2>/dev/null | grep -iE 'wip|temp|experiment|try |attempt|hack|fixup' | head -10 || true)
    if [[ -n "$EXPERIMENTS" ]]; then
        echo -e "  ${YELLOW}Experimental/WIP commits:${NC}"
        while IFS= read -r line; do
            echo "    $line"
            FOUND=$((FOUND + 1))
            TOTAL_WIP=$((TOTAL_WIP + 1))
        done <<< "$EXPERIMENTS"
    fi

    # 3. Large deletions (>50 lines removed, more than 2x additions)
    BIG_DELETES=$(git log --oneline --numstat -- "$file" 2>/dev/null | \
        awk 'NF==1 { msg=$0; next } /^[0-9]/ { if ($2+0 > 50 && $2+0 > ($1+0)*2) print msg" ("$2" lines deleted)"}' | \
        head -5 || true)
    if [[ -n "$BIG_DELETES" ]]; then
        echo -e "  ${YELLOW}Large deletions (possible abandoned code):${NC}"
        while IFS= read -r line; do
            echo "    $line"
            FOUND=$((FOUND + 1))
        done <<< "$BIG_DELETES"
    fi

    [[ $FOUND -eq 0 ]] && echo "  (no abandoned approaches found)"
    echo ""
done

echo -e "${CYAN}${BOLD}=== Summary ===${NC}"
echo "Explicit reverts:       $TOTAL_REVERTS"
echo "WIP/experimental:       $TOTAL_WIP"
echo ""

if [[ $TOTAL_REVERTS -gt 0 || $TOTAL_WIP -gt 0 ]]; then
    echo -e "${YELLOW}Questions to surface:${NC}"
    echo "  - Does the PR explain why previous approaches were abandoned?"
    echo "  - Is the current approach avoiding the same pitfalls?"
    echo "  - Would the next engineer know about the failed attempts?"
fi
