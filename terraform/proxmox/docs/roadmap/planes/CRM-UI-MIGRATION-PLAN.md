# CT618 — sustitución de la interfaz CRM

Estado **BLOCKED para el corte directo**, 20/11/2026 Europe/Madrid. Fase 7, IaC Reliability, Security & Disaster Recovery. Diagnóstico de lectura completado. Rama `docs/crm-ui-migration`, worktree hermano `mailerblend-platform-infra-crm-ui-migration`, base y SHA inicial `ac9335262082f4a47010299a381615366212a024`. El propietario aprobó sustituir la convivencia por un corte único. Preparación, ejecución y retirada son hitos distintos.

[PR de planificación #21](https://github.com/eduardo152030/mailerblend-platform-infra/pull/21).

## Arquitectura comprobada

- CT618 (192.168.1.118) aloja tres responsabilidades de aplicación: UI/workflows, CRMAPI (FastAPI) y PostgreSQL. La UI activa es una instancia all-in-one recuperada; el worker separado y originales de rollback están detenidos. CouchDB y Redis están activos en la red externa compartida `nucleo_network`, con CRMAPI, PostgreSQL y la UI. El inventario de la red identifica miembros, pero no prueba quién consume cada dependencia.
- Lectura SSH 19/11, 20:49 CET. El alias directo carece de clave de host registrada. Diagnóstico completado por PVE con SSH estricto y `pct exec 618` de solo lectura. `docker compose ls` identifica proyectos D051 independientes para la UI activa y CRMAPI, además del Compose de dependencias, PostgreSQL y los exporters. Puertos publicados en la IP del CT: UI 8080, API 18088 y PostgreSQL 5432. UI y API tenían estado healthy. Preservar D-009, recuperación D051 y originales hasta la retirada autorizada.
- Desde la sesión de auditoría, TLS verificado y HTTP 200 en `/builder/auth/login` y `/_svc/health` del dominio actual; `/_svc/v1/health` devolvió 404. Los códigos prueban alcance HTTP, no acceso de usuario ni paridad. Propiedad y fuente declarativa del proxy/DNS, rutas privadas de acceso directo y consumidores externos requieren inventario. El nombre del dominio se comparte con otros servicios.
- Compose y runtime muestran `supabase-db` como PostgreSQL 16, sin servicio Supabase Auth identificado. Las [lecciones](../../../services/infra-composable-crm/lecciones-aprendidas.md) sitúan datos de negocio en PostgreSQL y cuentas, pantallas y configuración de UI en CouchDB; Redis gestiona sesión/caché. Auditar también formularios publicados, automatizaciones, adjuntos, permisos y escrituras externas antes de retirar metadatos. La credencial expuesta se retiró y rotó bajo #23, cerrado con login humano confirmado por el propietario.
- El código Lovable de [PR #19](https://github.com/eduardo152030/mailerblend-platform-infra/pull/19) está integrado. El código actual está en `compose/crm-ui/crm-core-main`. React/Vite presenta tres proyectos en un shell compartido, cada uno con flujos que se conectarán a CRMAPI por PR. `LoginPage.tsx` selecciona y navega, `App.tsx` carece de un control de sesión, y `lib/api.ts` usa una ruta relativa del mismo origen y carece de sesión. El código de CRMAPI declara CORS comodín y un control propio para ingestión. Revisar protección efectiva de cada ruta y de los accesos alternativos. Comparar OpenAPI desplegado con `src/lib/api.ts`, incluyendo conversiones offline y dashboard LinkedIn. La UI incluye un archivo de mocks LinkedIn también importado para tipos y constantes, por lo que hay que verificar sus usos y datos efectivos. No hay aceptación funcional acreditada por la importación.
- [Inventario de referencias](CRM-UI-MIGRATION-REFERENCES.md) al SHA inicial. Las referencias de otros servicios se investigan por propiedad; Redis compartido o ajeno queda fuera. Llevar a decisión el tratamiento de evidencia histórica versionada y respaldos retenidos antes de comprometer «cero referencias». El alcance operativo propuesto es retirar todas las referencias CRM activas del árbol final, incluidos nombres, scripts, rutas, configuración, piezas generadas y pruebas. El historial Git y las copias privadas de recuperación tienen una política de retención propia.

## Corte directo aprobado

Ronda 20/11/2026 Europe/Madrid. Rama `docs/crm-direct-cutover`, worktree
hermano `mailerblend-platform-infra-crm-direct-cutover`, SHA inicial
`7082472bcafdd8d95033ae4b956d62adfbb8eb0e`.

- Una sola sustitución de UI en `https://infra-svc01.mailerblend.com/`.
  Mismo certificado Nginx de CT109. Respaldar y verificar el vhost.
  Cambiar la raíz y el enrutamiento de /builder y /app hacia CRM UI, salvo
  excepciones concretas de Budibase que se demuestren necesarias. Conservar
  los upstreams y contratos de /_svc/ e ingestión conforme al alcance de #24.
- Basic Auth temporal para la UI hasta activar Supabase Auth. CRMAPI y UI
  bajo el mismo origen y sin secretos en Vite. Datos reales solo con control
  de acceso verificado tanto por proxy como por la ruta directa del API.
- Los contenedores Budibase, CouchDB y Redis se mantienen con sus volúmenes.
  La vuelta atrás es restaurar y recargar el vhost, con verificación de TLS,
  Budibase y CRMAPI. Tras un corte exitoso ensayar una reversión y reaplicar
  la versión verificada. Ante fallo revertir y corregir, máximo tres intentos.
  Retirada o borrado requieren permiso separado en #31.
- GoTrue autoalojado aprobado para #25, PostgreSQL 16 en CT618, esquema
  auth exclusivo y migraciones aisladas. [Contrato de acceso](CRM-UI-AUTH-CONTRACT-PLAN.md).
- Después de autenticación y hardening, conectar pantallas a CRMAPI y eliminar
  mocks en orden FormEntries → Smart management → LinkedIn. Cada cambio llega
  por PR verificado con pruebas de regresión. El orden no implica tres cortes
  de vhost ni UAT por fases.

## Catálogo publicado de Budibase

Lectura autenticada de CouchDB en CT618, filtrada a metadatos de publicación,
sin registros, URLs con credenciales ni cuerpos privados. Se encontró una
base de workspace publicada con una aplicación habilitada
`NT_Crm_FormEntries` (`/ntcrmformentries`). Sus diez pantallas tienen rol
`BASIC`. Nueve contienen componentes de formulario.

| Rutas internas de pantalla | Componentes de formulario |
| --- | --- |
| /facturas, /formulario_web, /contactos | Sí |
| /parametros_utm, /historial, /pendientes | Sí |
| /oportunidades, /presupuestos, /conversiones_offline | Sí |
| / | Sin componente de formulario observado |

Automatización publicada: `Email_send_new_entry`, disparador `ROW_SAVED`,
sin marca disabled. No se encontró una referencia literal al dominio en
los doce documentos de aplicación, pantallas y automatización revisados.
No se identificó un webhook público en ese catálogo. Esto no demuestra
que no haya consumidores externos ni confirma qué pantallas reciben
tráfico. Antes de aplicar el vhost, confirmar el uso de formularios y
el origen de las escrituras que disparan el correo. Añadir solo las
excepciones concretas cuya dependencia pública quede comprobada.

## Bloqueo de seguridad del corte

Lectura del vhost CT109: Nginx tiene una ubicación independiente
`/_svc/` sin Basic Auth. Un GET HTTPS de `/_svc/v1/contacts?limit=1`
sin credenciales obtuvo 200. El cuerpo se descartó y TLS se verificó.
La API de contactos en el código fuente obtiene la conexión a datos
sin una dependencia de identidad en esa operación. Un 401 de la nueva
raíz no protegería las rutas de negocio del API.

Se aplica la parada del propietario por datos accesibles sin autenticación.
No hubo backup de vhost, reload, despliegue, golden test de escritura ni
alteración de CT109/CT618. Próximo paso requerido: acordar si se adelanta
la protección de datos de #49 o la de #25 al corte, preservando health,
intake y los consumidores de servicio autorizados. Validar 401/403 anónimo
en laboratorio y acceso autorizado antes de permitir datos reales.

## Contrato de Cline para cada PR de interfaz

Leer [AGENTS](../../../services/infra-composable-crm/compose/crm-ui/crm-core-main/AGENTS.md), [Style Fixer](../../../services/infra-composable-crm/compose/crm-ui/crm-core-main/docs/style-fixer.md), [Code Reviewer](../../../services/infra-composable-crm/compose/crm-ui/crm-core-main/docs/ui-crm-core-agent-code-reviewer.md) y los prompts [estilo](../../../services/infra-composable-crm/compose/crm-ui/crm-core-main/docs/prompts/style-fixer-prompt.md) y [revisión](../../../services/infra-composable-crm/compose/crm-ui/crm-core-main/docs/prompts/code-reviewer-prompt.md). Actualizar enlaces en el traslado. Usar los prompts como guía de revisión basada en el código real. La alerta de 250 líneas abre revisión de cohesión. Mantener tokens semánticos, temas claro/oscuro, móvil, teclado y foco, manejo de carga/error/vacío, transporte vía hooks, claves e invalidaciones React Query por dominio. Mantener `/` fuera del shell, rutas de proyecto protegidas dentro de `CRMLayout`, menú y selector coherentes. Cada PR adjunta evidencia por criterio, comprobación del diff y revisión independiente antes de abrir el siguiente issue.

## Issues vigentes

| Issue | Entrega y estado |
| --- | --- |
| [#22](https://github.com/eduardo152030/mailerblend-platform-infra/issues/22) | Inventario técnico integrado. Confirmar dependencias externas para el corte. |
| [#23](https://github.com/eduardo152030/mailerblend-platform-infra/issues/23) | Cerrado. Rotación y login humano aceptados. |
| [#24](https://github.com/eduardo152030/mailerblend-platform-infra/issues/24) | Corte único. BLOCKED por acceso directo anónimo a datos. |
| [#25](https://github.com/eduardo152030/mailerblend-platform-infra/issues/25) | GoTrue autoalojado, sesión y permisos. Diseño aprobado, ejecución pendiente. |
| [#26](https://github.com/eduardo152030/mailerblend-platform-infra/issues/26) | Aprovisionar identidades y roles aprobados. Depende de #25. |
| [#27](https://github.com/eduardo152030/mailerblend-platform-infra/issues/27) · 06 | Backup, validación y rollback del vhost único. Ensayo posterior a un corte exitoso. |
| [#28](https://github.com/eduardo152030/mailerblend-platform-infra/issues/28) · 07 | Conectar FormEntries con API real y quitar mocks. Incluye formularios, edición y conversiones. |
| [#29](https://github.com/eduardo152030/mailerblend-platform-infra/issues/29) · 08 | Conectar Smart management con API real y quitar mocks. |
| [#30](https://github.com/eduardo152030/mailerblend-platform-infra/issues/30) · 09 | Conectar LinkedIn con API real y quitar mocks. |
| [#31](https://github.com/eduardo152030/mailerblend-platform-infra/issues/31) · 10 | Retirar legado y dependencias exclusivas. Autorización separada obligatoria. |
| [#49](https://github.com/eduardo152030/mailerblend-platform-infra/issues/49) | Hardening CRMAPI y proxy, incluidos gate de datos, CORS, SQL/Pydantic, adjuntos, límites, cabeceras y gitleaks. |
| [#36](https://github.com/eduardo152030/mailerblend-platform-infra/issues/36) | Recambio general diferido hasta terminar las pruebas. |
