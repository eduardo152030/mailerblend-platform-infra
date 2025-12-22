#!/usr/bin/env bash
set -euo pipefail

while read -r NAME IP; do
  echo "==> node_exporter -> ${NAME} (${IP})"
  ./scripts/deploy-common.sh node-exporter "${IP}"
done < <(./scripts/inventory_list.py)
