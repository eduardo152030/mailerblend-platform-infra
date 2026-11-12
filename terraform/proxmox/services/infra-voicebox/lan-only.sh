#!/usr/bin/env bash
set -euo pipefail
[[ $(hostname) == infra-voicebox ]]
# Regla específica del puerto Voicebox después de DNAT; no cambia otras políticas.
args=(-p tcp ! -s 192.168.1.0/24 -m conntrack --ctdir ORIGINAL --ctorigdst 192.168.1.127 --ctorigdstport 17493 -j DROP)
iptables -C DOCKER-USER "${args[@]}" 2>/dev/null || iptables -I DOCKER-USER 1 "${args[@]}"
# Migración exacta del candidato inicial D063: no filtrar respuestas del bridge.
old=(-p tcp ! -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.1.127 --ctorigdstport 17493 -j DROP)
if iptables -C DOCKER-USER "${old[@]}" 2>/dev/null; then
  iptables -D DOCKER-USER "${old[@]}"
fi
