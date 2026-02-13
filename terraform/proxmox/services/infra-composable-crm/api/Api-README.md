# Composable CRM API (API-first)

## Overview
This service exposes the CRM as an API-first backend over Postgres (source of truth).  
UI clients (Budibase, custom UI) and automations (n8n) must consume this API rather than connecting directly to the DB.

- Front (Budibase): https://infra-svc01.mailerblend.com/
- API base: https://infra-svc01.mailerblend.com/api/
- Swagger: https://infra-svc01.mailerblend.com/api/docs
- OpenAPI JSON: https://infra-svc01.mailerblend.com/api/openapi.json

## Runtime Architecture
- Postgres in LAN (source of truth)
- CRM API (FastAPI) connects to Postgres using a dedicated user
- Edge-router (Nginx) terminates TLS and routes:
  - `/` -> Budibase
  - `/api/` -> CRM API

## Environment variables
Required:
- `CRM_DB_DSN` = Postgres DSN for application user
- `CRM_API_KEY` = shared secret API key (header-based)
- `CRM_BASE_PATH` = `/api` in production, empty in local dev

Example:
CRM_DB_DSN="postgresql://crm_api:***@192.168.1.118:5432/<db>?sslmode=disable"
CRM_API_KEY="change-me"
CRM_BASE_PATH="/api"

## Authentication
Header-based API key (v1 baseline):
- Header: `X-API-Key: <CRM_API_KEY>`

Later upgrade path:
- JWT for users + service accounts
- Keep `X-API-Key` for machine-to-machine (n8n, webhooks) if needed

## Health endpoints
- `GET /health` -> liveness
- `GET /ready` -> checks DB connectivity (SELECT 1)

## Core resources (v1)
- Contacts (lead/contact)
- Opportunities
- Timeline (activity log)
- Tasks
- Quotes/Invoices
- Offline conversions
- LinkedIn sourcing tables (optional)

## How to add a new table/resource
1) Add a DB migration (SQL) in `migrations/`:
   - `V2__add_<feature>.sql`
2) Run migrations via Flyway (in compose)
3) Create a router:
   - `app/routers/<resource>.py`
4) Create Pydantic schemas:
   - `app/schemas/<resource>.py`
5) Add queries in:
   - `app/db/<resource>.py`
6) Register router in `app/main.py`
7) Add endpoints to OpenAPI automatically (FastAPI)
8) Add at least:
   - list (GET)
   - create (POST)
   - get-by-id (GET)
   - patch (PATCH)

## How to expose Views / Materialized Views
Budibase can SELECT from views. The API can also read views:
- Prefer READ-only endpoints for views.
- Example: `GET /v1/analytics/<view_name>`
- Security: never allow arbitrary view names from user input (whitelist).

## n8n integration patterns
### Pattern A: n8n calls the API (recommended)
- n8n uses `HTTP Request` nodes against:
  - `POST /v1/contacts`
  - `POST /v1/contacts/{id}/timeline`
  - `POST /v1/opportunities`
- Authenticate with `X-API-Key`.

### Pattern B: Webhooks -> API -> DB (recommended for inbound)
- API provides inbound webhooks:
  - `POST /v1/webhooks/form`
  - `POST /v1/webhooks/linkedin`
- API validates signature/api-key and persists.

### Pattern C: Outbound events (for automations)
Option 1 (simple): n8n polls endpoints:
- `GET /v1/events?since=...`

Option 2 (robust): Outbox table (recommended)
- API writes business change + outbox record in same DB transaction.
- A worker delivers events to n8n webhook:
  - n8n endpoint: `POST https://<n8n-domain>/webhook/<id>`
- This avoids missed events.

## Local development
- Run compose with `CRM_BASE_PATH=""` so docs are at `/docs`
- In production behind Nginx use `CRM_BASE_PATH="/api"`

## Production deployment
- CRM API runs in the same docker network as Budibase (`nucleo_network`)
- Edge-router routes `/api/` to the CRM API service port.

## Conventions
- All endpoints are under `/v1`
- Cursor pagination: `limit` + `cursor`
- All timestamps are ISO-8601 in UTC

Documentación de Cambio de Infraestructura - 2026-02-08
Servicio: infra-svc01.mailerblend.com Acción: Migración de IP y reestructuración de rutas de API.

Cambios realizados:

• Migración de IP: El destino del Proxy Pass se cambió de la IP antigua a la nueva IP interna `192.168.1.118`.
• Nueva Ruta de API Segura: Se creó la ruta genérica `/_svc/` apuntando al puerto `18088`.
• Corrección de Conflicto: Se eliminó la ruta `/api/` del proxy original para evitar colisiones con la API interna de Budibase, que causaba errores 404 en el builder.

Justificación:

1. Seguridad por Oscuridad: El uso de `/_svc/` oculta la naturaleza del microservicio frente a escaneos comunes.
2. Estabilidad (High Availability): Se asegura que el Builder de Budibase funcione correctamente al no interceptar sus llamadas internas a `/api/`.
3. Escalabilidad: Esta estructura permite añadir más servicios bajo rutas seguras sin afectar la aplicación principal.
jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ curl -sS https://infra-svc01.mailerblend.com/_svc/health
{"status":"ok"}jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ curl -sS https://infra-svc01.mailerblend.com/_svc/ready
{"db":"ok"}jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ curl -I  https://infra-svc01.mailerblend.com/_svc/docs
HTTP/2 200 
server: nginx/1.18.0 (Ubuntu)
date: Sun, 08 Feb 2026 20:20:23 GMT
content-type: text/html; charset=utf-8
content-length: 950
jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$ 