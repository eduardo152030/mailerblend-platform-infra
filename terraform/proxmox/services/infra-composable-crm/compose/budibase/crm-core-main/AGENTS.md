# AGENTS.md

## Rules

- Routing: `/` renders the access screen outside the app shell; every other page is nested under `CRMLayout` via a layout route, and the CRM Dashboard is served at `/dashboard`. Keep `crmOptions` entry points and the sidebar nav items aligned with those routes.
