#!/usr/bin/env bash
set -euo pipefail

PROM_IP="${1:-192.168.1.110}"

echo "==> Regenerating Prometheus file_sd targets from inventory"
./scripts/gen-prom-targets.py

echo "==> Deploying infra-prom to ${PROM_IP}"
./scripts/deploy-service.sh infra-prom "${PROM_IP}"

echo "==> Done. You can verify targets at: http://${PROM_IP}:9090/targets"
