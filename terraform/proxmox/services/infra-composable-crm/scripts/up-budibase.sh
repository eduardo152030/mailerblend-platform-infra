#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../compose/budibase"
docker compose up -d
docker compose ps
