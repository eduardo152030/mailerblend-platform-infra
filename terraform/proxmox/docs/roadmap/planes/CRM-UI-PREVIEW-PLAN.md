# CT618 — preparación de preview CRM UI

[Issue #24](https://github.com/eduardo152030/mailerblend-platform-infra/issues/24).
Fase 7, IN PROGRESS, 19/11/2026 Europe/Madrid.
Rama `feat/crm-ui-preview`, worktree hermano `mailerblend-platform-infra-crm-preview`,
SHA inicial `18743981dc27135879e4e9f321eab43fc08b4088`.

Lovable trasladado a [compose/crm-ui](../../../services/infra-composable-crm/compose/crm-ui/),
incluidas guías y prompts. Se sincronizó el lockfile npm para instalación limpia.
Dockerfile multietapa con digests verificados, Nginx con health y fallback SPA,
Compose publicado solo en loopback. La UI usa `/_svc/v1` relativo. Nginx
responde 503 para esa ruta y CSP limita conexiones al mismo origen. Sin
upstream real, hostname externo ni datos CRM.

Instalación limpia, build, typecheck, lint del cliente y Vitest PASS con
Node 22.23.1 y npm 10.9.8. Raíz, ruta profunda y assets PASS con Vite Preview.
Bundle sin dominio del API real. Lint global reportó errores y avisos en
el código importado. Build advierte por tamaño del bundle y datos Browserslist
antiguos.

Pendientes: Compose y Nginx con Docker real, idempotencia y digest del release.
Para una preview externa, confirmar DNS, fuente declarativa del proxy y
control de acceso antes de configurar TLS. Sin despliegue en CT618.
