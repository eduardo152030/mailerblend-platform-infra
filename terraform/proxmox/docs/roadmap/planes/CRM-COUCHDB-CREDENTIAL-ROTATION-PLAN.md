# CT618 — remediación de la credencial de CouchDB

[PR #35](https://github.com/eduardo152030/mailerblend-platform-infra/pull/35).

[Issue #23](https://github.com/eduardo152030/mailerblend-platform-infra/issues/23). Fase 7, IN PROGRESS. 19/11/2026 Europe/Madrid. Rama `docs/crm-ui-issue-23`, worktree hermano `mailerblend-platform-infra-crm-23`, SHA inicial `2175f1b403cf99376175b38fe4e483d53fd98684`. El propietario aceptó el avance del inventario #22 y el cotejo del catálogo como condición de #28. El PR #34 sigue sujeto a revisión del propietario. Este PR parte de main y no depende de sus cambios de archivos.

## Alcance y resultado local

Retirada del valor expuesto de las fuentes activas. Búsqueda exacta en archivos rastreados, pasando el patrón por entrada estándar sin imprimirlo: un archivo antes y cero después. Las lecciones conservan la ubicación lógica de la configuración. La credencial histórica sigue siendo material expuesto. Se requiere rotación y se preserva el historial.

El [Compose legado](../../../services/infra-composable-crm/compose/budibase/docker-compose.yml) exige referencias de credencial para CouchDB y la app. La observación #22 identificó la app efectiva en el proyecto separado D051. Confirmar qué referencias consume ese proyecto y cuáles incluyen originales de rollback. El Compose heredado por sí solo no acredita la configuración activa.

## Procedimiento por preparar y ensayar en aislamiento

1. Identificar imagen/digest, servicios, archivos efectivos y montajes. Registrar únicamente nombres de entradas, propietarios y permisos. Confirmar con el responsable el alcance de la cuenta expuesta y los clientes. Resolver asignaciones duplicadas comprobando precedencia en una copia privada.
2. Verificar respaldo externo y restauración de los volúmenes y configuración con el [runbook](../../../services/infra-composable-crm/recovery/RECOVERY.md). Preparar entradas privadas nuevas y copia de rollback. Mantener identificadores, permisos y versiones de los componentes.
3. Construir el helper versionado con preflight, dry-run, bloqueo de concurrencia y una transacción acotada a la cuenta y consumidores efectivos. Ensayar el mecanismo real de CouchDB en una copia aislada con la versión efectiva: comprobar si la credencial se origina en configuración de administradores persistente, en parámetros de arranque o en ambos. Validar la sincronización de CouchDB y clientes. Evitar suposiciones basadas solo en cambiar el archivo .env. No propagar valores al log ni al diff.
4. Aceptación del ensayo: conexión con valor nuevo válida, valor anterior rechazado, login y función de la app correctos, CRMAPI/PostgreSQL con salud conservada. Simular error a mitad de operación, comprobar vuelta coordinada de CouchDB y consumidor, y verificar segunda aplicación sin reinicios o cambios extra. Si falla, detener el paso dependiente.
5. Tras autorización separada y ventana aprobada, ejecutar la receta ensayada en CT618, observar servicios y conservar evidencias filtradas. Si es imprescindible revertir temporalmente a la credencial expuesta, registrar ese estado y coordinar nueva rotación. Mantener worker/originales detenidos. No restaurar una copia sobre los volúmenes vivos.

Pendiente: helper ejecutable y ensayo de integración. El entorno local de esta revisión carece de cliente Docker. No se ejecutó una rotación ni se comprobó si el valor histórico sigue siendo el efectivo.

## Consumidores observados en CT618

Ronda 02 del 19/11/2026, 21:44 CET. Inicio `de88da2e`. SSH estricto vía PVE y
lectura de etiquetas Compose, nombres de entradas, destinos de montaje y modos
de archivo. Se excluyeron valores de credenciales.

| Contenedor | Estado y fuente Compose | Evidencia y tratamiento |
| --- | --- | --- |
| budibase-couchdb | Activo, proyecto `budibase`, `/opt/infra-composable-crm/budibase/docker-compose.yml` | `COUCHDB_USER` y `COUCHDB_PASSWORD`; volumen en `/opt/couchdb/data`. Confirmar mecanismo efectivo de rotación en la réplica. |
| budibase-app | Activo, proyecto `d051-budibase-app`, `/opt/healthcheck-d051/budibase-app/compose.private.json` | Incluye `COUCH_DB_URL`, `COUCHDB_USER` y `COUCHDB_PASSWORD`; volumen `/data`. Fuente privada modo 0600, propietario root. Actualizarla coordinadamente en la receta. |
| budibase-worker, budibase-app-d051-original, budibase-app-pre-recovery | Detenidos; proyectos histórico y de recuperación | Los tres conservan referencias CouchDB y montaje `/data`. Preservar y mantener detenidos. El ensayo de rollback debe comprobar compatibilidad con el secreto nuevo antes de considerar su activación. |
| crm-api | Activo, proyecto `d051-crm-api` | No presenta esas tres entradas. Conservar su configuración y usar health/readiness como controles de regresión. |

El `.env` heredado tiene modo **0644**. Incorporar comprobación de propietario
efectivo en el CT y protección a 0600 en el procedimiento, después de comprobar
quién necesita leerlo. El propietario del archivo apareció sin resolución de
nombre en esta lectura. La presencia de variables no prueba igualdad de valores
ni excluye clientes externos. No se ha modificado el modo del archivo.

Siguiente paso del ensayo: usar infraestructura Docker aislada, las imágenes
efectivas y datos sintéticos. Replicar ambos proyectos Compose y sus volúmenes
separados. Medir cambio de credencial en CouchDB, propagación a la app D051 y
rollback. El insumo pendiente es un runtime Docker aislado con acceso a las
imágenes y red interna de prueba. No usar CT618 como banco de ensayo.

Ronda de resolución de conflictos. SHA inicial `fac40053`, base
`main` actualizada a `05c99dee`. Roadmap, estado y fase conservan los
registros del #22 integrado y el seguimiento del #23.
