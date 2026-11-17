# infra-pulpo (CT 619)

## Rol

Servidor de automatización n8n para el proyecto **LinkedIn Stealth Sourcing**.
Orquesta la búsqueda de leads en LinkedIn, el enriquecimiento, la selección de
plantillas de invitación (A/B) y el registro de actividad. Contiene n8n y su base
de datos PostgreSQL.

## Componentes

| Componente | Detalle |
|------------|---------|
| n8n | v2.8.3, contenedor `infra-pulpo-n8n-1`, base de datos PostgreSQL 16 |
| PostgreSQL | contenedor `infra-pulpo-postgres-1`, volumen `n8n_postgres_data` (67 MB) |
| Workflows | 11 definidos; **ninguno activo** (ver estado en el proyecto) |

## Endpoints y puertos

| Puerto | Servicio | Notas |
|--------|----------|-------|
| 5678 | n8n | UI y API de n8n (interno) |
| 5432 | PostgreSQL | Solo acceso interno desde n8n |

## Workflows (estado observado 2026-11-15)

- `1. LinkedIn Search & Invite - 3 PACKS` — versión canónica (id `1lbacmAUQ2Hne7Fc`,
  42 nodos, con control de presupuesto de invitaciones). **Inactivo.**
- Duplicados de "3 PACKS": `b25FRkdahggQtnuW` y `wezH45QWFXjqC3ep` (38 nodos, sin
  control de presupuesto). **Inactivos.**
- `EVA - Telegram Human Reminders` (id `I5ZFvl8PWNBxQorw`). **Inactivo.**
- 7 workflows archivados (variantes históricas de Search/Import/Enrichment/Health Check).

> La lógica de negocio llama al endpoint `/search/people` del worker de CT 620 y a
> `https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/*` (CRM). No existe
> `/job/search` en el worker (devuelve 404); el endpoint real de búsqueda es
> `/search/people`. Ver `docs/projects/LinkedIn_Stealth_Sourcing_status/WORKFLOWS.md`.

## Configuración

- `.env` en `/opt/infra-pulpo/` (variables n8n; sin credenciales en el inventario).
- Base de datos n8n: PostgreSQL 16, datos en `/var/lib/postgresql/data`.

## Notas operativas

- Acceso: `ssh pve` → `pct exec 619` (SSH directo al CT bloqueado por host key).
- Recursos: 2 vCPU, 2048 MiB RAM, 16 GiB disco (uso observado 5,3 GiB / 58%).
- Todos los workflows están desactivados; no hay ejecución programada activa.

## Fuentes

- `inventory/services/infra-pulpo.yml`
- `docs/inventory/619-LXC-INVENTORY.md`
- `docs/projects/LinkedIn_Stealth_Sourcing_status/`