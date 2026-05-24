#!/usr/bin/env bash
# Seed the whole ERP via Selenium WebDriver (Chrome).
# Requires: postgres + backend + frontend running (same as E2E).
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
export E2E_SEED_COUNT="${E2E_SEED_COUNT:-10}"

echo "Seeding ERP via Selenium (${E2E_SEED_COUNT} records per type)…"
pytest test_system_seed.py -m slow "$@"
