# CT611 — infra-grafana

Servidor de visualización y dashboards de monitorización. Datos observados el **19/11/2026** (Europe/Madrid) con consultas de solo lectura a PVE y Docker mediante SSH estricto.

## Componentes observados

| Contenedor | Estado | Puerto publicado |
|---|---|---|
| `grafana` | Up 7 days | `0.0.0.0:3010->3000/tcp`, `[::]:3010->3000/tcp` |
| `node_exporter` | Up 7 days | `192.168.1.111:9100->9100/tcp` |
| `cadvisor` | Up 7 days (healthy) | `192.168.1.111:8085->8080/tcp` |

## Recursos

- **CPU:** 1 vCPU
- **RAM:** 1048 MiB (287 MiB usados, 760 MiB disponibles)
- **Swap:** 512 MiB (96 MiB usados)
- **Disco raíz:** 9.8 GiB, 4.6 GiB usados (49%), 4.8 GiB disponibles
- **Red:** `192.168.1.111/24`, gateway `192.168.1.254`, firewall de interfaz activo
- **Etiquetas PVE:** `192.168.1.111`, `grafana`, `infra`, `monitoring`
- **Sistema:** Ubuntu 22.04.5 LTS, kernel 6.8.12-4-pve
- **Docker:** 29.1.3, Compose 5.0.0

## Notas operativas

- CT privilegiado (`unprivileged: 0`), AppArmor `unconfined`, nesting habilitado.
- Grafana expuesto en puerto 3010 en todas las interfaces.
- node_exporter y cadvisor para monitorización del LXC y contenedores Docker.
- Todos los contenedores llevan 7 días sin reinicio.
