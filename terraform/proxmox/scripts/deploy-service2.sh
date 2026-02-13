#!/usr/bin/env bash
set -euo pipefail

SERVICE="${1:?Usage: deploy-service.sh <service-name> <target-ip>}"
TARGET_IP="${2:?Usage: deploy-service.sh <service-name> <target-ip>}"

SRC_DIR="services/${SERVICE}"
REMOTE_DIR="/opt/${SERVICE}"

# Flags para evitar el error de "Host Identification Changed"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

if [[ ! -d "${SRC_DIR}" ]]; then
  echo "ERROR: Service folder not found: ${SRC_DIR}" >&2
  exit 1
fi

echo "==> Deploying ${SERVICE} to ${TARGET_IP}:${REMOTE_DIR}"

# Crear directorios remotos
ssh $SSH_OPTS "root@${TARGET_IP}" "mkdir -p ${REMOTE_DIR}"

# Copy compose y config usando los mismos SSH_OPTS
rsync -av -e "ssh $SSH_OPTS" "${SRC_DIR}/compose/" "root@${TARGET_IP}:${REMOTE_DIR}/"

# Si existe carpeta config, copiarla
if [[ -d "${SRC_DIR}/config" ]]; then
  rsync -av -e "ssh $SSH_OPTS" "${SRC_DIR}/config/" "root@${TARGET_IP}:${REMOTE_DIR}/config/"
fi

# Si existe perm.env, copiarlo al remoto (necesario para Alertmanager SMTP)
if [[ -f "${SRC_DIR}/perm.env" ]]; then
  rsync -av -e "ssh $SSH_OPTS" "${SRC_DIR}/perm.env" "root@${TARGET_IP}:${REMOTE_DIR}/perm.env"
  ssh $SSH_OPTS "root@${TARGET_IP}" "chmod 600 ${REMOTE_DIR}/perm.env"
else
  echo "WARN: ${SRC_DIR}/perm.env not found (skipping)."
fi

echo "==> Ensuring docker network nucleo_network exists (idempotent)..."
ssh $SSH_OPTS "root@${TARGET_IP}" \
  "docker network inspect nucleo_network >/dev/null 2>&1 || docker network create --driver bridge --attachable nucleo_network"

echo "==> Pulling and Starting containers..."

# Caso 1: compose “clásico” en la raíz (NO rompemos nada existente)
ssh $SSH_OPTS "root@${TARGET_IP}" "test -f ${REMOTE_DIR}/docker-compose.yml" && {
  ssh $SSH_OPTS "root@${TARGET_IP}" \
    "cd ${REMOTE_DIR} && docker compose pull && docker compose up -d --remove-orphans"
  echo "==> Done. Service ${SERVICE} should be up at http://${TARGET_IP}"
  exit 0
}

# Caso 2: multi-compose por subcarpetas (ej: supabase/ y budibase/)
ssh $SSH_OPTS "root@${TARGET_IP}" "ls -1 ${REMOTE_DIR}/*/docker-compose.yml >/dev/null 2>&1" || {
  echo "ERROR: No docker-compose.yml found in ${REMOTE_DIR} or subfolders." >&2
  exit 1
}

# Orden preferido: supabase primero (datos críticos), luego budibase (UI)
# 1) Supabase (si existe)
if ssh $SSH_OPTS "root@${TARGET_IP}" "test -f ${REMOTE_DIR}/supabase/docker-compose.yml"; then
  echo "==> Starting sub-stack: supabase"
  ssh $SSH_OPTS "root@${TARGET_IP}" \
    "cd ${REMOTE_DIR}/supabase && docker compose pull && docker compose up -d --remove-orphans"
fi

# 2) Budibase (si existe)
if ssh $SSH_OPTS "root@${TARGET_IP}" "test -f ${REMOTE_DIR}/budibase/docker-compose.yml"; then
  echo "==> Starting sub-stack: budibase"
  ssh $SSH_OPTS "root@${TARGET_IP}" \
    "cd ${REMOTE_DIR}/budibase && docker compose pull && docker compose up -d --remove-orphans"
fi

# 3) Cualquier otro substack (por si creces a futuro)
echo "==> Starting any other sub-stacks (if present)..."
ssh $SSH_OPTS "root@${TARGET_IP}" "
  for f in ${REMOTE_DIR}/*/docker-compose.yml; do
    d=\$(dirname \"\$f\")
    base=\$(basename \"\$d\")
    if [ \"\$base\" != \"supabase\" ] && [ \"\$base\" != \"budibase\" ]; then
      echo \"==> Starting sub-stack: \$base\"
      (cd \"\$d\" && docker compose pull && docker compose up -d --remove-orphans)
    fi
  done
"

echo "==> Done. Service ${SERVICE} deployed to ${TARGET_IP}:${REMOTE_DIR}"
