# CT 611 — infra-grafana

Panel de visualización y dashboards del clúster. Grafana se conecta a
Prometheus (CT610) como fuente de datos principal.

## Estado observado el 19/11/2026 (Europe/Madrid)

- Nodo PVE `pve`, Ubuntu 22.04.5 LTS (Jammy), kernel `6.8.12-4-pve`.
- 1 vCPU, 1048 MiB RAM y 512 MiB swap. LXC privilegiado con perfil AppArmor
  `unconfined`, nesting habilitado.
- IP `192.168.1.111/24`, bridge `vmbr0`, gateway `192.168.1.254`, DNS
  `192.168.1.254`, firewall de interfaz activo.
- Disco raíz `local-lvm:vm-611-disk-0` de 10 GiB. `df -h /` mostró 4,6 GiB
  usados, 4,8 GiB disponibles, 49 % de uso.
- Grafana, Node Exporter y cAdvisor en ejecución desde hace 8 días sin
  reinicios.

## Puertos y persistencia

| Componente | Puerto publicado | Volumen |
|---|---|---|
| Grafana | TCP 3010 en todas las interfaces del CT | `grafana_data` en `/var/lib/grafana` |
| Node Exporter | `192.168.1.111:9100` | `/` montado en `/host` |
| cAdvisor | `192.168.1.111:8085` | Múltiples montajes de solo lectura (`/rootfs`, `/sys`, `/var/lib/docker`, `/var/run/docker.sock`, etc.) |

Grafana monta su configuración de provisioning bajo
`/opt/infra-grafana/config/provisioning` en solo lectura y sus dashboards
bajo `/opt/infra-grafana/config/dashboards`.

## Referencias del repositorio

- Ficha técnica: `docs/inventory/611-LXC-INVENTORY.md`
- Declaración IaC: `inventory/services/infra-grafana.yml`
- Compose: `services/infra-grafana/compose/docker-compose.yml`
