#!/usr/bin/env bash
set -euo pipefail
# Do not recreate anonymous data volumes or start two all-in-one stacks blindly.
ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
python3 "$ROOT_DIR/scripts/validate-budibase-topology.py"
cd "$(dirname "$0")/../compose/budibase"
docker compose up -d
docker compose ps
