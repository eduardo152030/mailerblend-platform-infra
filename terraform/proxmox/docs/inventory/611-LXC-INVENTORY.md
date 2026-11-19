# CT611 — infra-grafana

Panel de visualización y dashboards del clúster. Datos observados el
**19/11/2026** (Europe/Madrid) con consultas de solo lectura a PVE y Docker
mediante SSH estricto.

- [Declaración IaC](../../inventory/services/infra-grafana.yml)
- [Notes operativas](../../services/infra-grafana/NOTES.md)

## Infraestructura

| Campo | Valor |
|---|---|
| VMID / hostname / nodo | `611` / `infra-grafana` / `pve` |
| Estado | En ejecución |
| Sistema | Ubuntu 22.04.5 LTS (Jammy), kernel `6.8.12-4-pve` |
| Recursos | 1 vCPU, 1048 MiB RAM y 512 MiB swap |
| Seguridad LXC | Privilegiado, perfil AppArmor `unconfined`, nesting=1, keyctl=1 |
| Red | `192.168.1.111/24`, `vmbr0`, gateway `192.168.1.254`, firewall de interfaz activo |
| Etiquetas PVE | `192.168.1.111`, `grafana`, `infra`, `monitoring` |
| Disco raíz | `local-lvm:vm-611-disk-0`, 10 GiB declarados y observados |
| Uso del disco | `df -h /`: 4,6 GiB usados, 4,8 GiB disponibles, 49 % de uso |

## Componentes observados

| Contenedor | Imagen | Estado | Puerto publicado |
|---|---|---|---|
| `grafana` | `grafana/grafana:latest` (sha256:2175aaa91c96) | En ejecución, 8 días | TCP 3010 en todas las interfaces del CT |
| `node_exporter` | `prom/node-exporter@sha256:3ac34ce007ac` | En ejecución, 8 días | `192.168.1.111:9100/tcp` |
| `cadvisor` | `ghcr.io/google/cadvisor@sha256:b8e7d1093144` | En ejecución, healthy, 8 días | `192.168.1.111:8085` → `8080/tcp` |

Los puertos publicados describen bindings de Docker. El acceso efectivo
depende de la red y sus reglas de firewall.

## Persistencia y configuración

| Componente | Volumen | Montajes de solo lectura dentro del contenedor |
|---|---|---|
| Grafana | `grafana_data` en `/var/lib/grafana` | `/opt/infra-grafana/config/provisioning` → `/etc/grafana/provisioning`, `/opt/infra-grafana/config/dashboards` → `/var/lib/grafana/dashboards` |
| Node Exporter | `/` montado en `/host` | `node-cgroup.sh` en `/opt/pilot-node-cgroup.sh` |
| cAdvisor | — | `/rootfs`, `/sys`, `/var/lib/docker`, `/var/run/docker.sock`, `/run/containerd/containerd.sock`, `/var/lib/containerd` |

Grafana se conecta a Prometheus en `http://192.168.1.110:9090` como fuente
de datos por defecto. La configuración de provisioning incluye un datasource
de Prometheus y dashboards de flota Proxmox LXC.

## Contenedores eliminados (historial)

| Contenedor | Imagen | Estado | Motivo |
|---|---|---|---|
| `grafana-d060-replay-final` | sha256:2175aaa91c96 | Exited (0) | Prueba D060 |
| `grafana-d060-replay3` | sha256:2175aaa91c96 | Exited (0) | Prueba D060 |
| `grafana-d060-replay2` | sha256:2175aaa91c96 | Exited (0) | Prueba D060 |
| `grafana-d060-replay` | sha256:2175aaa91c96 | Exited (0) | Prueba D060 |
| `cadvisor-pre-phase4-611` | `gcr.io/cadvisor/cadvisor:v0.49.1` | Exited (0) | Reemplazado por fase 4 |
| `node_exporter-pre-phase4-611` | `prom/node-exporter:latest` | Exited (143) | Reemplazado por fase 4 |
