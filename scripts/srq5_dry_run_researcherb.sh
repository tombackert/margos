#!/usr/bin/env bash

set -euo pipefail

PLATFORM_DIR="${PLATFORM_DIR:-$HOME/Repos/marl-platform}"
ATZ_DIR="${ATZ_DIR:-$HOME/Repos/ArgosToZoo}"
VENV_DIR="${VENV_DIR:-$HOME/.venvs/srq5}"
CURRENT_USER="$(id -un)"
NORMALIZED_USER="$(printf '%s' "$CURRENT_USER" | tr '[:upper:]' '[:lower:]')"
EXPECTED_USER="${EXPECTED_USER:-$NORMALIZED_USER}"

if [[ "$NORMALIZED_USER" != "$EXPECTED_USER" ]]; then
  echo "This script is intended to run as the '$EXPECTED_USER' macOS user."
  echo "Current user: $CURRENT_USER"
  exit 1
fi

if [[ ! -d "$PLATFORM_DIR" ]]; then
  echo "Platform repo not found: $PLATFORM_DIR"
  exit 1
fi

if [[ ! -d "$ATZ_DIR" ]]; then
  echo "ArgosToZoo repo not found: $ATZ_DIR"
  exit 1
fi

if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "Virtualenv not found: $VENV_DIR"
  echo "Run scripts/bootstrap_researcherb.sh first."
  exit 1
fi

source "$VENV_DIR/bin/activate"

echo "Using Python: $(python --version 2>&1)"
echo "Using ARGoS: $(argos3 --version 2>&1 | head -n 1)"
echo

echo "== Platform dry run =="
cd "$PLATFORM_DIR"
printf '\n' | platform run srq5_eval

echo
echo "== Manual dry run =="
cd "$ATZ_DIR"
PYTHONPATH=src python scripts/ray_footbot_aggregation_srq5.py

echo
echo "Dry runs completed."
