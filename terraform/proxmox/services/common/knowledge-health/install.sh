#!/usr/bin/env bash
set -euo pipefail
case "${1:?Expected host required}" in
  infra-knowledge|infra-diagrams|infra-modeling) ;;
  *) exit 2 ;;
esac
[[ "$(hostname)" == "$1" ]]
test -d /var/lib/node_exporter/textfile
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
changed=0
apply() {
  local source="$1" dest="$2" mode="$3"
  if ! cmp -s "$here/$source" "$dest"; then
    install -m "$mode" "$here/$source" "$dest"
    changed=1
  fi
}
apply probe.sh /opt/lxc-monitoring/knowledge-health.sh 0755
apply knowledge-health.service /etc/systemd/system/knowledge-health.service 0644
apply knowledge-health.timer /etc/systemd/system/knowledge-health.timer 0644
if (( changed )); then systemctl daemon-reload; fi
systemctl is-active --quiet knowledge-health.timer || systemctl enable --now knowledge-health.timer
systemctl start knowledge-health.service
awk '$1=="knowledge_app_probe_success" {ok=($2==1)} END {exit !ok}' /var/lib/node_exporter/textfile/knowledge-health.prom
