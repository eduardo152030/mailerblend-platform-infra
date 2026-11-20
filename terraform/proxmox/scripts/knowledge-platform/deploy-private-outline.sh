#!/usr/bin/env bash
set -euo pipefail
bootstrap="${1:?Verified CT633 bootstrap directory required}"
secrets="${2:?Private Outline directory required}"
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
compose="$repo/services/infra-knowledge"
jq -e '.ct_id == 633 and .hostname == "infra-knowledge" and .fixture == false' "$bootstrap/bootstrap.json" >/dev/null
jq -e '.ct_id == 633 and .result == "PASS" and .owner_key_access == "VERIFIED"' "$bootstrap/verified.json" >/dev/null
[[ "$(stat -c %a "$secrets")" == 700 && "$(stat -c %a "$secrets/outline.env")" == 600 ]]
known="$bootstrap/known_hosts"
ip="$(awk 'NR==1 {print $1}' "$known")"
[[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]
public_key="$(jq -er .owner_public_key_file "$bootstrap/bootstrap.json")"
opts=(-o "UserKnownHostsFile=$known" -o StrictHostKeyChecking=yes -o BatchMode=yes
      -o IdentitiesOnly=yes -i "${public_key%.pub}")
target="root@$ip"
remote=/opt/infra-knowledge
ssh "${opts[@]}" "$target" "test \"\$(hostname)\" = infra-knowledge && docker compose version >/dev/null && install -d -m 700 $remote $remote/private"
old_nginx="$(ssh "${opts[@]}" "$target" "if test -f $remote/private/nginx.conf; then sha256sum $remote/private/nginx.conf | cut -d' ' -f1; fi")"
new_nginx="$(sha256sum "$compose/private/nginx.conf" | cut -d' ' -f1)"
scp "${opts[@]}" "$compose/compose/docker-compose.yml" "$target:$remote/docker-compose.yml"
scp "${opts[@]}" "$compose/private/compose.yml" "$target:$remote/private/compose.yml"
scp "${opts[@]}" "$compose/private/nginx.conf" "$target:$remote/private/nginx.conf"
scp "${opts[@]}" "$secrets/outline.env" "$target:$remote/.env"
for name in ca.pem server.pem server.key dex.json; do
  scp "${opts[@]}" "$secrets/private/$name" "$target:$remote/private/$name"
done
ssh "${opts[@]}" "$target" 'set -eu
  cd /opt/infra-knowledge
  chmod 600 .env private/server.key private/dex.json
  chmod 644 private/ca.pem
  chown 1001:1001 private/dex.json
  compose() { docker compose -p infra-knowledge -f docker-compose.yml -f private/compose.yml "$@"; }
  compose config --quiet
  compose pull
  compose up -d --wait --wait-timeout 180'
if [[ -n "$old_nginx" && "$old_nginx" != "$new_nginx" ]]; then
  ssh "${opts[@]}" "$target" 'docker exec infra-knowledge-gateway-1 nginx -t && docker kill --signal HUP infra-knowledge-gateway-1 >/dev/null'
fi
