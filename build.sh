#!/usr/bin/env bash
# Build script for Render deployment
# Builds frontend React app and installs backend dependencies

set -e

echo "=== Building Frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== Installing Backend Dependencies ==="
cd backend
pip install -r requirements.txt

echo "=== Running Database Migrations ==="
alembic upgrade head

echo "=== Build Complete ==="
