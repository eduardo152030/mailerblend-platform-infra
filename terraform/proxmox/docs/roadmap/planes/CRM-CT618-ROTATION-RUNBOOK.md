# CT618 — runbook de rotación de la credencial CouchDB

[PR #46](https://github.com/eduardo152030/mailerblend-platform-infra/pull/46).

[Issue #23](https://github.com/eduardo152030/mailerblend-platform-infra/issues/23).
Fase 7. Rotación productiva ejecutada con autorización explícita el
20/11/2026 Europe/Madrid. El alcance fue CouchDB y Budibase D051.
El recambio general queda en [#36](https://github.com/eduardo152030/mailerblend-platform-infra/issues/36).

## Preflight de la ventana

1. Vincular la ventana a la revisión Git integrada y al respaldo de
   [snapshot y restauración](CRM-CT618-SNAPSHOT-RESTORE-PLAN.md).
   Si el estado cambió sustancialmente, obtener una nueva copia consistente
   y verificarla antes de intervenir. Conservar el manifiesto y una copia
   privada separada de los tres archivos de configuración. Comprobar el
   segundo respaldo fuera del host si el runbook de recuperación lo exige.
2. Confirmar 200 con TLS verificado para GET de `/builder/auth/login` y
   `/_svc/health`. Registrar ID, imagen, StartedAt, health y volumen de
   CouchDB y Budibase D051. Registrar también los cinco servicios activos
   y originales detenidos. Validar nombre de proyecto, digest y montajes.
3. En un directorio privado 0700 del CT, preparar copias 0600 con
   `install -m 600` y conservar por separado los originales y su propietario.
   El destino persistido se obtiene de `docker inspect --format` sobre el
   montaje volumen cuyo Destination es `/data` de `budibase-app`.
   Exigir exactamente un montaje, resolver su ruta y verificar que pertenece
   a Docker en CT618. No mostrar la URL ni el Compose renderizado.
4. Ejecutar el generador versionado sobre las copias con
   `--env-file`, `--couch-compose`, `--app-compose`,
   `--app-persisted-env`, `--prepare-candidate` y `--normalize-legacy-env`.
   Confirmar la ausencia de duplicados y la coherencia de los tres candidatos.
   Verificar que el `COUCH_DB_URL` sigue apuntando al CouchDB actual.
   Mantener el usuario CouchDB, la red Docker y los volúmenes existentes.

## Secuencia prevista para una ejecución autorizada

Ejecutar desde una receta versionada con SSH estricto vía PVE, dentro de una
ventana exclusiva y después de verificar el respaldo. Los siguientes comandos
identifican las operaciones que debe ejecutar la receta. Esta ronda solo
prepara y revisa el procedimiento.

```bash
legacy=/opt/infra-composable-crm/budibase
d051=/opt/healthcheck-d051/budibase-app
couch=(docker compose --project-directory "$legacy" -p budibase \
       --env-file "$legacy/.env" -f "$legacy/docker-compose.yml")
app=(docker compose --project-directory "$d051" -p d051-budibase-app \
     --env-file /dev/null -f "$d051/compose.private.json")
"${app[@]}" stop budibase-app
# Instalar atómicamente los tres candidatos desde staging privado.
# Aplicar dueño/grupo verificados y 0600 cuando sean compatibles con el runner.
"${couch[@]}" up -d --no-deps --force-recreate couchdb
# Verificar autenticación nueva, rechazo 401 de la anterior y el mismo volumen.
"${app[@]}" up -d --no-deps --force-recreate budibase-app
```

La instalación atómica usa un temporal 0600 en el mismo directorio del
destino, `install` con propietario/grupo verificado y `mv -T` al nombre
final. Incluye los tres archivos: `$legacy/.env`, `$d051/compose.private.json`
y `/data/.env` en el volumen correcto. Para verificar credenciales, usar
la cuenta en memoria o entrada estándar y registrar solo estatus HTTP.
No pasar contraseñas en argumentos ni imprimir modelos Compose.

Usar GET autenticado de CouchDB `/_all_dbs` con el candidato y con el valor
anterior. El candidato debe dar 200 y el anterior 401. Exigir D051 healthy,
GET del Builder y CRMAPI 200 con TLS, login acordado por el propietario y
mismos IDs de Redis, CRMAPI y PostgreSQL. Revisar que los originales sigan
detenidos. Una segunda aplicación de Compose sin `--force-recreate` ni
cambio de configuración conserva los IDs e inicios del servicio.

## Rollback y tiempo

Ante pérdida de acceso CouchDB, demora fuera del límite, health fallido
o cambio de un servicio ajeno, detener el avance. Con Budibase detenido,
restaurar los tres archivos anteriores de forma atómica, recrear solo
CouchDB y validar su autenticación con el valor original, luego recrear
solo Budibase D051 y repetir health y login. Mantener el mismo volumen de
CouchDB durante el rollback. Si la persistencia resultase dañada, preservar
los volúmenes actuales y revertir en un CT aislado a partir de la copia;
una restauración sobre volúmenes vivos queda fuera de esta receta.

Presupuesto inicial: reservar **30 minutos** de ventana, con una previsión
de **5–10 minutos de indisponibilidad de Budibase** y margen para rollback.
El presupuesto es una estimación basada en etapas de arranque y
verificación. No implica un tiempo medido en producción. Iniciar la
reversión si el candidato no alcanza readiness funcional en cinco minutos
desde la recreación de Budibase o antes si falla una guarda crítica.
Una futura ejecución requiere su propia ventana y autorización.

## Evidencia disponible y orden de fusión

El snapshot actual y la restauración funcional del 20/11/2026 se verificaron
en CT9618. Se conservan el archivo, su checksum y el clon apagado. El
respaldo está en otro disco del mismo PVE. Revalidar alcance, antigüedad y
requisitos de copia separada para la ventana. El arranque aislado incluyó
espera de red y Docker, por lo que no se usa como medida de indisponibilidad
de producción. La estimación de 5–10 minutos y la reserva de 30 minutos
se mantienen como presupuesto inicial con criterio explícito de reversión.

#44 y #45 están integrados en main. Esta entrega parte de ese main y
puede fusionarse directamente. La fusión solo publica los procedimientos
y evidencias. La autorización operativa de esta ronda se registra abajo.

## Ejecución productiva del 20/11/2026

Rama `ops/crm-618-couchdb-rotation`, worktree hermano
`mailerblend-platform-infra-crm-618-couchdb-rotation`, SHA inicial
`eeb4a5134c551906ef889764e70daf1e1113bfcc`. PR #46 integrado antes del
preflight. El propietario dio el OK explícito para ejecutar inmediatamente.
[PR de ejecución #47](https://github.com/eduardo152030/mailerblend-platform-infra/pull/47).

Se usó la [receta versionada](../../../scripts/run-crm-618-couchdb-rotation.sh)
contra el **archivo ya restaurado y verificado** del PR #46. El ejecutor
revalida checksum, edad, modo y estado del clon, y conserva copias privadas
de los tres originales. Se validaron las referencias de imagen antes de
recrear. Un ensayo simulado inyectó un fallo en D051 y comprobó reversión
de los tres archivos. Preflight real y ejecución:

```bash
scripts/run-crm-618-couchdb-rotation.sh storage:backup/vzdump-lxc-618-2026_11_20-08_23_42.tar.zst prepare
scripts/run-crm-618-couchdb-rotation.sh storage:backup/vzdump-lxc-618-2026_11_20-08_23_42.tar.zst execute
```

Resultado a las 09:18 CET:

- CouchDB anterior HTTP 401 y candidato HTTP 200. Usuario, imagen, red,
  puertos y montajes de CouchDB y D051 preservados.
- D051 healthy y salud de sistema PASS. GET de Builder y CRMAPI HTTP 200
  con TLS verificado. Prueba de login humana productiva pendiente.
- Redis, PostgreSQL y CRMAPI conservaron ID e inicio. Worker y originales
  continuaron detenidos. Segunda aplicación con los mismos modelos mantuvo
  ID e inicio en ambos objetivos. No se necesitó rollback.
- Secuencia de parada y verificación: **35 s**. El tiempo exacto de
  indisponibilidad HTTP no se midió por separado. Originales retenidos en
  staging privado y archivo de recuperación conservado. Los tres archivos
  activos se instalaron en modo 0600 con propietarios preservados.

Rotación puntual DONE técnica. #23 sigue abierto para aceptación del
propietario. El recambio general #36 continúa diferido. CT109 y su preview
no cambiaron. No se programó ninguna otra intervención productiva.
