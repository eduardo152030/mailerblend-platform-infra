# CT 620 — infra-excraper: inventario técnico individual

Ficha principal del worker de scraping/enriquecimiento para el proyecto
**LinkedIn Stealth Sourcing**. Verificado por lectura el **15/11/2026** vía
`ssh pve` → `pct exec 620`; las evidencias conservan sus marcas UTC. Captura de
estado, no garantía futura. Se consultó CT620 y sus dependencias directas
(n8n CT619, CRM infra-svc01).

Fuentes: [inventario declarado](../../inventory/services/infra-excraper.yml),
[observación LXC](../../inventory/lxc-observed.json),
[NOTES operativas](../../services/infra-excraper/NOTES.md).

## A. General Information

| Campo | Valor / verificación |
|---|---|
| CT ID / hostname | 620 / infra-excraper; Proxmox |
| Nodo / estado | pve / running |
| Entorno | Internal: tags `internal`, `automation`; clasificación `Not verified` en metadata |
| IP privada | 192.168.1.120/24 |
| Propósito | Workers de scraping LinkedIn y enriquecimiento de señales |
| Dominio principal | Sin dominio público; acceso interno por IP |
| Endpoint público | Ninguno; workers expuestos en 192.168.1.120:3000/3001 (interno) |
| Infraestructura | Proxmox LXC + Docker Compose |
| CPU / RAM / swap | 2 cores / 2048 MiB / 512 MiB asignados |
| Disco real | `local-lvm:vm-620-disk-0,size=10G` (asignación, no espacio libre) |
| Disco declarado | 20 GiB en YAML; discrepancia no corregida |
| OS del LXC | Ubuntu 22.04.5 LTS (Jammy) |
| Red | vmbr0; gateway 192.168.1.254; firewall de interfaz habilitado |
| Tags observados | `192.168.1.120;automation;infra;internal;linkedin-worker;parte_linkedin_stealth_sourcing;signals-worker` |

## B. Purpose

CT620 ejecuta dos workers para el proyecto **LinkedIn Stealth Sourcing**:

- **linkedin-worker** (Node.js + Playwright): login, búsqueda de personas e
  invitaciones en LinkedIn. Expone `POST /search/people` (endpoint real de
  búsqueda, límite 5 por llamada) y `POST /job/invite`.
- **signals-worker** (Python/Flask): enriquecimiento de señales de empresa con
  Google Places y PageSpeed Insights. Expone `POST /enrich`, `POST /enrich/places`
  y `POST /enrich/batch`.

Ambos workers comparten Redis como cola/estado interno. El worker llama al CRM
en `https://infra-svc01.mailerblend.com` para importar leads y registrar
actividad.

**Nota:** El endpoint `/job/search` que aparece en documentación de negocio
**no existe** en el worker (devuelve 404). La búsqueda real se hace con
`POST /search/people`.

## C. Applications and Components

| Aplicación | Contenedor Docker real | Imagen / versión comprobada | Publicado → interno | Función / estado |
|---|---|---|---|---|
| linkedin-worker | `infra-excraper-linkedin-worker-1` | `mcr.microsoft.com/playwright:v1.41.0-jammy` | 192.168.1.120:3000 → 3000 | Búsqueda e invitaciones LinkedIn; **running** |
| signals-worker | `infra-excraper-signals-worker-1` | `python:3.11-slim` | 192.168.1.120:3001 → 3001 | Enriquecimiento de señales; **running** |
| Redis | `infra-excraper-redis-1` | `redis:7-alpine` | Sin puerto publicado (interno) | Cola/estado; **running**, healthy, dbsize 0 |
| node_exporter | `node_exporter` | `prom/node-exporter@sha256:3ac34ce0…` | 192.168.1.120:9100 → 9100 | Métricas del nodo; **running** |
| cadvisor | `cadvisor` | `ghcr.io/google/cadvisor@sha256:b8e7d109…` | 192.168.1.120:8085 → 8080 | Métricas de contenedores; **running**, healthy |

Contenedores residuales (exited, no activos):
- `cadvisor-pre-phase4-620` — versión anterior pre-Fase 4.

## D. Network and Ports

| Puerto | Dirección | Servicio | Notas |
|---|---|---|---|
| 3000 | 192.168.1.120 | linkedin-worker | Búsqueda e invitaciones LinkedIn |
| 3001 | 192.168.1.120 | signals-worker | Enriquecimiento de señales |
| 9100 | 192.168.1.120 | node_exporter | Métricas Prometheus |
| 8085 | 192.168.1.120 | cadvisor | Métricas de contenedores |
| 6379 | interno (bridge) | Redis | Solo accesible desde workers en la red Docker |

Sin dominio público ni proxy Nginx. Sin reglas de routing observadas en
`routing-observed.json`.

## E. Data and Storage

| Recurso | Detalle |
|---|---|
| Montaje workers | `/opt/infra-excraper/` con `.env` y `docker-compose.yml` |
| Montaje exporters | `/opt/exporter-phase4-pilot/integration-20261102T223431Z-620/` |
| Capturas de pantalla | `SCREENSHOTS_PATH` (login, search, invite) |
| Disco LXC | `local-lvm:vm-620-disk-0,size=10G`; uso observado 5,2 GiB / 57% |
| Redis | dbsize 0 (vacío en el momento de la auditoría) |

## F. Configuration

- `.env` en `/opt/infra-excraper/` con claves: `LINKEDIN_USERNAME`,
  `LINKEDIN_PASSWORD`, `CRM_API_BASE`, `CRM_API_KEY`, `GOOGLE_PLACES_KEY`,
  `PAGESPEED_KEY` (valores fuera del inventario).
- `docker-compose.yml` en `/opt/infra-excraper/` define linkedin-worker,
  signals-worker y redis.
- Compose de exporters en `/opt/exporter-phase4-pilot/integration-20261102T223431Z-620/`.

## G. Endpoints (verificados 2026-11-15)

### linkedin-worker (puerto 3000)

| Método | Ruta | Estado |
|---|---|---|
| GET | `/health` | 200 OK |
| POST | `/login` | Disponible |
| GET/POST | `/search/people` | Disponible (endpoint real de búsqueda) |
| POST | `/job/invite` | Disponible |
| POST | `/job/check-connection` | Disponible |
| POST | `/job/search` | **404 — no implementado** |

> El endpoint `/job/search` que aparece en la documentación de negocio **no existe**
> en el worker. La búsqueda real se hace con `POST /search/people` (límite 5 por
> llamada, rate-limit en memoria).

### signals-worker (puerto 3001)

| Método | Ruta | Detalle |
|---|---|---|
| GET | `/health` | 200 OK |
| POST | `/enrich` | Enriquecimiento principal (Places + PageSpeed) |
| POST | `/enrich/places` | Solo Google Places |
| POST | `/enrich/batch` | Múltiples empresas |

## H. Dependencies

| Dependencia | Dirección | Propósito |
|---|---|---|
| n8n (CT619) | 192.168.1.119:15678 | Orquestación de workflows |
| CRM (infra-svc01) | https://infra-svc01.mailerblend.com | Importación de leads, registro de actividad |
| Google Places API | Externo | Enriquecimiento de empresas |
| PageSpeed Insights API | Externo | Métricas de rendimiento web |
| Redis (interno) | bridge Docker | Cola/estado compartido |

## I. Monitoring

| Componente | Puerto | Notas |
|---|---|---|
| node_exporter | 9100 | Métricas del nodo LXC |
| cadvisor | 8085 | Métricas de contenedores (Fase 4) |
| Prometheus (CT610) | — | Scrapeo de exporters |
| Alertmanager / Telegram | — | Alertas de infraestructura |

## J. Operational Notes

- Acceso: `ssh pve` → `pct exec 620` (SSH directo al CT bloqueado por host key).
- Recursos: 2 vCPU, 2048 MiB RAM, 10 GiB disco real (20 GiB declarado).
- Redis vacío (`dbsize 0`): sin trabajos en cola en el momento de la auditoría.
- El worker llama a `CRM_API_BASE` (infra-svc01) para importar leads y registrar
  actividad.
- Contenedores residuales exited no afectan operación; candidatos a limpieza.

## K. Backup and Recovery

No hay política de backup específica documentada para CT620. Para recuperación:
1. Snapshot del LXC desde Proxmox.
2. Restaurar `.env` y `docker-compose.yml` desde `/opt/infra-excraper/`.
3. Redis no contiene datos persistentes (dbsize 0 observado).

No se ha verificado restauración funcional.

## L. Pending Verification

1. Entorno y responsable operativo por confirmar.
2. Repositorio de aplicación independiente por confirmar.
3. Prueba funcional y dependencias externas pendientes.
4. Discrepancia disco: 20 GiB declarado vs 10 GiB real; no corregida.
5. Limpieza de contenedores residuales exited (2 contenedores).
6. Healthcheck de workers: no configurado; solo redis tiene healthcheck.
7. Verificación de credenciales LinkedIn y API keys (fuera del inventario).

Este archivo es la ficha principal; el índice general solo debe enlazarla.
Revisar fecha/evidencias cuando cambie producción. Notes son su resumen
operativo, no una copia.
- `node_exporter-pre-phase4-620` — versión anterior pre-Fase 4.