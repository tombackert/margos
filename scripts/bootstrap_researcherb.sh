#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MARGOS_DIR="${MARGOS_DIR:-$REPO_ROOT}"
ATZ_DIR="${ATZ_DIR:-$HOME/Repos/ArgosToZoo}"
VENV_DIR="${VENV_DIR:-$HOME/.venvs/srq5}"
TRANSFER_DIR="${TRANSFER_DIR:-/Users/Shared/srq5-transfer}"
ZPROFILE="${HOME}/.zprofile"
ZSHRC="${HOME}/.zshrc"
CURRENT_USER="$(id -un)"
NORMALIZED_USER="$(printf '%s' "$CURRENT_USER" | tr '[:upper:]' '[:lower:]')"
EXPECTED_USER="${EXPECTED_USER:-$NORMALIZED_USER}"

# Make Homebrew-installed tools available in this shell immediately, not only in future shells.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

if [[ "$NORMALIZED_USER" != "$EXPECTED_USER" ]]; then
  echo "This script is intended to run as the '$EXPECTED_USER' macOS user."
  echo "Current user: $CURRENT_USER"
  exit 1
fi

if [[ ! -d "$MARGOS_DIR" ]]; then
  echo "Margos repo not found: $MARGOS_DIR"
  exit 1
fi

if [[ ! -d "$ATZ_DIR" ]]; then
  echo "ArgosToZoo repo not found: $ATZ_DIR"
  exit 1
fi

PYTHON_BIN=""
if [[ -x /opt/homebrew/bin/python3.12 ]]; then
  PYTHON_BIN="/opt/homebrew/bin/python3.12"
elif command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.12)"
else
  echo "python3.12 not found. Expected /opt/homebrew/bin/python3.12 or python3.12 on PATH."
  exit 1
fi

mkdir -p "$(dirname "$VENV_DIR")"

if ! grep -Fq 'eval "$(/opt/homebrew/bin/brew shellenv)"' "$ZPROFILE" 2>/dev/null; then
  cat >> "$ZPROFILE" <<'EOF'
eval "$(/opt/homebrew/bin/brew shellenv)"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
EOF
fi

CMAKE_BIN=""
if [[ -x /opt/homebrew/bin/cmake ]]; then
  CMAKE_BIN="/opt/homebrew/bin/cmake"
elif command -v cmake >/dev/null 2>&1; then
  CMAKE_BIN="$(command -v cmake)"
else
  echo "cmake not found. Install it with: brew install cmake"
  exit 1
fi

MAKE_BIN=""
if command -v make >/dev/null 2>&1; then
  MAKE_BIN="$(command -v make)"
else
  echo "make not found. Install Xcode Command Line Tools with: xcode-select --install"
  exit 1
fi

ensure_fresh_cmake_build_dir() {
  local build_dir="$1"
  local source_dir="$2"
  local cache_file="$build_dir/CMakeCache.txt"

  if [[ ! -f "$cache_file" ]]; then
    return 0
  fi

  if grep -Fq "$source_dir" "$cache_file"; then
    return 0
  fi

  echo "Resetting stale CMake build directory: $build_dir"
  echo "Cached source path does not match current source: $source_dir"
  find "$build_dir" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
}

echo "Using Python: $PYTHON_BIN"
"$PYTHON_BIN" --version
echo "Using CMake: $CMAKE_BIN"
echo "Using make: $MAKE_BIN"

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip setuptools wheel

echo "Installing margos dependencies..."
cd "$MARGOS_DIR"
pip install -e '.[ml]'

echo "Installing ArgosToZoo dependencies..."
cd "$ATZ_DIR"
pip install -r requirements.txt
pip install numpy gymnasium

echo "Building margos ARGoS plugins..."
mkdir -p "$MARGOS_DIR/argos_plugins/build"
ensure_fresh_cmake_build_dir "$MARGOS_DIR/argos_plugins/build" "$MARGOS_DIR/argos_plugins"
cd "$MARGOS_DIR/argos_plugins/build"
"$CMAKE_BIN" ..
"$MAKE_BIN" -j4

echo "Building ArgosToZoo ARGoS plugins..."
mkdir -p "$ATZ_DIR/build"
ensure_fresh_cmake_build_dir "$ATZ_DIR/build" "$ATZ_DIR"
cd "$ATZ_DIR/build"
"$CMAKE_BIN" ..
"$MAKE_BIN" -j4

if ! grep -Fq '# SRQ5 researcherb setup' "$ZSHRC" 2>/dev/null; then
  cat >> "$ZSHRC" <<EOF

# SRQ5 researcherb setup
export SRQ5_TRANSFER="$TRANSFER_DIR"
alias srq5-margos='cd "$MARGOS_DIR" && source "$VENV_DIR/bin/activate"'
alias srq5-manual='cd "$ATZ_DIR" && source "$VENV_DIR/bin/activate"'
EOF
fi

echo
echo "Bootstrap complete."
echo "Verification commands:"
echo "  source \"$VENV_DIR/bin/activate\""
echo "  cd \"$MARGOS_DIR\" && margos show configs"
echo "  cd \"$ATZ_DIR\" && PYTHONPATH=src python -c \"from zoo.argos_env import ArgosEnv; print('ArgosToZoo OK')\""
