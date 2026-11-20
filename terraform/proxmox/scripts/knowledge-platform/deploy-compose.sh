#!/usr/bin/env bash
set -euo pipefail

service="${1:?Service key required}"
bootstrap_dir="${2:?Verified SSH bootstrap directory required}"
env_file="${3:?Private environment file required}"
case "$service" in
  infra-knowledge) ct=633 ;;
  infra-diagrams) ct=634 ;;
  infra-modeling) ct=635 ;;
  *) printf 'Unknown platform service\n' >&2; exit 2 ;;
esac

bootstrap="$bootstrap_dir/bootstrap.json"
jq -e --arg service "$service" --argjson ct "$ct" \
  '.hostname == $service and .ct_id == $ct and .fixture == false' "$bootstrap" >/dev/null
jq -e --argjson ct "$ct" \
  '.ct_id == $ct and .result == "PASS" and .owner_key_access == "VERIFIED"' \
  "$bootstrap_dir/verified.json" >/dev/null
[[ -f "$env_file" && ! -L "$env_file" && "$(stat -c '%a' "$env_file")" == 600 ]]
known_hosts="$bootstrap_dir/known_hosts"
ip="$(awk 'NR==1 {print $1}' "$known_hosts")"
[[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]
public_key="$(jq -er .owner_public_key_file "$bootstrap")"
remote="/opt/$service"
module="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
ssh_opts=(-o "UserKnownHostsFile=$known_hosts" -o StrictHostKeyChecking=yes
          -o BatchMode=yes -o IdentitiesOnly=yes -i "${public_key%.pub}")
target="root@$ip"
ssh "${ssh_opts[@]}" "$target" "test \"\$(hostname)\" = '$service' && docker compose version >/dev/null && install -d -m 700 '$remote'"
scp "${ssh_opts[@]}" "$module/services/$service/compose/docker-compose.yml" "$target:$remote/docker-compose.yml.candidate"
scp "${ssh_opts[@]}" "$env_file" "$target:$remote/.env.candidate"
ssh "${ssh_opts[@]}" "$target" "set -eu
  cd '$remote'
  chmod 600 .env.candidate
  docker compose --project-name '$service' --env-file .env.candidate -f docker-compose.yml.candidate config --quiet
  docker compose --project-name '$service' --env-file .env.candidate -f docker-compose.yml.candidate pull
  if [ -f docker-compose.yml ] && [ -f .env ] && { ! cmp -s docker-compose.yml docker-compose.yml.candidate || ! cmp -s .env .env.candidate; }; then
    stamp=\$(date -u +%Y%m%dT%H%M%S%N)
    install -m 600 docker-compose.yml \"docker-compose.yml.\$stamp\"
    install -m 600 .env \".env.\$stamp\"
  fi
  mv .env.candidate .env
  mv docker-compose.yml.candidate docker-compose.yml
  docker compose --project-name '$service' up -d --wait"
