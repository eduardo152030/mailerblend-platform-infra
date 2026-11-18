# infra-prom (CT 610)

## Rol

Servidor de monitorización central. Aloja **Prometheus** y **Alertmanager**
mediante Docker Compose. Recibe métricas de los 17 contenedores LXC del
clúster y gestiona las alertas (Telegram).

## Componentes

| Componente | Detalle |
|------------|---------|
| Prometheus | `prom/prometheus:v3.12.0`, contenedor `prometheus`, puerto `9090` |
| Alertmanager | `prom/alertmanager:v0.33.0`, contenedor `eloquent_ganguly`, puerto `9093` |
| node_exporter | `prom/node-exporter`, uno por CT (incluido infra-prom) |
| cAdvisor | `ghcr.io/google/cadvisor`, uno por CT (incluido infra-prom) |
| blackbox_exporter | `prom/blackbox-exporter`, uno por CT |

## Endpoints y puertos

| Puerto | Servicio | Notas |
|--------|----------|-------|
| 9090 | Prometheus | UI y API de consultas (interno) |
| 9093 | Alertmanager | UI y API de alertas (interno) |
| 9100 | node_exporter | Métricas del host (interno) |
| 8085 | cAdvisor | Métricas de contenedores Docker (interno) |

## Configuración

- **Compose:** `/opt/infra-prom/docker-compose.yml`
- **Variables:** `/opt/infra-prom/perm.env`
- **Prometheus config:** `/opt/infra-prom/config/prometheus.yml`
- **Reglas:** `/opt/infra-prom/config/rules/`
- **Targets:** `/opt/infra-prom/config/targets/`
- **Alertmanager config:** `/.runtime/alertmanager.yml`
- **Telegram token:** `/.runtime/telegram_bot_token` (secret de Docker)

## Datos y almacenamiento

| Recurso | Evidencia |
|---------|-----------|
| Disco observado | `local-lvm:vm-610-disk-0,size=10G` |
| Disco declarado | 25 GiB en el YAML del servicio |
| Datos Prometheus | Volumen Docker `infra-prom_prom_data` (`/prometheus`) |
| Datos Alertmanager | Volumen Docker `alert_data` (`/alertmanager`) |

## Notas operativas

- Acceso: `ssh pve` → `pct exec 610` (SSH directo al CT bloqueado por host key).
- Recursos: 2 vCPU, 2048 MiB RAM, 512 MiB swap.
- Sistema: Ubuntu 22.04.5 LTS (Jammy), Docker 29.1.3.
- LXC privilegiado (`unprivileged=0`), perfil AppArmor `unconfined`.
- **Discrepancia de disco:** el disco observado es 10 GiB, el declarado 25 GiB.
  Reconciliación pendiente (ver receta `services/infra-prom/resize-20261114/`).

## Fuentes

- `inventory/services/infra-prom.yml`
- `docs/inventory/610-LXC-INVENTORY.md`
- `inventory/lxc-observed.json`