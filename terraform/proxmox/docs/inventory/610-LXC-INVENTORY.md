# CT610 — infra-prom · Inventario técnico

Ficha principal de CT610, el servidor de monitorización central del clúster.
Captura del **18 de noviembre de 2026**, basada en la inspección del observed
state y la auditoría de configuración. El acceso al CT se hizo mediante
`ssh infra-prom` (SSH directo). Las evidencias de origen conservan sus marcas
de tiempo en UTC.

**Estado al corte.** El CT está en ejecución. Prometheus v3.12.0 y Alertmanager
v0.33.0 están corriendo mediante Docker Compose. Los exporters (node_exporter,
cAdvisor, blackbox_exporter) están desplegados en los 17 CT del clúster.

- [Inventario declarado](../../inventory/services/infra-prom.yml)
- [Inventario LXC observado](../../inventory/lxc-observed.json)
- [Notes operativas de infra-prom](../../services/infra-prom/NOTES.md)

## A. Identificación e infraestructura

| Campo | Valor |
|---|---|
| CT / hostname / nodo | `610` / `infra-prom` / `pve` |
| Estado observado | `running` |
| Plataforma y sistema | Proxmox LXC con Docker Compose sobre Ubuntu 22.04.5 LTS (Jammy) |
| Clasificación | Etiquetas `internal` y `monitoring`. Clasificación formal `Not verified` en la metadata |
| Recursos asignados | 2 vCPU, 2048 MiB de RAM, 512 MiB de swap |
| Privilegios y AppArmor | LXC privilegiado (`unprivileged=0`), perfil `unconfined` |
| Red | `192.168.1.110/24`, bridge `vmbr0`, gateway `192.168.1.254`. Firewall de interfaz habilitado |
| Disco observado | `local-lvm:vm-610-disk-0,size=10G` |
| Disco declarado | 25 GiB en el YAML del servicio. Diferencia pendiente de reconciliar |
| Descripción observada en Proxmox | `Managed by Terraform - Service: infra-prom` |
| Etiquetas observadas | `192.168.1.110;monitoring;infra;internal;prometheus` |

## B. Función del servicio

CT610 aloja el servidor de monitorización central del clúster. Prometheus
recopila métricas de todos los CT mediante exporters (node_exporter,
cAdvisor, blackbox_exporter). Alertmanager gestiona las alertas y las
notificaciones por Telegram.

## C. Aplicaciones y componentes

| Servicio | Contenedor | Imagen o versión observada | Estado observado |
|---|---|---|---|
| Prometheus | `prometheus` | `prom/prometheus:v3.12.0` | En ejecución, 0 reinicios observados |
| Alertmanager | `eloquent_ganguly` | `prom/alertmanager:v0.33.0` | En ejecución, 0 reinicios observados |
| node_exporter | `node_exporter` | `prom/node-exporter` | En ejecución |
| cAdvisor | `cadvisor` | `ghcr.io/google/cadvisor` | En ejecución, `healthy` |
| blackbox_exporter | `blackbox_exporter` | `prom/blackbox-exporter` | En ejecución |

## D. Red y puertos

| Puerto publicado en el CT | Puerto en Docker | Servicio |
|---|---|---|
| `192.168.1.110:9090` | `9090/tcp` | UI y API de Prometheus |
| `192.168.1.110:9093` | `9093/tcp` | UI y API de Alertmanager |
| `192.168.1.110:9100` | `9100/tcp` | Métricas de node_exporter |
| `192.168.1.110:8085` | `8080/tcp` | Métricas de cAdvisor |

El inventario de routing citado en la ficha de origen no registra un dominio
público, un proxy Nginx ni una regla de publicación para CT610. El alcance de
acceso efectivo depende de la red y de sus reglas de firewall.

## E. Datos y almacenamiento

| Recurso | Evidencia |
|---|---|
| Sistema de archivos raíz | 10 GiB observados (disco LXC). Uso pendiente de verificación con `df -h` |
| Datos Prometheus | Volumen Docker `infra-prom_prom_data` montado en `/prometheus` |
| Datos Alertmanager | Volumen Docker `alert_data` montado en `/alertmanager` |
| Configuración Prometheus | `/opt/infra-prom/config/prometheus.yml` (bind mount, solo lectura) |
| Reglas de alerta | `/opt/infra-prom/config/rules/` (bind mount, solo lectura) |
| Targets de scraping | `/opt/infra-prom/config/targets/` (bind mount, solo lectura) |
| Configuración Alertmanager | `/.runtime/alertmanager.yml` (bind mount, solo lectura) |
| Token Telegram | `/.runtime/telegram_bot_token` (Docker secret) |

## F. Configuración

| Elemento | Ubicación o estado |
|---|---|
| Compose del servicio | `/opt/infra-prom/docker-compose.yml`, con Prometheus y Alertmanager |
| Variables y secretos | `/opt/infra-prom/perm.env` |
| Persistencia propia | Volúmenes Docker: `prom_data`, `alert_data` |
| Zona horaria | Pendiente confirmar la zona efectiva de las alertas |

## G. Exporters desplegados en el clúster

CT610 es el punto central de scraping. Los exporters están desplegados en los
17 CT del clúster:

| CT | Servicio | node_exporter | cAdvisor | blackbox_exporter |
|---|---|---|---|---|
| 610 | infra-prom | Sí | Sí | Sí |
| 611 | infra-webui | Sí | Sí | Sí |
| 612 | infra-redis | Sí | Sí | Sí |
| 613 | infra-journal | Sí | Sí | Sí |
| 614 | infra-sgtm | Sí | Sí | Sí |
| 615 | infra-redis2 | Sí | Sí | Sí |
| 616 | infra-redis3 | Sí | Sí | Sí |
| 617 | infra-redis4 | Sí | Sí | Sí |
| 618 | infra-redis5 | Sí | Sí | Sí |
| 619 | infra-pulpo | Sí | Sí | Sí |
| 620 | infra-svc01 | Sí | Sí | Sí |
| 621 | infra-svc02 | Sí | Sí | Sí |
| 622 | infra-svc03 | Sí | Sí | Sí |
| 623 | infra-svc04 | Sí | Sí | Sí |
| 624 | infra-cadvisor | Sí | Sí | Sí |
| 625 | infra-logger | Sí | Sí | Sí |
| 626 | infra-excraper | Sí | Sí | Sí |

## H. Observaciones

- **Discrepancia de disco:** el disco observado es 10 GiB, el declarado 25 GiB.
  Existe una receta de resize en `services/infra-prom/resize-20261114/README.md`
  que reconcilia 10→25 GiB. Pendiente de ejecución.
- **CT legacy:** no tiene bloque `documentation:` en su YAML de Terraform ni
  `legacy_notes` en `documentation.yml`. Se documenta con la estructura
  estándar (`NOTES.md` + ficha de inventario).
- **Recursos observados:** 2048 MiB RAM, 1754620 KiB disponibles (~1.67 GiB).
  Disco libre observado: ~3.7 GiB.