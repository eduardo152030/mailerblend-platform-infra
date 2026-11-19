# CT610 — infra-prom

Servidor central de monitorización. Datos observados el **19/11/2026**
(Europe/Madrid) con consultas de solo lectura a PVE y Docker mediante SSH
estricto.

- [Declaración IaC](../../inventory/services/infra-prom.yml)
- [Notes operativas](../../services/infra-prom/NOTES.md)
- [Ampliación de disco y evidencias de backup](../roadmap/CT610-DISK-20261114.md)
- [Declaración de Blackbox Exporter en CT616](../../inventory/services/infra-blackbox.yml)

## Infraestructura

| Campo | Valor |
|---|---|
| VMID / hostname / nodo | `610` / `infra-prom` / `pve` |
| Estado | En ejecución |
| Sistema | Ubuntu 22.04.5 LTS, Docker 29.1.3 |
| Recursos | 2 vCPU, 2048 MiB RAM y 512 MiB swap |
| Seguridad LXC | Privilegiado, perfil AppArmor `unconfined` |
| Red | `192.168.1.110/24`, `vmbr0`, gateway `192.168.1.254`, firewall de interfaz activo |
| Etiquetas PVE | `192.168.1.110`, `infra`, `monitoring`, `prometheus` |
| Disco raíz | `local-lvm:vm-610-disk-0`, 25 GiB declarados y observados |
| Uso del disco | `df -h /`: 8,3 GiB usados, 16 GiB disponibles, 36 % de uso |

## Componentes observados

| Contenedor | Versión o imagen observada | Estado | Puerto publicado |
|---|---|---|---|
| `prometheus` | `prom/prometheus:v3.12.0` | En ejecución, 0 reinicios | TCP 9090 en todas las interfaces del CT |
| `alertmanager` | `prom/alertmanager:v0.33.0` | En ejecución, 0 reinicios | TCP 9093 en todas las interfaces del CT |
| `node_exporter` | ID `3ac34ce007ac` | En ejecución | `192.168.1.110:9100/tcp` |
| `cadvisor` | ID `b8e7d1093144` | En ejecución, healthy | `192.168.1.110:8085` → `8080/tcp` |
| `pve-uptime-exporter` | `mailerblend/pve-uptime:3.11.0-py312-d056` | En ejecución | Sin puerto publicado |

Los puertos publicados describen bindings de Docker. El acceso efectivo
depende de la red y sus reglas de firewall.

## Persistencia y configuración

| Componente | Volumen | Montajes de solo lectura dentro del contenedor |
|---|---|---|
| Prometheus | `infra-prom_prom_data` en `/prometheus` | `/etc/prometheus/prometheus.yml`, `/etc/prometheus/rules`, `/etc/prometheus/targets` |
| Alertmanager | `infra-prom_alert_data` en `/alertmanager` | `/etc/alertmanager/alertmanager.yml`, `/etc/alertmanager/templates`, secreto de Telegram bajo `/run/secrets/` |

La revisión comprobó configuración y estado de contenedores. La restauración
funcional y la recepción humana de avisos Telegram quedan pendientes de prueba.
