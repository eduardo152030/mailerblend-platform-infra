#!/usr/bin/env bash
set -euo pipefail
echo "== Supabase =="
cd "$(dirname "$0")/../compose/supabase" && docker compose ps
echo
echo "== Budibase =="
cd "$(dirname "$0")/../compose/budibase" && docker compose ps
