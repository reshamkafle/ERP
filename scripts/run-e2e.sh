#!/usr/bin/env bash
# Run Selenium E2E tests (Chrome). Requires postgres + backend + frontend already running.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/e2e"

if [[ ! -d "$ROOT/backend/.venv" ]]; then
  echo "Create backend venv first: cd backend && python3 -m venv .venv && pip install -r requirements.txt"
  exit 1
fi

# shellcheck source=/dev/null
source "$ROOT/backend/.venv/bin/activate"
pip install -q -r requirements.txt

export E2E_BASE_URL="${E2E_BASE_URL:-http://localhost:5173}"
export E2E_API_URL="${E2E_API_URL:-http://localhost:8000}"
export E2E_HEADLESS="${E2E_HEADLESS:-true}"

pytest "$@"
