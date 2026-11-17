# infra-excraper (CT 620)

## Rol

Worker de scraping/enriquecimiento para el proyecto **LinkedIn Stealth Sourcing**.
Ejecuta dos workers: `linkedin-worker` (búsqueda e invitaciones en LinkedIn vía
Playwright) y `signals-worker` (enriquecimiento de señales de empresa con Google
Places y PageSpeed Insights).

## Componentes

| Componente | Puerto | Detalle |
|------------|--------|---------|
| linkedin-worker | 3000 | Node.js + Playwright; login, búsqueda e invitaciones |
| signals-worker | 3001 | Python/Flask; enriquecimiento de empresas |
| Redis | 6379 | Cola/estado interno (dbsize 0 observado) |

## Endpoints (verificados 2026-11-15)

### linkedin-worker (puerto 3000)

| Método | Ruta | Estado |
|--------|------|--------|
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
|--------|------|---------|
| GET | `/health` | 200 OK |
| POST | `/enrich` | Enriquecimiento principal (Places + PageSpeed) |
| POST | `/enrich/places` | Solo Google Places |
| POST | `/enrich/batch` | Múltiples empresas |

## Configuración

- `.env` en `/opt/infra-excraper/` con claves: `LINKEDIN_USERNAME`,
  `LINKEDIN_PASSWORD`, `CRM_API_BASE`, `CRM_API_KEY`, `GOOGLE_PLACES_KEY`,
  `PAGESPEED_KEY` (valores fuera del inventario).
- Capturas de pantalla en `SCREENSHOTS_PATH` (login, search, invite).

## Notas operativas

- Acceso: `ssh pve` → `pct exec 620` (SSH directo al CT bloqueado por host key).
- Recursos: 2 vCPU, 2048 MiB RAM, 20 GiB disco (uso observado 5,2 GiB / 57%).
- Redis vacío (`dbsize 0`): sin trabajos en cola en el momento de la auditoría.
- El worker llama a `CRM_API_BASE` (infra-svc01) para importar leads y registrar
  actividad.

## Fuentes

- `inventory/services/infra-excraper.yml`
- `docs/inventory/620-LXC-INVENTORY.md`
- `docs/projects/LinkedIn_Stealth_Sourcing_status/`