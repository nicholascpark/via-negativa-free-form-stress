#!/usr/bin/env bash
# co-change-gaps.sh — Find files that usually change together but weren't changed
#
# Analyzes git history to find files that have historically been modified in the
# same commits as the PR's changed files, but are missing from this PR.
# This is the highest-value script: co-change violations are invisible to
# reasoning alone — you need the history to see them.
# Answers: "What usually gets updated alongside this but was missed?"
#
# Usage:
#   ./co-change-gaps.sh                        # auto-detect from HEAD~1
#   ./co-change-gaps.sh --base main            # diff against a branch
#   ./co-change-gaps.sh --threshold 0.3        # co-change frequency threshold
#   ./co-change-gaps.sh file1.py               # explicit file list

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

BASE_BRANCH=""
THRESHOLD="0.3"  # Files that co-change >30% of the time
LOOKBACK=200     # Number of commits to analyze
CHANGED_FILES=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --base) BASE_BRANCH="$2"; shift 2 ;;
        --threshold) THRESHOLD="$2"; shift 2 ;;
        --lookback) LOOKBACK="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: co-change-gaps.sh [--base <branch>] [--threshold 0.3] [file1 ...]"
            echo "Find files that usually change together but are missing from this PR."
            echo ""
            echo "Options:"
            echo "  --threshold N   Co-change frequency threshold (default: 0.3 = 30%)"
            echo "  --lookback N    Number of commits to analyze (default: 200)"
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

echo -e "${CYAN}${BOLD}=== Co-Change Gap Analysis ===${NC}"
echo -e "Threshold: files that co-change >${THRESHOLD} of the time"
echo -e "Lookback:  last $LOOKBACK commits"
echo ""

# Build co-change map
# For each changed file, find all commits that touched it, then count
# how often each other file appears in those same commits

declare -A GAPS
TOTAL_GAPS=0

for file in "${CHANGED_FILES[@]}"; do
    echo -e "${YELLOW}--- $file ---${NC}"

    # Get commits that touched this file
    mapfile -t FILE_COMMITS < <(git log --format='%H' -n "$LOOKBACK" -- "$file" 2>/dev/null)

    if [[ ${#FILE_COMMITS[@]} -lt 3 ]]; then
        echo "  (not enough commit history to establish co-change patterns)"
        echo ""; continue
    fi

    FILE_COMMIT_COUNT=${#FILE_COMMITS[@]}

    # Count co-occurring files across these commits
    declare -A COCHANGE_COUNT
    for commit in "${FILE_COMMITS[@]}"; do
        while IFS= read -r cofile; do
            [[ "$cofile" == "$file" ]] && continue
            [[ -z "$cofile" ]] && continue
            COCHANGE_COUNT["$cofile"]=$(( ${COCHANGE_COUNT["$cofile"]:-0} + 1 ))
        done < <(git diff-tree --no-commit-id --name-only -r "$commit" 2>/dev/null)
    done

    # Find files above threshold that are NOT in the PR
    FOUND=0
    for cofile in "${!COCHANGE_COUNT[@]}"; do
        COUNT=${COCHANGE_COUNT["$cofile"]}
        FREQ=$(echo "scale=2; $COUNT / $FILE_COMMIT_COUNT" | bc 2>/dev/null || echo "0")

        # Check if above threshold
        ABOVE=$(echo "$FREQ >= $THRESHOLD" | bc 2>/dev/null || echo "0")
        [[ "$ABOVE" != "1" ]] && continue

        # Check if file exists and is NOT in the PR
        [[ ! -f "$cofile" ]] && continue
        IN_PR=0
        for cf in "${CHANGED_FILES[@]}"; do
            [[ "$cofile" == "$cf" ]] && { IN_PR=1; break; }
        done
        [[ $IN_PR -eq 1 ]] && continue

        # This is a gap
        PCT=$(echo "scale=0; $FREQ * 100 / 1" | bc 2>/dev/null || echo "?")
        echo -e "  ${RED}!${NC} $cofile — co-changes ${PCT}% of the time ($COUNT/$FILE_COMMIT_COUNT commits)"
        GAPS["$cofile"]="$PCT"
        FOUND=$((FOUND + 1))
        TOTAL_GAPS=$((TOTAL_GAPS + 1))
    done

    unset COCHANGE_COUNT

    [[ $FOUND -eq 0 ]] && echo "  (no co-change gaps — PR file set looks complete)"
    echo ""
done

echo -e "${CYAN}${BOLD}=== Summary ===${NC}"
echo "Co-change gaps found: $TOTAL_GAPS"
echo ""

if [[ $TOTAL_GAPS -gt 0 ]]; then
    echo -e "${RED}${BOLD}Files that historically change with these files but are missing:${NC}"
    # Sort by frequency
    for f in "${!GAPS[@]}"; do
        echo -e "  ${RED}!${NC} $f (${GAPS[$f]}%)"
    done | sort -t'(' -k2 -rn

    echo ""
    echo -e "${YELLOW}${BOLD}These are the highest-confidence findings.${NC}"
    echo -e "${YELLOW}If a file historically changes alongside what you modified but isn't"
    echo -e "in this PR, either:${NC}"
    echo -e "  1. The PR is incomplete (most common)"
    echo -e "  2. The coupling has been intentionally broken (document why)"
    echo -e "  3. The historical pattern was accidental (verify)"
fi
