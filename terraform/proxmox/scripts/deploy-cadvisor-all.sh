#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INV_DIR="$ROOT_DIR/inventory/services"

# cAdvisor: expone /metrics en :8080 dentro del contenedor
# Nosotros lo mapeamos a :8085 en el host para coincidir con Prometheus targets.
CADVISOR_IMAGE="${CADVISOR_IMAGE:-gcr.io/cadvisor/cadvisor:v0.49.1}"
HOST_PORT="${HOST_PORT:-8085}"
NAME="cadvisor"

if [[ ! -d "$INV_DIR" ]]; then
  echo "ERROR: inventory/services no existe: $INV_DIR" >&2
  exit 1
fi

mapfile -t SERVICE_FILES < <(find "$INV_DIR" -maxdepth 1 -type f -name "*.yml" | sort)

if [[ "${#SERVICE_FILES[@]}" -eq 0 ]]; then
  echo "ERROR: No hay archivos *.yml en $INV_DIR" >&2
  exit 1
fi

echo "==> Deploying cAdvisor to all services from inventory: $INV_DIR"
echo "     Image: $CADVISOR_IMAGE"
echo "     Port : $HOST_PORT -> 8080"
echo

for f in "${SERVICE_FILES[@]}"; do
  svc="$(awk -F': ' '/^\s*name:\s*/{print $2; exit}' "$f" | tr -d '\r')"
  ip="$(awk -F': ' '/^\s*ip:\s*/{print $2; exit}' "$f" | cut -d/ -f1 | tr -d '\r')"

  if [[ -z "${svc:-}" || -z "${ip:-}" ]]; then
    echo "SKIP: no pude leer name/ip en $f"
    continue
  fi

  echo "---- $svc ($ip) ----"

  ssh -o StrictHostKeyChecking=accept-new "root@$ip" bash -s <<EOSSH
set -euo pipefail

# asegurar docker
command -v docker >/dev/null 2>&1 || { apt-get update && apt-get install -y docker.io docker-compose-plugin; systemctl enable --now docker; }

# stop/remove si ya existe
docker rm -f ${NAME} >/dev/null 2>&1 || true

# levantar cAdvisor
docker run -d --name ${NAME} --restart unless-stopped \
  --privileged \
  -p ${HOST_PORT}:8080 \
  -v /:/rootfs:ro \
  -v /var/run:/var/run:rw \
  -v /sys:/sys:ro \
  -v /var/lib/docker/:/var/lib/docker:ro \
  -v /dev/disk/:/dev/disk:ro \
  ${CADVISOR_IMAGE} >/dev/null

# sanity check local
curl -fsS "http://127.0.0.1:${HOST_PORT}/metrics" >/dev/null
echo "OK: cAdvisor up on :${HOST_PORT}"
EOSSH

  echo
done

echo "==> Done."
