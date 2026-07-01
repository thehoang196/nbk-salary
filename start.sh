#!/usr/bin/env bash
# Start script for Render deployment
# Runs Alembic migrations then starts uvicorn

set -e

cd backend

echo "=== Running migrations ==="
alembic upgrade head 2>/dev/null || echo "Migrations skipped (may already be up to date)"

echo "=== Seeding data ==="
python -m app.seed 2>/dev/null || echo "Seed skipped"

echo "=== Starting server on port $PORT ==="
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
