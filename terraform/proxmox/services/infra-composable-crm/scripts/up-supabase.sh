#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../compose/supabase"
docker compose up -d
docker compose ps
