# Inventario funcional LXC — generado mediante IaC

No editar este archivo ni las notas generadas manualmente. Fuente: inventario de
recursos, `inventory/documentation.yml`, `inventory/lxc-observed.json` y rutas
Nginx filtradas. Regenerar: `python3 scripts/generate-lxc-inventory.py`.
La observación es una captura fechada; no constituye un monitor en tiempo real.
**Declarado**, **observado** y **funcionalidad confirmada** se muestran por separado.
No se atribuye un dominio por su nombre. Recursos distintos no se reconcilian aquí.

| CT | Servicio | Funcionalidad | IP | Dominio según proxy | Aplicaciones activas | Documentación | Runbook |
|---|---|---|---|---|---|---|---|
| 610 | infra-prom | Recolección de métricas y enrutamiento de alertas | 192.168.1.110 | Not verified | eloquent_ganguly, prometheus, alertmanager | Parcial: observación verificada; funcionalidad pendiente | [PHASE2-EXECUTION.md](../../services/infra-prom/PHASE2-EXECUTION.md) |
| 611 | infra-grafana | Visualización de métricas con Grafana | 192.168.1.111 | Not verified | grafana | Parcial: observación verificada; funcionalidad pendiente | [CRITICAL-D039-EXECUTION.md](../../docs/roadmap/CRITICAL-D039-EXECUTION.md) |
| 613 | infra-hola | Servicio demo hola declarado; aplicación no observada en ejecución | 192.168.1.113 | Not verified | Sin aplicación Docker activa | Parcial: observación verificada; funcionalidad pendiente | [R1-613.md](../../docs/roadmap/R1-613.md) |
| 614 | infra-nucleoedge | Google Tag Manager Server-Side de Núcleo Tecnológico | 192.168.1.114 | edge.nucleotecnologico.es | infra-nucleoedge-sgtm-1, infra-nucleoedge-sgtm_preview-1 | Parcial: observación verificada; funcionalidad pendiente | [614-LXC-INVENTORY.md](../../docs/inventory/614-LXC-INVENTORY.md) |
| 615 | infra-mailerblend-edge | Google Tag Manager Server-Side de Mailerblend | 192.168.1.115 | edge.mailerblend.com | mailerblend-sgtm-serving, mailerblend-sgtm-preview | Parcial: observación verificada; funcionalidad pendiente | [615-LXC-INVENTORY.md](../../docs/inventory/615-LXC-INVENTORY.md) |
| 616 | infra-blackbox | Sondas HTTP externas de disponibilidad | 192.168.1.116 | Not verified | infra-blackbox | Parcial: observación verificada; funcionalidad pendiente | [CRITICAL-D039-EXECUTION.md](../../docs/roadmap/CRITICAL-D039-EXECUTION.md) |
| 617 | infra-orbit | Pasarela de ingestión de analítica y proxy de acceso | 192.168.1.117 | edge.nucleotecnologico.es | analytics-ingest-gateway, orbit-gateway-proxy | Parcial: observación verificada; funcionalidad pendiente | [EXPORTERS-D041-CLOSURE.md](../../docs/roadmap/EXPORTERS-D041-CLOSURE.md) |
| 618 | infra-composable-crm | CRM componible con interfaz Budibase y API | 192.168.1.118 | infra-svc01.mailerblend.com | budibase-app, crm-api, budibase-redis, budibase-couchdb, supabase-db | Parcial: observación verificada; funcionalidad pendiente | [RECOVERY.md](../../services/infra-composable-crm/recovery/RECOVERY.md) |
| 619 | infra-pulpo | Automatización de flujos con n8n | 192.168.1.119 | infra-pulpo.mailerblend.com | infra-pulpo-n8n-1, infra-pulpo-postgres-1 | Parcial: observación verificada; funcionalidad pendiente | [PHASE4-HANDOFF.md](../../docs/roadmap/PHASE4-HANDOFF.md) |
| 620 | infra-excraper | Workers LinkedIn y señales con Redis | 192.168.1.120 | Not verified | infra-excraper-linkedin-worker-1, infra-excraper-signals-worker-1, infra-excraper-redis-1 | Parcial: observación verificada; funcionalidad pendiente | [R2-621-620.md](../../docs/roadmap/R2-621-620.md) |
| 621 | infra-project-gestion | Gestión de proyectos con Focalboard | 192.168.1.121 | Not verified | focalboard | Parcial: observación verificada; funcionalidad pendiente | [R2-621-620.md](../../docs/roadmap/R2-621-620.md) |
| 622 | infra-eva-assistant-bot | Asistente EVA con API, tareas programadas y Focalboard | 192.168.1.122 | infra-eva.mailerblend.com, infra-focalboard.mailerblend.com | eva-cron-digest, eva-sync, eva-scheduler, focalboard, eva-postgres, eva-docker-cleanup, eva-api | Parcial: observación verificada; funcionalidad pendiente | [STORAGE-PLAN.md](../../services/infra-eva-assistant-bot/recovery/STORAGE-PLAN.md) |
| 623 | infra-gestoria | Gestoría con Odoo y PostgreSQL | 192.168.1.123 | Not verified | infra-gestoria-odoo-1, infra-gestoria-db-1, test-nginx | Parcial: observación verificada; funcionalidad pendiente | [PHASE4-HANDOFF.md](../../docs/roadmap/PHASE4-HANDOFF.md) |
| 624 | infra-journal-web | Interfaz web de Journal TradeIntuit | 192.168.1.124 | app.tradeintuit.com | infra-journal-web-web-1, test-nginx | Parcial: observación verificada; funcionalidad pendiente | [JOURNAL-EXECUTION.md](../../docs/roadmap/JOURNAL-EXECUTION.md) |
| 625 | infra-journal-db | PostgreSQL de Journal TradeIntuit | 192.168.1.125 | Not verified | infra-journal-db-db-1, test-nginx | Parcial: observación verificada; funcionalidad pendiente | [JOURNAL-EXECUTION.md](../../docs/roadmap/JOURNAL-EXECUTION.md) |
| 626 | infra-journal-api | API de Journal TradeIntuit | 192.168.1.126 | app.tradeintuit.com | infra-journal-api-api-1, test-nginx | Parcial: observación verificada; funcionalidad pendiente | [JOURNAL-EXECUTION.md](../../docs/roadmap/JOURNAL-EXECUTION.md) |
| 61211 | svc01 | Plataforma NocoDB con PostgreSQL | 192.168.1.112 | Not verified | infra-svc01-nocodb, infra-svc01-nocodb-db | Parcial: observación verificada; funcionalidad pendiente | [CT61211-D037-EXECUTION.md](../../docs/roadmap/CT61211-D037-EXECUTION.md) |

## CT 610 — infra-prom

**Función:** Recolección de métricas y enrutamiento de alertas
**Entorno:** Not verified | **Categoría:** Observabilidad
**Proyecto:** infra-prom | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 610 | IP 192.168.1.110/24 | CPU 2 | RAM 2048 MiB | disco 25 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 2 | RAM 2048 MiB | rootfs local-lvm:vm-610-disk-0,size=10G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- eloquent_ganguly: Not verified: Alertmanager adicional sin puertos publicados; puertos sin publicación; Docker not configured; imagen prom/alertmanager:v0.33.0
- prometheus: Series temporales y evaluación de reglas; puertos *:9090->9090/tcp; Docker not configured; imagen prom/prometheus:v3.12.0
- alertmanager: Agrupación y envío de alertas Telegram; puertos *:9093->9093/tcp; Docker not configured; imagen prom/alertmanager:v0.33.0

**Dominios:** Not verified (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** Not verified / no depends_on declarado
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: eloquent_ganguly: not configured; prometheus: not configured; alertmanager: not configured
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261106T174253610Z-610/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261106T174253610Z-610/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T174253610Z-610/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261106T174253610Z-610/node.yml,/opt/exporter-phase4-pilot/integration-20261106T174253610Z-610/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T174253610Z-610/node-cgroup.yml; /opt/infra-prom/docker-compose.yml
- IaC: inventory/services/infra-prom.yml; services/infra-prom/ (puede contener configuración histórica; contrastar con activa).
- Runbook: services/infra-prom/PHASE2-EXECUTION.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** node_exporter-pre-phase4-610, cadvisor-pre-phase4-610

**Nota previa conservada:** Managed by Terraform - Service: infra-prom

## CT 611 — infra-grafana

**Función:** Visualización de métricas con Grafana
**Entorno:** Not verified | **Categoría:** Observabilidad
**Proyecto:** infra-grafana | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 611 | IP 192.168.1.111/24 | CPU 1 | RAM 1048 MiB | disco 15 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 1 | RAM 1048 MiB | rootfs local-lvm:vm-611-disk-0,size=10G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- grafana: Dashboards y consulta de métricas; puertos *:3010->3000/tcp; Docker not configured; imagen grafana/grafana:latest

**Dominios:** Not verified (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** Not verified / no depends_on declarado
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: grafana: not configured
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261106T174253611Z-611/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261106T174253611Z-611/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T174253611Z-611/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261106T174253611Z-611/node.yml,/opt/exporter-phase4-pilot/integration-20261106T174253611Z-611/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T174253611Z-611/node-cgroup.yml; /opt/infra-grafana/docker-compose.yml
- IaC: inventory/services/infra-grafana.yml; services/infra-grafana/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/CRITICAL-D039-EXECUTION.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-pre-phase4-611, node_exporter-pre-phase4-611

**Nota previa conservada:** Managed by Terraform - Service: infra-grafana

## CT 613 — infra-hola

**Función:** Servicio demo hola declarado; aplicación no observada en ejecución
**Entorno:** Not verified | **Categoría:** Demostración
**Proyecto:** infra-hola | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 613 | IP 192.168.1.113/24 | CPU 1 | RAM 512 MiB | disco 8 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 1 | RAM 512 MiB | rootfs local-lvm:vm-613-disk-0,size=10G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- No se observaron contenedores de aplicación activos.

**Dominios:** Not verified (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** Not verified / no depends_on declarado
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: Aplicación: Not verified
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261102T204936Z-613/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261102T204936Z-613/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T204936Z-613/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261102T204936Z-613/node.yml,/opt/exporter-phase4-pilot/integration-20261102T204936Z-613/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T204936Z-613/node-cgroup.yml
- IaC: inventory/services/infra-hola.yml; services/infra-hola/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/R1-613.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes; Compose declara hola, pero no se observó su contenedor activo

**Conservados detenidos (no reactivar automáticamente):** node_exporter-pre-phase4-613, cadvisor-pre-phase4-613

**Nota previa conservada:** Managed by Terraform - Service: infra-hola

## CT 614 — infra-nucleoedge

Ficha principal: [614-LXC-INVENTORY.md](../../docs/inventory/614-LXC-INVENTORY.md). No duplicar aquí su contenido.

## CT 615 — infra-mailerblend-edge

Ficha principal: [615-LXC-INVENTORY.md](../../docs/inventory/615-LXC-INVENTORY.md). No duplicar aquí su contenido.

## CT 616 — infra-blackbox

**Función:** Sondas HTTP externas de disponibilidad
**Entorno:** Not verified | **Categoría:** Observabilidad
**Proyecto:** infra-blackbox | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 616 | IP 192.168.1.116/24 | CPU 1 | RAM 512 MiB | disco 8 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 1 | RAM 512 MiB | rootfs local-lvm:vm-616-disk-0,size=10G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- infra-blackbox: Blackbox Exporter: comprobación de endpoints; puertos 0.0.0.0:9115->9115/tcp; Docker not configured; imagen prom/blackbox-exporter:v0.25.0

**Dominios:** Not verified (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** Not verified / no depends_on declarado
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: infra-blackbox: not configured
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261106T174253616Z-616/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261106T174253616Z-616/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T174253616Z-616/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261106T174253616Z-616/node.yml,/opt/exporter-phase4-pilot/integration-20261106T174253616Z-616/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T174253616Z-616/node-cgroup.yml; /opt/infra-blackbox/docker-compose.yml
- IaC: inventory/services/infra-blackbox.yml; services/infra-blackbox/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/CRITICAL-D039-EXECUTION.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-pre-phase4-616, node_exporter-pre-phase4-616

**Nota previa conservada:** Managed by Terraform - Service: infra-blackbox

## CT 617 — infra-orbit

**Función:** Pasarela de ingestión de analítica y proxy de acceso
**Entorno:** Not verified | **Categoría:** Analítica
**Proyecto:** infra-orbit | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 617 | IP 192.168.1.117/24 | CPU 1 | RAM 512 MiB | disco 8 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 1 | RAM 512 MiB | rootfs local-lvm:vm-617-disk-0,size=10G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- analytics-ingest-gateway: Recepción de solicitudes; entrega final Not verified; puertos sin publicación; Docker not configured; imagen infra-orbit-ingest-gateway
- orbit-gateway-proxy: Proxy Nginx de acceso a ingest-gateway; puertos *:18088->8080/tcp; Docker not configured; imagen nginx:1.25-alpine

**Dominios:** edge.nucleotecnologico.es (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** orbit-gateway-proxy -> ingest-gateway
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: analytics-ingest-gateway: not configured; orbit-gateway-proxy: not configured
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261106T191534617Z-617/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261106T191534617Z-617/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T191534617Z-617/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261106T191534617Z-617/node.yml,/opt/exporter-phase4-pilot/integration-20261106T191534617Z-617/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T191534617Z-617/node-cgroup.yml; /opt/infra-orbit/docker-compose.yml
- IaC: inventory/services/infra-orbit.yml; services/infra-orbit/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/EXPORTERS-D041-CLOSURE.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-phase4-617-held, node_exporter-phase4-617-held, node_exporter-pre-phase4-617, cadvisor-pre-phase4-617

**Nota previa conservada:** Managed by Terraform - Service: infra-orbit

## CT 618 — infra-composable-crm

**Función:** CRM componible con interfaz Budibase y API
**Entorno:** Not verified | **Categoría:** Aplicación
**Proyecto:** infra-composable-crm | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 618 | IP 192.168.1.118/24 | CPU 2 | RAM 6144 MiB | disco 50 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 2 | RAM 6144 MiB | rootfs local-lvm:vm-618-disk-0,size=50G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- budibase-app: Interfaz CRM Budibase 3.27.4 recuperada; puertos 192.168.1.118:8080->80/tcp; Docker unhealthy; imagen budibase/budibase@sha256:5c5c995643132864ea017af2b838e35506b37977ea5c0f379c059d9cce1f0bfa
- crm-api: API del CRM; puertos 192.168.1.118:18088->8080/tcp; Docker unhealthy; imagen infra-composable-crm/crm-api:local
- budibase-redis: Caché y coordinación Budibase; puertos sin publicación; Docker healthy; imagen redis:7-alpine
- budibase-couchdb: Persistencia Budibase; puertos sin publicación; Docker not configured; imagen couchdb:3
- supabase-db: PostgreSQL del CRM; puertos 192.168.1.118:5432->5432/tcp; Docker healthy; imagen postgres:16-alpine

**Dominios:** infra-svc01.mailerblend.com (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** budibase-app -> redis, couchdb; budibase-worker -> redis, couchdb
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: budibase-app: configured (command withheld); crm-api: configured (command withheld); budibase-redis: configured (command withheld); budibase-couchdb: not configured; supabase-db: configured (command withheld)
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261106T191534618Z-618/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261106T191534618Z-618/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T191534618Z-618/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261106T191534618Z-618/node.yml,/opt/exporter-phase4-pilot/integration-20261106T191534618Z-618/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T191534618Z-618/node-cgroup.yml; /opt/infra-composable-crm/budibase/docker-compose.yml; /opt/infra-composable-crm/budibase/docker-compose.yml,/opt/infra-composable-crm/budibase/docker-compose.recovery.yml; /opt/infra-composable-crm/crm-api/docker-compose.yml; /opt/infra-composable-crm/supabase/docker-compose.yml
- IaC: inventory/services/infra-composable-crm.yml; services/infra-composable-crm/ (puede contener configuración histórica; contrastar con activa).
- Runbook: services/infra-composable-crm/recovery/RECOVERY.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-phase4-618-framework-1aa5f3e714bf-held, node_exporter-phase4-618-framework-1aa5f3e714bf-held, node_exporter-pre-phase4-618, cadvisor-pre-phase4-618, budibase-app-pre-recovery, budibase-worker

**Nota previa conservada:** Managed by Terraform - Service: infra-composable-crm

## CT 619 — infra-pulpo

**Función:** Automatización de flujos con n8n
**Entorno:** Not verified | **Categoría:** Automatización
**Proyecto:** infra-pulpo | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 619 | IP 192.168.1.119/24 | CPU 2 | RAM 2048 MiB | disco 16 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 2 | RAM 2048 MiB | rootfs local-lvm:vm-619-disk-0,size=10G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- infra-pulpo-n8n-1: Editor y ejecución de flujos; puertos 192.168.1.119:15678->5678/tcp; Docker not configured; imagen n8nio/n8n:latest
- infra-pulpo-postgres-1: Persistencia de n8n; puertos sin publicación; Docker healthy; imagen postgres:16-alpine

**Dominios:** infra-pulpo.mailerblend.com (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** n8n -> postgres
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: infra-pulpo-n8n-1: not configured; infra-pulpo-postgres-1: configured (command withheld)
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261102T223431Z-619/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-619/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-619/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261102T223431Z-619/node.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-619/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-619/node-cgroup.yml; /opt/infra-pulpo/docker-compose.yml
- IaC: inventory/services/infra-pulpo.yml; services/infra-pulpo/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/PHASE4-HANDOFF.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-phase4-619-rejected-1, cadvisor-pre-phase4-619, node_exporter-pre-phase4-619

**Nota previa conservada:** Managed by Terraform - Service: infra-pulpo

## CT 620 — infra-excraper

**Función:** Workers LinkedIn y señales con Redis
**Entorno:** Not verified | **Categoría:** Automatización
**Proyecto:** infra-excraper | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 620 | IP 192.168.1.120/24 | CPU 2 | RAM 2048 MiB | disco 20 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 2 | RAM 2048 MiB | rootfs local-lvm:vm-620-disk-0,size=10G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- infra-excraper-linkedin-worker-1: Worker LinkedIn; alcance funcional Pending documentation; puertos *:3000->3000/tcp; Docker not configured; imagen mcr.microsoft.com/playwright:v1.41.0-jammy
- infra-excraper-signals-worker-1: Procesamiento de señales; alcance funcional Pending documentation; puertos *:3001->3001/tcp; Docker not configured; imagen python:3.11-slim
- infra-excraper-redis-1: Cola/caché compartida; puertos sin publicación; Docker healthy; imagen redis:7-alpine

**Dominios:** Not verified (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** linkedin-worker -> redis; signals-worker -> redis
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: infra-excraper-linkedin-worker-1: not configured; infra-excraper-signals-worker-1: not configured; infra-excraper-redis-1: configured (command withheld)
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261102T223431Z-620/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-620/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-620/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261102T223431Z-620/node.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-620/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-620/node-cgroup.yml; /opt/infra-excraper/docker-compose.yml
- IaC: inventory/services/infra-excraper.yml; services/infra-excraper/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/R2-621-620.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-pre-phase4-620, node_exporter-pre-phase4-620

**Nota previa conservada:** Managed by Terraform - Service: infra-excraper

## CT 621 — infra-project-gestion

**Función:** Gestión de proyectos con Focalboard
**Entorno:** Not verified | **Categoría:** Aplicación
**Proyecto:** infra-project-gestion | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 621 | IP 192.168.1.121/24 | CPU 2 | RAM 2048 MiB | disco 12 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 2 | RAM 2048 MiB | rootfs local-lvm:vm-621-disk-0,size=10G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- focalboard: Tableros de gestión de proyectos; puertos *:8081->8000/tcp; Docker not configured; imagen mattermost/focalboard:7.10.0

**Dominios:** Not verified (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** Not verified / no depends_on declarado
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: focalboard: not configured
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261102T223431Z-621/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-621/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-621/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261102T223431Z-621/node.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-621/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-621/node-cgroup.yml; /opt/infra-project-gestion/docker-compose.yml
- IaC: inventory/services/infra-project-gestion.yml; services/infra-project-gestion/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/R2-621-620.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** node_exporter-pre-phase4-621, cadvisor-pre-phase4-621

**Nota previa conservada:** Managed by Terraform - Service: infra-project-gestion

## CT 622 — infra-eva-assistant-bot

**Función:** Asistente EVA con API, tareas programadas y Focalboard
**Entorno:** Not verified | **Categoría:** Aplicación
**Proyecto:** infra-eva-assistant-bot | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 622 | IP 192.168.1.122/24 | CPU 2 | RAM 2048 MiB | disco 12 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 2 | RAM 2048 MiB | rootfs local-lvm:vm-622-disk-0,size=40G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- eva-cron-digest: Resúmenes periódicos; puertos sin publicación; Docker not configured; imagen sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659
- eva-sync: Sincronización EVA/Focalboard; puertos sin publicación; Docker not configured; imagen sha256:aa054e4001f73fc2b3a62ea1e347b3701e2e9f01afeeae9d5678e095df058fdb
- eva-scheduler: Tareas programadas; puertos sin publicación; Docker not configured; imagen sha256:aa054e4001f73fc2b3a62ea1e347b3701e2e9f01afeeae9d5678e095df058fdb
- focalboard: Tableros de trabajo; puertos *:8002->8000/tcp; Docker unhealthy; imagen sha256:337346b132a7c1bd988b5fea59a9050ade42b9855399b0add5f95cf8f99ba800
- eva-postgres: Persistencia PostgreSQL; puertos sin publicación; Docker healthy; imagen sha256:20edbde7749f822887a1a022ad526fde0a47d6b2be9a8364433605cf65099416
- eva-docker-cleanup: Mantenimiento Docker existente; no ejecutado aquí; puertos sin publicación; Docker not configured; imagen sha256:17b5c235f40be7432a7c0914c154e9278aed63bad4afe5607e4f91840696a9f8
- eva-api: API del asistente EVA; puertos *:8001->8000/tcp; Docker healthy; imagen sha256:aa054e4001f73fc2b3a62ea1e347b3701e2e9f01afeeae9d5678e095df058fdb

**Dominios:** infra-eva.mailerblend.com, infra-focalboard.mailerblend.com (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** eva-api -> postgres; eva-scheduler -> postgres; eva-sync -> postgres, focalboard; eva-cron-digest -> eva-api; focalboard -> postgres
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: eva-cron-digest: not configured; eva-sync: not configured; eva-scheduler: not configured; focalboard: configured (command withheld); eva-postgres: configured (command withheld); eva-docker-cleanup: not configured; eva-api: configured (command withheld)
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261106T174253622Z-622/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261106T174253622Z-622/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T174253622Z-622/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261106T174253622Z-622/node.yml,/opt/exporter-phase4-pilot/integration-20261106T174253622Z-622/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T174253622Z-622/node-cgroup.yml; /opt/infra-eva-assistant-bot/docker-compose.storage-recovery.yml
- IaC: inventory/services/infra-eva-assistant-bot.yml; services/infra-eva-assistant-bot/ (puede contener configuración histórica; contrastar con activa).
- Runbook: services/infra-eva-assistant-bot/recovery/STORAGE-PLAN.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** eva-api-pre-storage-recovery, eva-scheduler-pre-storage-recovery, eva-sync-pre-storage-recovery, eva-docker-cleanup-pre-storage-recovery, focalboard-pre-storage-recovery, eva-postgres-pre-storage-recovery, eva-cron-digest-pre-storage-recovery, cadvisor-pre-phase4-622, node_exporter-pre-phase4-622

**Nota previa conservada:** Managed by Terraform - Service: infra-eva-assistant-bot

## CT 623 — infra-gestoria

**Función:** Gestoría con Odoo y PostgreSQL
**Entorno:** Not verified | **Categoría:** Aplicación
**Proyecto:** infra-gestoria | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 623 | IP 192.168.1.123/24 | CPU 2 | RAM 4096 MiB | disco 20 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 2 | RAM 4096 MiB | rootfs local-lvm:vm-623-disk-0,size=50G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- infra-gestoria-odoo-1: Gestión empresarial Odoo 17; puertos 127.0.0.1:8069->8069/tcp; Docker not configured; imagen odoo:17
- infra-gestoria-db-1: Persistencia de Odoo; puertos sin publicación; Docker not configured; imagen postgres:15
- test-nginx: Not verified: función pendiente; puertos *:8080->80/tcp; Docker not configured; imagen nginx:alpine

**Dominios:** Not verified (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** odoo -> db
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: infra-gestoria-odoo-1: not configured; infra-gestoria-db-1: not configured; test-nginx: not configured
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261102T223431Z-623/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-623/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-623/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261102T223431Z-623/node.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-623/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261102T223431Z-623/node-cgroup.yml; /opt/infra-gestoria/docker-compose.yml; /root/docker-test/docker-compose.yml
- IaC: inventory/services/infra-gestoria.yml; services/infra-gestoria/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/PHASE4-HANDOFF.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-phase4-623-rejected-1, cadvisor-pre-phase4-623, node_exporter-pre-phase4-623

**Nota previa conservada:** Managed by Terraform - Service: infra-gestoria

## CT 624 — infra-journal-web

**Función:** Interfaz web de Journal TradeIntuit
**Entorno:** Not verified | **Categoría:** Aplicación
**Proyecto:** TradeIntuit Journal | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 624 | IP 192.168.1.124/24 | CPU 1 | RAM 512 MiB | disco 8 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 1 | RAM 512 MiB | rootfs local-lvm:vm-624-disk-0,size=50G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- infra-journal-web-web-1: Interfaz web mediante Nginx; puertos 192.168.1.124:8090->80/tcp; Docker not configured; imagen nginx:alpine
- test-nginx: Interfaz web mediante Nginx; puertos *:8080->80/tcp; Docker not configured; imagen nginx:alpine

**Dominios:** app.tradeintuit.com (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** Not verified / no depends_on declarado
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: infra-journal-web-web-1: not configured; test-nginx: not configured
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/pilot-624-20261102T161242+0100/cadvisor.yml,/opt/exporter-phase4-pilot/pilot-624-20261102T161242+0100/cadvisor-limits.yml,/opt/exporter-phase4-pilot/pilot-624-20261102T161242+0100/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/pilot-624-20261102T161242+0100/node.yml,/opt/exporter-phase4-pilot/pilot-624-20261102T161242+0100/node-limits.yml,/opt/exporter-phase4-pilot/pilot-624-20261102T161242+0100/node-cgroup.yml; /opt/infra-journal-web/docker-compose.yml; /root/docker-test/docker-compose.yml
- IaC: inventory/services/infra-journal-web.yml; services/infra-journal-web/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/JOURNAL-EXECUTION.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-phase4-624-rejected-1, node_exporter-phase4-624-rejected-2, cadvisor-pre-phase4-624

**Nota previa conservada:** Managed by Terraform - Service: infra-journal-web

## CT 625 — infra-journal-db

**Función:** PostgreSQL de Journal TradeIntuit
**Entorno:** Not verified | **Categoría:** Base de datos
**Proyecto:** TradeIntuit Journal | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 625 | IP 192.168.1.125/24 | CPU 2 | RAM 2048 MiB | disco 8 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 2 | RAM 2048 MiB | rootfs local-lvm:vm-625-disk-0,size=50G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- infra-journal-db-db-1: Persistencia PostgreSQL del Journal; puertos 192.168.1.125:5432->5432/tcp; Docker not configured; imagen postgres:16-alpine
- test-nginx: Not verified: función pendiente; puertos *:8080->80/tcp; Docker not configured; imagen nginx:alpine

**Dominios:** Not verified (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** Not verified / no depends_on declarado
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: infra-journal-db-db-1: not configured; test-nginx: not configured
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/journal-20261102T190629Z-625/cadvisor.yml,/opt/exporter-phase4-pilot/journal-20261102T190629Z-625/cadvisor-limits.yml,/opt/exporter-phase4-pilot/journal-20261102T190629Z-625/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/journal-20261102T190629Z-625/node.yml,/opt/exporter-phase4-pilot/journal-20261102T190629Z-625/node-limits.yml,/opt/exporter-phase4-pilot/journal-20261102T190629Z-625/node-cgroup.yml; /opt/infra-journal-db/docker-compose.yml; /root/docker-test/docker-compose.yml
- IaC: inventory/services/infra-journal-db.yml; services/infra-journal-db/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/JOURNAL-EXECUTION.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-pre-phase4-625

**Nota previa conservada:** Managed by Terraform - Service: infra-journal-db

## CT 626 — infra-journal-api

**Función:** API de Journal TradeIntuit
**Entorno:** Not verified | **Categoría:** Aplicación
**Proyecto:** TradeIntuit Journal | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 626 | IP 192.168.1.126/24 | CPU 2 | RAM 2048 MiB | disco 8 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 2 | RAM 2048 MiB | rootfs local-lvm:vm-626-disk-0,size=50G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- infra-journal-api-api-1: API del Journal; contratos funcionales Pending documentation; puertos 192.168.1.126:3000->3000/tcp; Docker not configured; imagen infra-journal-api-api
- test-nginx: Not verified: función pendiente; puertos *:8080->80/tcp; Docker not configured; imagen nginx:alpine

**Dominios:** app.tradeintuit.com (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** Not verified / no depends_on declarado
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: infra-journal-api-api-1: not configured; test-nginx: not configured
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/journal-20261102T190629Z-626/cadvisor.yml,/opt/exporter-phase4-pilot/journal-20261102T190629Z-626/cadvisor-limits.yml,/opt/exporter-phase4-pilot/journal-20261102T190629Z-626/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/journal-20261102T190629Z-626/node.yml,/opt/exporter-phase4-pilot/journal-20261102T190629Z-626/node-limits.yml,/opt/exporter-phase4-pilot/journal-20261102T190629Z-626/node-cgroup.yml; /opt/infra-journal-api/docker-compose.yml; /root/docker-test/docker-compose.yml
- IaC: inventory/services/infra-journal-api.yml; services/infra-journal-api/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/JOURNAL-EXECUTION.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes

**Conservados detenidos (no reactivar automáticamente):** cadvisor-pre-phase4-626

**Nota previa conservada:** Managed by Terraform - Service: infra-journal-api

## CT 61211 — svc01

**Función:** Plataforma NocoDB con PostgreSQL
**Entorno:** Not verified | **Categoría:** Aplicación
**Proyecto:** svc01 | **Ciclo de vida:** En servicio (LXC en ejecución; aceptación funcional independiente)

**Infraestructura declarada:** CT 61211 | IP 192.168.1.112/24 | CPU 3 | RAM 6656 MiB | disco 40 GiB
**Observada (2026-11-06T21:45:05.721883+00:00):** nodo pve | status: running | CPU 3 | RAM 6656 MiB | rootfs local-lvm:vm-61211-disk-0,size=40G | SO Ubuntu 22.04.5 LTS

**Aplicaciones observadas (estado de proceso, no prueba funcional):**
- infra-svc01-nocodb: Interfaz de gestión de datos NocoDB; puertos *:18080->8080/tcp; Docker not configured; imagen nocodb/nocodb:latest
- infra-svc01-nocodb-db: Persistencia PostgreSQL de NocoDB; puertos sin publicación; Docker healthy; imagen postgres:16-alpine

**Dominios:** Not verified (asociación de upstream en Nginx CT109; no prueba pública extremo a extremo).
**Dependencias declaradas en Compose:** nocodb -> db
Dependencias externas y su disponibilidad: Not verified.

**Operación:**
- Healthchecks: infra-svc01-nocodb: not configured; infra-svc01-nocodb-db: configured (command withheld)
- Monitorización: Node Exporter :9100, cAdvisor :8085; aceptación F4 D041. Estado actual de targets: comprobar Prometheus, no inferir de Docker.
- Alertas: Prometheus -> Alertmanager -> Telegram; cobertura específica de aplicación Not verified.
- Despliegue: Compose del servicio y procedimiento del runbook; no usar deploy-all.
- Configuración activa observada: /opt/exporter-phase4-pilot/integration-20261106T12344561211Z-61211/cadvisor.yml,/opt/exporter-phase4-pilot/integration-20261106T12344561211Z-61211/cadvisor-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T12344561211Z-61211/cadvisor-containerd.yml; /opt/exporter-phase4-pilot/integration-20261106T12344561211Z-61211/node.yml,/opt/exporter-phase4-pilot/integration-20261106T12344561211Z-61211/node-limits.yml,/opt/exporter-phase4-pilot/integration-20261106T12344561211Z-61211/node-cgroup.yml; /opt/infra-svc01/docker-compose.yml
- IaC: inventory/services/infra-svc01.yml; services/infra-svc01/ (puede contener configuración histórica; contrastar con activa).
- Runbook: docs/roadmap/CT61211-D037-EXECUTION.md

**Repositorio IaC:** https://github.com/eduardo152030/mailerblend-platform-infra
**Repositorio de aplicación:** Not verified
**Funcionalidad confirmada:** Not verified: esta tarea no certifica funcionalidad de negocio
**Pendiente:** Entorno y responsable operativo por confirmar; Repositorio de aplicación independiente por confirmar; Prueba funcional y dependencias externas pendientes; README histórico atribuye infra-svc01.mailerblend.com a NocoDB, pero Nginx observado lo dirige a CT 618; no atribuir dominio a CT 61211

**Conservados detenidos (no reactivar automáticamente):** cadvisor-phase4-61211-ram-v1-held, node_exporter-phase4-61211-ram-v1-held, node_exporter-pre-phase4-61211, cadvisor-pre-phase4-61211

**Nota previa conservada:** Managed by Terraform - Service: svc01
