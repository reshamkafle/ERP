#!/usr/bin/env bash
# Start ERP locally: Postgres (Docker) + backend + frontend
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Open Docker Desktop, wait until it is ready, then run this script again."
  exit 1
fi

echo "Starting Postgres..."
docker compose -f "$ROOT/docker-compose.yml" up -d postgres

echo "Waiting for Postgres..."
for i in $(seq 1 60); do
  if docker exec erp-postgres-1 pg_isready -U erp -d erp >/dev/null 2>&1; then
    echo "Postgres ready."
    break
  fi
  if [[ "$i" -eq 60 ]]; then
    echo "Postgres did not become ready in time."
    exit 1
  fi
  sleep 1
done

echo "Starting backend on http://127.0.0.1:8000 ..."
(
  cd "$ROOT/backend"
  source .venv/bin/activate
  exec uvicorn app.main:app --reload --port 8000
) &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:5173 ..."
(
  cd "$ROOT/frontend"
  exec npm run dev
) &
FRONTEND_PID=$!

trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null' EXIT

echo ""
echo "ERP is starting:"
echo "  App:     http://localhost:5173/"
echo "  API:     http://127.0.0.1:8000/api/v1/health"
echo "  Login:   admin@example.com / changeme123"
echo ""
echo "Press Ctrl+C to stop backend and frontend."

wait
