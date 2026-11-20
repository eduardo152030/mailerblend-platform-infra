# CT618 — runbook de rotación de la credencial CouchDB

[Issue #23](https://github.com/eduardo152030/mailerblend-platform-infra/issues/23).
Fase 7. Preparado para revisión. Ejecución productiva **pendiente de aprobación
y fecha/hora concretas**. Aplicar únicamente a CouchDB y Budibase D051.
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
La ventana y el permiso efectivo siguen por fijar.

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
y evidencias. La intervención en CT618 queda pendiente de autorización.
