#!/usr/bin/env bash
set -euo pipefail
case "$(hostname)" in
  infra-knowledge)
    response=$(curl -fsS --max-time 5 --resolve knowledge.test:18443:127.0.0.1 \
      --cacert /opt/infra-knowledge/private/ca.pem https://knowledge.test:18443/_health) && [[ "$response" == OK ]] && status=1 || status=0 ;;
  infra-diagrams)
    response=$(curl -fsS --max-time 5 http://127.0.0.1:8080/) && [[ "$response" == *draw.io* || "$response" == *diagrams.net* ]] && status=1 || status=0 ;;
  infra-modeling)
    encoded=$(python3 -c 'import base64,zlib;c=zlib.compressobj(wbits=-15);b=c.compress(b"@startuml\nAlice -> Bob\n@enduml\n")+c.flush();b+=bytes(-len(b)%3);print(base64.b64encode(b).decode().translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/","0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_")))')
    response=$(curl -fsS --max-time 5 "http://127.0.0.1:8080/svg/$encoded") && [[ "$response" == *"<svg"* && "$response" == *Alice* ]] && status=1 || status=0 ;;
  *) exit 2 ;;
esac

directory=/var/lib/node_exporter/textfile
temp=$(mktemp "$directory/.knowledge-health.XXXXXX")
trap 'unlink "$temp" 2>/dev/null || true' EXIT
{
  printf '# TYPE knowledge_app_probe_success gauge\nknowledge_app_probe_success %d\n' "$status"
  printf '# TYPE knowledge_app_probe_timestamp_seconds gauge\nknowledge_app_probe_timestamp_seconds %s\n' "$(date +%s)"
} > "$temp"
chmod 644 "$temp"
mv -f "$temp" "$directory/knowledge-health.prom"
