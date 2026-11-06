#!/usr/bin/env bash
# Run only after explicit deployment approval. Never enable shell tracing.
set -euo pipefail
cd "$(dirname "$0")/../.."
PROM_HOST="${PROM_HOST:-192.168.1.110}"
[[ "$PROM_HOST" =~ ^[a-zA-Z0-9.-]+$ ]] || { echo 'Invalid PROM_HOST' >&2; exit 1; }
READINESS_TIMEOUT="${READINESS_TIMEOUT:-90}"
READINESS_INTERVAL="${READINESS_INTERVAL:-2}"
for VALUE in "$READINESS_TIMEOUT" "$READINESS_INTERVAL"; do
  [[ "$VALUE" =~ ^[1-9][0-9]*$ ]] && (( VALUE <= 3600 )) || {
    echo 'Readiness timeout/interval must be integers between 1 and 3600 seconds.' >&2; exit 2;
  }
done
./scripts/validate-monitoring.sh
# Override any global UserKnownHostsFile=/dev/null for both transports.
SSH_OPTIONS=(-o BatchMode=yes -o StrictHostKeyChecking=yes
  -o "UserKnownHostsFile=$HOME/.ssh/known_hosts")
SSH=(ssh "${SSH_OPTIONS[@]}" "root@$PROM_HOST")
# rsync parses -e as words, with doubled single quotes inside quoted arguments.
RSH=ssh
for OPTION in "${SSH_OPTIONS[@]}"; do
  RSH+=" '${OPTION//\'/\'\'}'"
done
# Preserve remote baseline including secrets, accessible only by root.
"${SSH[@]}" 'set -eu; umask 077; mkdir -p /opt/infra-prom/.rollback; chmod 700 /opt/infra-prom/.rollback; if test -f /opt/infra-prom/docker-compose.yml; then tar --exclude=./.rollback -czf /opt/infra-prom/.rollback/pre-telegram-$(date -u +%Y%m%dT%H%M%SZ).tgz -C /opt/infra-prom .; fi; mkdir -p /opt/infra-prom/config /opt/infra-prom/.runtime; chmod 700 /opt/infra-prom/.runtime'
# Snapshot before copying content: Compose does not track changes inside bind mounts.
"${SSH[@]}" bash -s -- snapshot "$READINESS_TIMEOUT" "$READINESS_INTERVAL" < scripts/apply-monitoring.sh
rsync -a -e "$RSH" services/infra-prom/compose/ "root@$PROM_HOST:/opt/infra-prom/"
rsync -a --checksum --inplace -e "$RSH" services/infra-prom/config/ "root@$PROM_HOST:/opt/infra-prom/config/"
rsync -a --checksum --inplace -e "$RSH" services/infra-prom/.runtime/alertmanager.yml services/infra-prom/.runtime/telegram_bot_token "root@$PROM_HOST:/opt/infra-prom/.runtime/"
"${SSH[@]}" bash -s -- apply "$READINESS_TIMEOUT" "$READINESS_INTERVAL" < scripts/apply-monitoring.sh
echo 'Deployment complete. Check targets, rules and Telegram delivery; readiness alone does not prove delivery.'
