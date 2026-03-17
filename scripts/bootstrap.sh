#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true
docker-compose up -d db

echo "Bootstrap complete."
echo "Run 'make api' and 'make web' in separate terminals."
