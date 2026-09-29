#!/usr/bin/env bash
# trajectory.sh — Track complexity trajectory of changed files
#
# Shows how file size has evolved over recent commits.
# Detects "complexity creep" — files that keep growing without refactoring.
# Answers: "Is this the Nth PR adding complexity without anyone stopping to refactor?"
#
# Usage:
#   ./trajectory.sh                            # auto-detect from HEAD~1
#   ./trajectory.sh --base main                # diff against a branch
#   ./trajectory.sh file1.py                   # explicit file list

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
BOLD='\033[1m'
NC='\033[0m'

BASE_BRANCH=""
SNAPSHOTS=8
CHANGED_FILES=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --base) BASE_BRANCH="$2"; shift 2 ;;
        --snapshots) SNAPSHOTS="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: trajectory.sh [--base <branch>] [--snapshots N] [file1 ...]"
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

echo -e "${CYAN}${BOLD}=== Complexity Trajectory ===${NC}"
echo ""

GROWING_FILES=()

for file in "${CHANGED_FILES[@]}"; do
    echo -e "${YELLOW}--- $file ---${NC}"

    mapfile -t COMMITS < <(git log --format='%H' -- "$file" 2>/dev/null | head -100)

    if [[ ${#COMMITS[@]} -lt 2 ]]; then
        echo "  (not enough history)"; echo ""; continue
    fi

    TOTAL=${#COMMITS[@]}
    STEP=$(( TOTAL / SNAPSHOTS ))
    [[ $STEP -lt 1 ]] && STEP=1

    SIZES=()
    LABELS=()

    for (( i=TOTAL-1; i>=0; i-=STEP )); do
        COMMIT="${COMMITS[$i]}"
        LINES=$(git show "$COMMIT:$file" 2>/dev/null | wc -l | tr -d ' ' || echo "0")
        DATE=$(git log -1 --format='%cd' --date=short "$COMMIT" 2>/dev/null)
        SIZES+=("$LINES")
        LABELS+=("$DATE")
    done

    # Current state
    if [[ -f "$file" ]]; then
        SIZES+=("$(wc -l < "$file" | tr -d ' ')")
        LABELS+=("now")
    fi

    # Display
    MAX=1
    for s in "${SIZES[@]}"; do [[ $s -gt $MAX ]] && MAX=$s; done

    for (( j=0; j<${#SIZES[@]}; j++ )); do
        SIZE=${SIZES[$j]}
        BAR_LEN=$(( SIZE * 40 / (MAX > 0 ? MAX : 1) ))
        [[ $BAR_LEN -lt 1 ]] && BAR_LEN=1
        BAR=$(printf '%0.s█' $(seq 1 $BAR_LEN))
        printf "  %s  %4d %s\n" "${LABELS[$j]}" "$SIZE" "$BAR"
    done

    # Growth assessment
    if [[ ${#SIZES[@]} -ge 2 ]]; then
        FIRST=${SIZES[0]}
        LAST=${SIZES[-1]}
        if [[ $FIRST -gt 0 ]]; then
            GROWTH=$(( (LAST - FIRST) * 100 / FIRST ))
            if [[ $GROWTH -gt 50 ]]; then
                echo -e "  ${RED}↑ ${GROWTH}% growth — complexity creep${NC}"
                GROWING_FILES+=("$file (+${GROWTH}%)")
            elif [[ $GROWTH -gt 20 ]]; then
                echo -e "  ${YELLOW}↑ ${GROWTH}% growth${NC}"
            elif [[ $GROWTH -lt -20 ]]; then
                echo -e "  ${GREEN}↓ ${GROWTH}% — simplifying${NC}"
            else
                echo -e "  ~ stable (${GROWTH}%)"
            fi
        fi
    fi
    echo ""
done

if [[ ${#GROWING_FILES[@]} -gt 0 ]]; then
    echo -e "${RED}${BOLD}Complexity creep detected:${NC}"
    for f in "${GROWING_FILES[@]}"; do echo -e "  ${RED}!${NC} $f"; done
    echo ""
    echo -e "${YELLOW}Ask: Should this area be refactored before adding more complexity?${NC}"
fi
