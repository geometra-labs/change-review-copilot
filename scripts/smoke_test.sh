#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "Checking health..."
curl -sSf "${BASE_URL}/health" >/dev/null

echo "Registering or logging in..."
REGISTER=$(curl -sS -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke@example.com","password":"password123"}' || true)

TOKEN=$(printf '%s' "$REGISTER" | python -c "import json,sys; raw=sys.stdin.read().strip(); print(json.loads(raw)['access_token'] if raw else '')" 2>/dev/null || true)

if [ -z "$TOKEN" ]; then
  LOGIN=$(curl -sS -X POST "${BASE_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"smoke@example.com","password":"password123"}')
  TOKEN=$(printf '%s' "$LOGIN" | python -c "import json,sys; print(json.loads(sys.stdin.read())[\"access_token\"])")
fi

echo "Creating project..."
curl -sS -X POST "${BASE_URL}/projects" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"name":"Smoke Project","description":"Smoke test"}' >/dev/null

echo "Listing projects..."
curl -sS -X GET "${BASE_URL}/projects" \
  -H "Authorization: Bearer ${TOKEN}" >/dev/null

echo "Smoke test passed."
