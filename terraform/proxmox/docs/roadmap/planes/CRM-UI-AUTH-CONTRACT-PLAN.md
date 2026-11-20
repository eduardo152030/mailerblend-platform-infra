# CRM UI — contrato de autenticación y autorización

[PR #48](https://github.com/eduardo152030/mailerblend-platform-infra/pull/48).

[Issue #25](https://github.com/eduardo152030/mailerblend-platform-infra/issues/25).
Fase 7, preparación local en progreso, 20/11/2026 Europe/Madrid.
Rama `docs/crm-auth-contract`, worktree hermano
`mailerblend-platform-infra-crm-auth-contract`, SHA inicial `eeb4a513`.
PR independiente de la rotación de CT618.

## Estado actual

El [inventario funcional](CRM-UI-COMPOSABLE-CONTRACT.md) identifica FormEntries,
Smart management y LinkedIn. App.tsx monta rutas bajo CRMLayout sin comprobar
sesión. LoginPage y el selector gestionan navegación. El dashboard de
FormEntries también consulta Gastos y LinkedIn. CRMAPI registra routers sin
dependencia global de identidad humana y permite CORS de prueba. Intake tiene
su propia dependencia X-Ingest-Secret. El helper X-API-Key existe en el código.
Se requiere inventariar qué clientes y rutas lo usan realmente antes de cambiar
red o contratos. Salud/readiness deben conservar un contrato mínimo separado.

## Contrato común

- UI y API bajo el mismo origen. Callback exacto y protección de estado del
  flujo. Si se usan cookies, Secure, HttpOnly, host-only y SameSite compatible,
  más comprobación de origen/CSRF para mutaciones. Sin claves de servicio en el bundle.
- CRMAPI comprueba identidad y permisos por operación y ámbito de datos.
  Asociar el emisor y sujeto estable a permisos por proyecto mantenidos
  en servidor. Email, ruta y campos enviados por el navegador no conceden acceso.
- project_key puede filtrar el ámbito permitido. Omitirlo o cambiarlo no amplía
  ese ámbito. Aplicar el control a listas, detalles, snapshots y agregados.
  El dashboard solo consulta módulos permitidos. Proyectos todavía no migrados
  permanecen deshabilitados y las rutas directas respetan el mismo control.
- Separar sesiones humanas y credenciales de integraciones. Conservar los
  métodos y rutas de intake y de clientes aprobados. Aplicar la política del
  backend tanto en acceso directo como desde el proxy.
- #26 aprovisionará identidades y permisos aprobados por invitación o
  restablecimiento. Conservar en #28 el cotejo de roles efectivos del catálogo
  anterior. La migración de hashes queda fuera del alcance.

## Decisión pendiente

| Opción | Implicación |
| --- | --- |
| Supabase Auth gestionado, proyecto dedicado para identidad | Mantener negocio en el CRM actual. Requiere cuenta/proyecto y aprobación de tratamiento de datos, región y coste. Confirmar configuración IaC y envío de correo. |
| Supabase Auth autoalojado, despliegue dedicado | Mantener control de infraestructura de identidad. Requiere provisionar Auth, base propia, TLS, correo, claves, actualizaciones, backup y restauración. PostgreSQL actual no presta ese servicio. |

Preparar el contrato común sin aprovisionar un proveedor. La elección requiere
al propietario por su impacto operativo y de datos. Referencias oficiales:
[Auth](https://supabase.com/docs/guides/auth), [configuración autoalojada](https://supabase.com/docs/guides/self-hosting/auth/config)
y [URLs de redirección](https://supabase.com/docs/guides/auth/redirect-urls).

## Aceptación por ejecutar

| Caso | Resultado observable |
| --- | --- |
| Sesión ausente, inválida, vencida o revocada | API 401 y vuelta al acceso sin cargar datos. Revocación o baja bloquean la obtención o renovación dentro del límite acordado. |
| Permiso de lectura | GET permitido en el proyecto. Edición y acciones reservadas responden 403. |
| Usuario de FormEntries abre Gastos o LinkedIn por enlace directo | Denegación en UI y API. El dashboard no lanza esas consultas. |
| Usuario cambia filtro, ID o proyecto | Autorización en servidor. Listas, snapshots y agregados siguen dentro del ámbito. |
| Login, logout y cambio de usuario | Callback válido, sesión nueva y caché de consultas separada. |
| Intake, otros clientes y health | Fixtures confirman los mismos contratos autorizados. Las credenciales de cliente no se confunden con una sesión humana. |
| Proxy, API directo y bundle | Autorización equivalente en operaciones protegidas. Pruebas de origen y CSRF si procede. Bundle sin valores privados. |

Preparación documental completada. No se ejecutaron estas pruebas de sesión.
Pendientes proveedor, responsables de roles e integraciones y publicación
del #24. Siguiente paso: validar adaptador, guardas y permisos con identidades
sintéticas una vez que se elija el proveedor. Sin cambios en producción.
