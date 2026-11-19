# CT618 — remediación de la credencial de CouchDB

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
