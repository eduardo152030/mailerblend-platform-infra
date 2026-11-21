#!/usr/bin/env bash
set -euo pipefail
umask 077
staged="${2:?Private staging path required}"
case "${1:?Expected diagrams or edge}" in
  diagrams)
    [[ "$(hostname)" == infra-diagrams ]]
    cd /opt/infra-diagrams
    [[ ! -e edge && -f .env ]]
    cp -p .env "$staged/env.before"
    install -d -m 700 edge
    install -m 644 "$staged/"{compose.yml,nginx.conf,server.pem} edge/
    install -m 600 "$staged/server.key" edge/
    compose() { docker compose -p infra-diagrams -f docker-compose.yml -f edge/compose.yml "$@"; }
    restore() {
      cp -p "$staged/env.before" .env
      compose stop gateway
      docker compose -p infra-diagrams up -d --no-deps drawio
    }
    trap restore ERR
    python3 - <<'PY'
from pathlib import Path
path = Path(".env")
before = path.read_text()
old = "DRAWIO_URL=http://127.0.0.1:8080/\n"
assert before.count(old) == 1
path.write_text(before.replace(old, "DRAWIO_URL=https://infra-diagrams.mailerblend.com/\n"))
PY
    compose config --quiet
    compose run --rm --no-deps gateway nginx -t
    compose up -d --wait --wait-timeout 120
    trap - ERR
    ;;
  restart-drawio)
    [[ "$(hostname)" == infra-diagrams ]]
    cd /opt/infra-diagrams
    docker compose -p infra-diagrams -f docker-compose.yml -f edge/compose.yml restart drawio
    ;;
  rollback-diagrams)
    [[ "$(hostname)" == infra-diagrams ]]
    cd /opt/infra-diagrams
    grep -Fx 'DRAWIO_URL=https://infra-diagrams.mailerblend.com/' .env >/dev/null
    cp -p "$staged/env.before" .env
    docker compose -p infra-diagrams -f docker-compose.yml -f edge/compose.yml stop gateway
    docker compose -p infra-diagrams up -d --no-deps drawio
    ;;
  rollback-edge)
    [[ "$(hostname)" == edge-router ]]
    available=/etc/nginx/sites-available/infra-diagrams.mailerblend.com.conf
    enabled=/etc/nginx/sites-enabled/infra-diagrams.mailerblend.com.conf
    [[ "$(readlink "$enabled")" == "$available" ]]
    cmp -s "$available" "$staged/vhost.conf"
    unlink "$enabled"
    if ! nginx -t || ! systemctl reload nginx; then
      ln -s "$available" "$enabled"
      nginx -t && systemctl reload nginx
      exit 1
    fi
    ;;
  edge)
    [[ "$(hostname)" == edge-router ]]
    available=/etc/nginx/sites-available/infra-diagrams.mailerblend.com.conf
    enabled=/etc/nginx/sites-enabled/infra-diagrams.mailerblend.com.conf
    ca=/etc/nginx/knowledge-platform/ct634-ca.pem
    [[ ! -e "$available" && ! -L "$enabled" && ! -e "$ca" ]]
    install -m 644 "$staged/ct634-ca.pem" "$ca"
    install -m 644 "$staged/vhost.conf" "$available"
    ln -s "$available" "$enabled"
    if ! nginx -t || ! systemctl reload nginx; then
      unlink "$enabled"
      mv "$available" "$staged/vhost.rejected"
      mv "$ca" "$staged/ca.rejected"
      nginx -t && systemctl reload nginx
      exit 1
    fi
    ;;
  *) exit 2 ;;
esac
