#!/usr/bin/env bash
# One-command entry point for the high-ticket dropshipping research pipeline.
#
# It bootstraps everything in order, so you only run ONE command:
#   1. resolves a runner (installed `niche-research`, else `uv run` which
#      installs the Python deps on first call — no manual pip/venv),
#   2. checks the engine + your Claude login (free, no tokens),
#   3. then either:
#        • SUGGESTS high-ticket products to research   (no niche given), or
#        • RUNS a full validation brief                (niche given).
#
# Usage:
#   ./research.sh                              # suggest high-ticket product ideas
#   ./research.sh "ergonomic standing desks"   # full opportunity brief for a niche
#   ./research.sh --suggest "home gym"         # focused product discovery
#
# Auth: uses your Claude Pro/Max subscription by default (the engine reuses the
# Claude Code CLI login). It only bills the API if ANTHROPIC_API_KEY is set.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_DIR="${CLAUDE_PLUGIN_ROOT:-$SCRIPT_DIR}/engine"
[[ -d "$ENGINE_DIR" ]] || ENGINE_DIR="$SCRIPT_DIR/engine"

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m%s\033[0m\n' "$*" 1>&2; exit 1; }

# 1. Resolve a runner. Prefer an installed CLI; else uv (auto-installs deps).
if command -v niche-research >/dev/null 2>&1; then
  run() { niche-research "$@"; }
elif command -v uv >/dev/null 2>&1; then
  run() { uv run --project "$ENGINE_DIR" niche-research "$@"; }
else
  die "Need 'uv' (or the niche-research CLI). Install it:  brew install uv"
fi

# 2. Preflight: verify install + login (free, no tokens, no API call).
bold "[1/3] Checking engine + Claude login…"
if ! run verify; then
  die "Not ready. If this is a login issue, run:  claude /login   (choose Pro/Max), then re-run this command."
fi

# 3. Decide mode from the arguments.
ARG1="${1:-}"
if [[ -z "$ARG1" ]]; then
  MODE="suggest"; SEED=""
elif [[ "$ARG1" == "--suggest" || "$ARG1" == "-s" || "$ARG1" == "suggest" ]]; then
  MODE="suggest"; SEED="${2:-}"
else
  MODE="run"; NICHE="$ARG1"
fi

# 4. Run it.
if [[ "$MODE" == "suggest" ]]; then
  bold "[2/3] Discovering high-ticket products…"
  if [[ -n "$SEED" ]]; then run suggest "$SEED"; else run suggest; fi
  bold "[3/3] Done. Validate any idea with:  ./research.sh \"<product>\""
else
  bold "[2/3] Validating niche: $NICHE …"
  run run "$NICHE"
  bold "[3/3] Done. Brief saved under ~/niche-research/briefs/"
fi
