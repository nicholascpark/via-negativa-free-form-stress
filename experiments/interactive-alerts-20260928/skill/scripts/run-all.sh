#!/usr/bin/env bash
# run-all.sh — Run the full via negativa investigation suite
#
# Executes all investigation scripts in sequence.
#
# Usage:
#   ./run-all.sh                      # auto-detect from HEAD~1
#   ./run-all.sh --base main          # diff against a branch
#   ./run-all.sh file1.py file2.ts    # explicit file list

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║     VIA NEGATIVA STRESS TEST - INVESTIGATION      ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}${BOLD}[1/5] Blast Radius${NC}"
echo "────────────────────────────────────────"
bash "$SCRIPT_DIR/blast-radius.sh" "$@" 2>&1 || echo "(error)"
echo ""

echo -e "${CYAN}${BOLD}[2/5] Churn Report${NC}"
echo "────────────────────────────────────────"
bash "$SCRIPT_DIR/churn-report.sh" "$@" 2>&1 || echo "(error)"
echo ""

echo -e "${CYAN}${BOLD}[3/5] Abandoned Approaches${NC}"
echo "────────────────────────────────────────"
bash "$SCRIPT_DIR/abandoned-approaches.sh" "$@" 2>&1 || echo "(error)"
echo ""

echo -e "${CYAN}${BOLD}[4/5] Complexity Trajectory${NC}"
echo "────────────────────────────────────────"
bash "$SCRIPT_DIR/trajectory.sh" "$@" 2>&1 || echo "(error)"
echo ""

echo -e "${CYAN}${BOLD}[5/5] Co-Change Gaps${NC}"
echo "────────────────────────────────────────"
bash "$SCRIPT_DIR/co-change-gaps.sh" "$@" 2>&1 || echo "(error)"
echo ""

echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║              INVESTIGATION COMPLETE                ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Feed these results into the via negativa stress test (SKILL.md)"
echo "for Layer 1-4 analysis with full system context."
