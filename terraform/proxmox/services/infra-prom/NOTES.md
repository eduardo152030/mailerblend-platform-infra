# CT 610 — infra-prom

Servidor central de monitorización. Prometheus recopila métricas del clúster
y Alertmanager gestiona las notificaciones a Telegram.

## Estado observado el 19/11/2026 (Europe/Madrid)

- Nodo PVE `pve`, Ubuntu 22.04.5 LTS, Docker 29.1.3.
- 2 vCPU, 2048 MiB RAM y 512 MiB swap. LXC privilegiado con perfil AppArmor
  `unconfined`.
- IP `192.168.1.110/24`, bridge `vmbr0`, gateway `192.168.1.254` y firewall
  de interfaz activo.
- Disco raíz `local-lvm:vm-610-disk-0` de 25 GiB. `df -h /` mostró 16 GiB
  disponibles y 36 % de uso.
- Prometheus v3.12.0 y Alertmanager v0.33.0 estaban en ejecución, con cero
  reinicios registrados por Docker. También estaban en ejecución Node
  Exporter, cAdvisor y el exporter central de disponibilidad PVE.
  Blackbox Exporter se aloja en CT616.

## Puertos y persistencia

| Componente | Puerto publicado | Volumen |
|---|---|---|
| Prometheus | TCP 9090 en todas las interfaces del CT | `infra-prom_prom_data` en `/prometheus` |
| Alertmanager | TCP 9093 en todas las interfaces del CT | `infra-prom_alert_data` en `/alertmanager` |
| Node Exporter | `192.168.1.110:9100` | |
| cAdvisor | `192.168.1.110:8085` | |

Prometheus monta su configuración, reglas y targets bajo `/etc/prometheus/`
en solo lectura. Alertmanager monta su configuración y plantillas bajo
`/etc/alertmanager/` y lee el secreto de Telegram desde `/run/secrets/`.

## Referencias del repositorio

- Ficha técnica: `docs/inventory/610-LXC-INVENTORY.md`
- Declaración IaC: `inventory/services/infra-prom.yml`
- Ampliación del disco: `docs/roadmap/CT610-DISK-20261114.md`
