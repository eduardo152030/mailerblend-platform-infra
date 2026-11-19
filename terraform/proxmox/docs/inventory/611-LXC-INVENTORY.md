# CT611 — infra-grafana

Servidor de visualización y dashboards de monitorización. Datos observados el **19/11/2026** (Europe/Madrid) con consultas de solo lectura a PVE y Docker mediante SSH estricto.

- [Declaración IaC](../../inventory/services/infra-grafana.yml)
- [Notes operativas](../../services/infra-grafana/NOTES.md)

## Infraestructura

| Campo | Valor |
|---|---|
| VMID / hostname / nodo | `611` / `infra-grafana` / `pve` |
| Estado | En ejecución |
| Sistema | Ubuntu 22.04.5 LTS, kernel 6.8.12-4-pve, Docker 29.1.3 |
| Recursos | 1 vCPU, 1048 MiB RAM y 512 MiB swap |
| Seguridad LXC | Privilegiado, perfil AppArmor `unconfined`, nesting habilitado |
| Red | `192.168.1.111/24`, `vmbr0`, gateway `192.168.1.254`, firewall de interfaz activo |
| Etiquetas PVE | `192.168.1.111`, `grafana`, `infra`, `monitoring` |
| Disco raíz | `local-lvm:vm-611-disk-0`, 10 GiB declarados y observados |
| Uso del disco | `df -h /`: 4.6 GiB usados, 4.8 GiB disponibles, 49 % de uso |

## Componentes observados

| Contenedor | Estado | Puerto publicado |
|---|---|---|
| `grafana` | Up 7 days | `0.0.0.0:3010->3000/tcp`, `[::]:3010->3000/tcp` |
| `node_exporter` | Up 7 days | `192.168.1.111:9100->9100/tcp` |
| `cadvisor` | Up 7 days (healthy) | `192.168.1.111:8085->8080/tcp` |

Los puertos publicados describen bindings de Docker. El acceso efectivo depende de la red y sus reglas de firewall.

## Memoria observada

| Métrica | Total | Usada | Libre | Disponible |
|---|---|---|---|---|
| RAM (MiB) | 1048 | 287 | 452 | 760 |
| Swap (MiB) | 512 | 96 | 415 | — |

## Notas operativas

- CT privilegiado (`unprivileged: 0`), AppArmor `unconfined`, nesting y keyctl habilitados.
- Grafana expuesto en puerto 3010 en todas las interfaces del CT.
- node_exporter y cadvisor para monitorización del LXC y contenedores Docker.
- Todos los contenedores llevan 7 días sin reinicio.
- DNS: `192.168.1.254`
- onboot: 1 (arranca automáticamente con el nodo PVE)
