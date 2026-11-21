#!/usr/bin/env bash
set -euo pipefail
[[ "$(hostname)" == infra-prom ]]
umask 077
destination=/opt/infra-prom/config/rules/knowledge-platform-health.yml
candidate="${1:?Rule candidate required}"
if cmp -s "$candidate" "$destination"; then
  printf 'Sin cambios\n'
  exit 0
fi
[[ ! -e "$destination" ]]
install -m 644 "$candidate" "$destination"
rollback() {
  unlink "$destination"
  docker kill --signal HUP prometheus >/dev/null
}
if ! docker exec prometheus promtool check config /etc/prometheus/prometheus.yml >/dev/null; then
  unlink "$destination"
  exit 1
fi
if ! docker kill --signal HUP prometheus >/dev/null; then
  rollback
  exit 1
fi
for attempt in {1..12}; do
  if curl -fsS --max-time 5 http://127.0.0.1:9090/api/v1/rules |
    python3 -c 'import json,sys; d=json.load(sys.stdin); assert any(g["name"]=="knowledge-platform-health" for g in d["data"]["groups"])' 2>/dev/null; then
    printf 'Regla de salud activa\n'
    exit 0
  fi
  sleep 2
done
rollback
exit 1
