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

## Preflight de solo lectura

[PR #37](https://github.com/eduardo152030/mailerblend-platform-infra/pull/37).

Rama `ops/crm-couchdb-rotation-preflight`, worktree hermano
`mailerblend-platform-infra-crm-rotation-preflight`, inicio `db4ff8a3`.
[Script de preflight](../../../scripts/check-crm-couchdb-rotation.py).
Recibe rutas del entorno legado, Compose CouchDB y Compose privado D051.
Renderiza ambos con Docker Compose y compara solo las claves esperadas,
sin imprimir los modelos. Bloquea secretos con permisos distintos de 0600,
claves duplicadas, overrides del entorno y credenciales no coincidentes.
La réplica debe usar el mismo formato D051. El preflight evalúa archivos,
mientras que la autenticación del motor y el login requieren el ensayo aislado.

Cinco casos sintéticos PASS con Compose simulado: coincidencia, discrepancia,
error de render con salida sensible, permisos y duplicados. Pendientes Docker
real, backup restaurado, helper de mutación/rollback y una ventana operativa.
Sin ejecución en CT618. El recambio general sigue diferido en [#36](https://github.com/eduardo152030/mailerblend-platform-infra/issues/36).

Ronda 02 del PR #37, inicio `e2f2f404`. El modo opcional
`--prepare-candidate DIRECTORIO_PRIVADO` genera dos candidatos con un valor
nuevo y valida ambos modelos Compose. Requiere directorio propio 0700.
Los candidatos quedan en un subdirectorio privado con archivos 0600, conserva
los archivos fuente, y no inicia ni recrea servicios. Usar una ubicación privada
fuera del repositorio. Prueba con Compose simulado PASS, incluyendo permisos
del destino, coincidencia del valor nuevo y ausencia de valores en salida.
No aplicar estos archivos antes del ensayo real de autenticación y rollback.

Ronda 03, inicio `a5fd8add`. Digest de CouchDB confirmado por lectura de
`RepoDigests` en CT618. [Ensayo de motor aislado](../../../scripts/rehearse-crm-couchdb-rotation.sh):
crea un volumen sintético y contenedores temporales, conserva una base de
prueba durante cambio y reversión, y exige HTTP 401 con la credencial retirada.
Se validó sintaxis Bash. No se ejecutó el ensayo: la integración GitHub devolvió
403 al publicar un workflow, y no hay Docker local. Aún falta el ensayo con
Budibase D051 y la prueba de rollback del consumidor. Sin cambios en CT618.

Entrega del ensayo en [PR #38](https://github.com/eduardo152030/mailerblend-platform-infra/pull/38),
rama `ops/crm-couchdb-rehearsal`, worktree hermano
`mailerblend-platform-infra-crm-rehearsal`, base de ronda `18743981`.
El avance se trasladó al PR #38 después de integrarse el PR #37.

Ronda 02 del PR #38, 19/11/2026 Europe/Madrid, SHA inicial `b8e66c96`.
Prueba local con binarios Docker 27.5.1 en un directorio temporal y un espacio
de nombres de usuario, montaje y PID. El daemon arrancó con socket y estado
privados, VFS y bridge y reglas de red del daemon deshabilitados. Docker Hub
entregó capas de la imagen fijada, pero el registro de la primera capa falló:
el mapeo de un solo UID/GID no permite aplicar el GID 42 de un archivo de la
imagen. El daemon temporal terminó. No se creó el volumen de prueba, no
arrancó CouchDB y no se ensayó la rotación. El entorno carece de los helpers
`newuidmap` y `newgidmap` para usar los rangos subordinados configurados.
Próxima ejecución: un motor Docker aislado con mapeo suficiente para instalar
las capas de las imágenes. Ningún cambio en CT618.

## Ensayo del motor con la imagen verificada

Ronda 03 del PR #38, 19/11/2026 22:02 CET. SHA inicial `580280ac`.
Se verificaron por SHA256 el manifiesto, el manifiesto amd64 cuando corresponde
y las capas del digest observado. Se extrajeron a un directorio temporal y se
ejecutó el binario CouchDB **3.5.1** dentro del rootfs en espacios de nombres
de usuario, montaje, PID y red. Solo loopback; credenciales y base sintéticas.
Se sobrescribió exclusivamente el INI de prueba, con reinicio del motor en
cada paso y el mismo directorio de datos.

| Evidencia | Resultado |
| --- | --- |
| Arranque y creación de base sintética con el valor inicial | PASS |
| Arranque con valor candidato, valor anterior rechazado y base accesible | HTTP 401 / 200 |
| Reversión al valor inicial, candidato rechazado y base accesible | HTTP 401 / 200 |

El entrypoint de la imagen crea el administrador desde el entorno solo si
no lo encuentra en los INI existentes. Confirmar en el ensayo Docker la
persistencia efectiva de esos INI al recrear el contenedor; un reinicio del
mismo contenedor no acredita por sí solo la rotación. El ensayo anterior
prueba el comportamiento del motor con configuración explícita y datos
persistidos. No ejercitó la recreación Docker, la configuración D051 ni el
login de Budibase. Esos pasos siguen siendo condiciones de la rotación.
Sin cambios en CT618.

## Comportamiento del entrypoint

Ronda 04 del PR #38, 19/11/2026 Europe/Madrid. Inicio `4cf01874`.
Se ejecutó el entrypoint original de la imagen verificada en un rootfs de
prueba y una red aislada. Para esta prueba local se adaptó el usuario del
rootfs temporal y se sustituyó únicamente el cambio de UID/GID de setpriv,
que el kernel bloqueaba en el namespace. El entrypoint y el binario CouchDB
no se editaron. Se reutilizó el mismo directorio de datos sintético.

- Reinicio con INI existente y un valor nuevo en el entorno: el valor
  anterior siguió funcionando (200) y el candidato fue rechazado (401).
- Arranque con INI nuevo y el candidato en el entorno: valor anterior
  rechazado (401), candidato válido y base conservada (200).
- Reversión con INI nuevo y valor inicial: candidato rechazado (401) y base
  accesible con el valor inicial (200).

El procedimiento debe distinguir la persistencia del INI del volumen de datos.
En la prueba Docker verificar los montajes y conservar toda personalización
vigente antes de preparar la recreación. Exigir prueba funcional de Budibase
D051 tras propagación y rollback. El ensayo de entrypoint no sustituye esa
prueba conjunta. Sin cambios en CT618.

## Ensayo Docker en VM desechable

19/11/2026 Europe/Madrid. Rama `test/crm-budibase-rotation`, worktree
hermano `mailerblend-platform-infra-crm-budibase-rotation`, base
`78ecfeec58050aacb2a6c84d9a41e898c51c06fe`, con #41 integrado.
[PR de ensayo #42](https://github.com/eduardo152030/mailerblend-platform-infra/pull/42).

En la misma VM QEMU/Alpine del ensayo de preview se ejecutó
`scripts/rehearse-crm-couchdb-rotation.sh` con Docker 28.3.3 y CouchDB
fijado al digest observado. Un intento inicial falló al publicar el puerto
porque loopback todavía no estaba levantado en el invitado. Tras habilitarlo,
el script terminó con el marcador `CRM_COUCHDB_DOCKER_PASS`. Recreación y
reversión sobre el mismo volumen de datos sintéticos: ambas credenciales
sustituidas obtuvieron HTTP 401 y la base de prueba siguió accesible.

Lectura filtrada de CT618 confirmó que `COUCH_DB_URL` utiliza HTTP en
5984 y sin usuario embebido. La réplica se prepara con ese modelo,
credenciales sintéticas y dos proyectos Compose en red privada. La
recreación conjunta y el login D051 siguen pendientes hasta que termine
el ensayo. No se usaron volúmenes ni credenciales de CT618.
