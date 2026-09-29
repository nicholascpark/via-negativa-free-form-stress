#!/usr/bin/env bash
# blast-radius.sh — Find every file that depends on the changed interfaces
#
# Answers: "Who is affected by this change that the diff doesn't show?"
#
# Usage:
#   ./blast-radius.sh                          # auto-detect from staged/uncommitted changes
#   ./blast-radius.sh --base main              # diff against a branch
#   ./blast-radius.sh file1.ts file2.ts        # explicit file list

set -euo pipefail

BRANCH=""
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CHANGED_FILES=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --base|--branch) BRANCH="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--base <branch>] [file1 ...]"
            exit 0 ;;
        *) CHANGED_FILES+=("$1"); shift ;;
    esac
done

if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
    if [[ -n "$BRANCH" ]]; then
        mapfile -t CHANGED_FILES < <(git diff --name-only "$BRANCH"...HEAD 2>/dev/null || git diff --name-only "$BRANCH" HEAD)
    else
        mapfile -t CHANGED_FILES < <(git diff --name-only HEAD 2>/dev/null || true)
        if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
            mapfile -t CHANGED_FILES < <(git diff --cached --name-only 2>/dev/null || true)
        fi
    fi
fi

[[ ${#CHANGED_FILES[@]} -eq 0 ]] && { echo "No changed files detected."; exit 0; }

echo "═══════════════════════════════════════════════════"
echo "  BLAST RADIUS ANALYSIS"
echo "═══════════════════════════════════════════════════"
echo ""
echo "Changed files:"
printf '  ✦ %s\n' "${CHANGED_FILES[@]}"
echo ""

# Extract searchable symbols from changed files
declare -A SEARCH_TERMS

for file in "${CHANGED_FILES[@]}"; do
    [[ ! -f "$REPO_ROOT/$file" ]] && continue

    basename_no_ext=$(basename "$file" | sed 's/\.[^.]*$//')
    # Skip overly generic names
    if [[ ${#basename_no_ext} -gt 2 ]] && [[ "$basename_no_ext" != "index" ]] && [[ "$basename_no_ext" != "main" ]]; then
        SEARCH_TERMS["$basename_no_ext"]=1
    fi

    # Extract exported/public symbols
    case "$file" in
        *.ts|*.tsx|*.js|*.jsx)
            while IFS= read -r sym; do
                [[ -n "$sym" ]] && [[ ${#sym} -gt 2 ]] && SEARCH_TERMS["$sym"]=1
            done < <(grep -oP '(?<=export\s+(default\s+)?(function|class|const|let|var|interface|type)\s+)\w+' "$REPO_ROOT/$file" 2>/dev/null || true)
            ;;
        *.py)
            while IFS= read -r sym; do
                [[ -n "$sym" ]] && [[ ${#sym} -gt 2 ]] && SEARCH_TERMS["$sym"]=1
            done < <(grep -oP '(?<=^def\s)\w+|(?<=^class\s)\w+' "$REPO_ROOT/$file" 2>/dev/null || true)
            ;;
        *.go)
            while IFS= read -r sym; do
                [[ -n "$sym" ]] && [[ ${#sym} -gt 2 ]] && SEARCH_TERMS["$sym"]=1
            done < <(grep -oP '(?<=^func\s)[A-Z]\w+|(?<=^type\s)[A-Z]\w+' "$REPO_ROOT/$file" 2>/dev/null || true)
            ;;
    esac
done

if [[ ${#SEARCH_TERMS[@]} -eq 0 ]]; then
    echo "Could not extract searchable symbols from changed files."
    exit 0
fi

echo "Searching for references to: ${!SEARCH_TERMS[*]}"
echo ""

GREP_PATTERN=$(printf '%s\|' "${!SEARCH_TERMS[@]}" | sed 's/\\|$//')

# Import-aware pattern: prioritize real dependencies (import/require/from/use/include)
# over incidental string matches (comments, variable names, docs).
IMPORT_PATTERN="\(import\|require\|from\|use \|include\|#include\).*\(${GREP_PATTERN}\)"

EXCLUDE_DIRS="--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor"
EXCLUDE_DIRS="$EXCLUDE_DIRS --exclude-dir=dist --exclude-dir=build --exclude-dir=__pycache__"
EXCLUDE_DIRS="$EXCLUDE_DIRS --exclude-dir=.next --exclude-dir=target --exclude-dir=venv"

CODE_INCLUDES="--include=*.ts --include=*.tsx --include=*.js --include=*.jsx"
CODE_INCLUDES="$CODE_INCLUDES --include=*.py --include=*.go --include=*.rb --include=*.java"
CODE_INCLUDES="$CODE_INCLUDES --include=*.rs --include=*.c --include=*.cpp --include=*.h"

CONFIG_INCLUDES="--include=*.yaml --include=*.yml --include=*.json --include=*.toml"

# High-confidence: files that import/require the changed symbols
IMPORT_RESULTS=$(eval grep -rl "'$IMPORT_PATTERN'" "'$REPO_ROOT'" $CODE_INCLUDES $EXCLUDE_DIRS 2>/dev/null | sort -u || true)

# Config files: no import statements, so any reference matters
CONFIG_RESULTS=$(eval grep -rl "'$GREP_PATTERN'" "'$REPO_ROOT'" $CONFIG_INCLUDES $EXCLUDE_DIRS 2>/dev/null | sort -u || true)

RESULTS=$(printf '%s\n%s' "$IMPORT_RESULTS" "$CONFIG_RESULTS" | grep -v '^$' | sort -u)

AFFECTED=""
AFFECTED_IMPORT=""
AFFECTED_CONFIG=""
for result in $RESULTS; do
    rel=$(realpath --relative-to="$REPO_ROOT" "$result" 2>/dev/null || echo "$result")
    is_self=false
    for cf in "${CHANGED_FILES[@]}"; do [[ "$rel" == "$cf" ]] && is_self=true && break; done
    $is_self && continue

    # Classify as import-based (high confidence) or config reference
    if echo "$IMPORT_RESULTS" | grep -qF "$result"; then
        AFFECTED_IMPORT="${AFFECTED_IMPORT}${rel}\n"
    else
        AFFECTED_CONFIG="${AFFECTED_CONFIG}${rel}\n"
    fi
    AFFECTED="${AFFECTED}${rel}\n"
done

if [[ -z "$AFFECTED" ]]; then
    echo "No other files reference the changed interfaces."
    echo "Blast radius appears contained."
else
    COUNT=$(echo -e "$AFFECTED" | grep -cv '^$')
    echo "───────────────────────────────────────────────────"
    echo "  BLAST RADIUS: ${COUNT} files outside the diff"
    echo "───────────────────────────────────────────────────"

    if [[ -n "$AFFECTED_IMPORT" ]]; then
        ICOUNT=$(echo -e "$AFFECTED_IMPORT" | grep -cv '^$')
        echo ""
        echo "  Direct dependencies ($ICOUNT files — import/require/use):"
        echo -e "$AFFECTED_IMPORT" | grep -v '^$' | while read -r f; do
            matches=$(grep -oh "$GREP_PATTERN" "$REPO_ROOT/$f" 2>/dev/null | sort -u | head -5 | tr '\n' ', ' | sed 's/,$//')
            echo "  → $f"
            [[ -n "$matches" ]] && echo "    references: $matches"
        done
    fi

    if [[ -n "$AFFECTED_CONFIG" ]]; then
        CCOUNT=$(echo -e "$AFFECTED_CONFIG" | grep -cv '^$')
        echo ""
        echo "  Config/data references ($CCOUNT files):"
        echo -e "$AFFECTED_CONFIG" | grep -v '^$' | while read -r f; do
            echo "  → $f"
        done
    fi

    echo ""
    echo "These files depend on interfaces modified by this change."
    echo "Verify they remain compatible."
fi
