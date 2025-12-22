#!/usr/bin/env bash
set -euo pipefail

PROM_IP="${1:-192.168.1.110}"

echo "==> Generating Prometheus targets from inventory"
./scripts/gen-prom-targets.py

echo "==> Deploying infra-prom to ${PROM_IP}"
./scripts/deploy-service.sh infra-prom "${PROM_IP}"

echo "==> Done. Targets summary:"
curl -s "http://${PROM_IP}:9090/api/v1/targets" | grep -E '"job":"(node|cadvisor)"' -n || true
