# Fase 4 — SKIP AND CONTINUE con baseline (D-035)

D038 actualiza aceptación: [STANDARD/CRITICAL](VALIDATION-PROFILES.md).
Una aplicación unhealthy previa permiteDONE de monitorización si baseline,
no regresión,alertas yrestogates están verificados. Los bloqueados617/615/614
no se reabren. No exigirwatch900s niTelegram/rollback real porcadaCT enSTANDARD.
Procedimientos/evidencias siguientes son históricos donde difieran.

## D-035 cerrado — 2026-11-06 12:24 CET

**Fase4 IN PROGRESS:8 DONE,4 BLOCKED,5 PENDING. HALT GLOBAL;61211 revertido.**
PolíticaA/B/C/D implementada:614 esBLOCKED / PRE-EXISTING ISSUE,503 previo,
originales/config intactos e independencia crítica verificada de61211 (DBlocal).
Se ejecutó solo61211: preflight/backups/promtool/fuentesLXC-Docker, rollback e
idempotenciaPASS; inicial13/360.225s yTelegramAPI+2/0errores.
Watcher31/903.637sFAIL desde60,025s: lectorRAMcomún terminó por
parseoRFC3339Nano con5decimales; no se demuestra error contable del exporter.
Rollback final verificado: originales/apps/config61211, checkpointProm8/24archivos,
backups externo/PVE, loggersdetenidos, ocho aceptados/Prom/AM intactos,17/17/11UP,
OOMdelta0. NoDONE ni9/17. Correcciónparser yregresión0–9decimales solo local,
NO desplegada ni reintentada.52 pruebas pertinentesPASS; sin commits/push.
PolíticaBLOCKED, permisosvacíos, HALTs/backups/candidatos conservados; noR6/R7.
Tiempo:36.8min. [Cierre61211](CT61211-D035-EXECUTION.md),
[política](SKIP-AND-CONTINUE.md), [cola](../../services/common/phase4-recovery-queue.yml).
Próximo objetivo: revalidar correccióncomún y reentrada exclusiva61211 tras revisar
HALT;614 no debe repararse para continuar un CT independiente. No617/615 ahora.


D-035 sustituye el veto D-034 sobre aplicaciones yaunhealthy. Solo61211 autorizado;
614 queda pospuesto sin intervención. No reparar aplicaciones en el rollout.

|Caso|Condición|Resultado|
|---|---|---|
|A|Aplicación saludable antes y después; todos los gates de monitorización y watcher completos|DONE|
|B|Problema anterior a cualquier mutación, original intacto, legacy/alertas conservados y dependencias críticas verificadas|BLOCKED / PRE-EXISTING ISSUE; continuar hacia CT independiente|
|C|Regresión local; rollback completo, saludoriginal restaurada y contención demostrada|BLOCKED / ROLLED BACK; continuar solo con evidencia positiva|
|D|Backups/datos/rollback fallidos, fallo compartido, impacto en otros servicios, estado incierto o dependencias no verificadas|HALT GLOBAL|

Un casoB no exige reparar ni declarar saludable una aplicación heredada. Sí exige
preexisting_before_mutation, no_active_changes, isolated, originals_verified,
prior_coverage_unchanged, legacy_and_alerts_preserved, global_monitoring_healthy,
data_safe y critical_dependencies_verified. Todos deben serTrue. Un fallo debackups
o dependencia desconocida jamás se convierte enB por tener un503 anterior.
A exige saludantes/después; C exige baseline_health_restored yregression_contained,
además de recuperación/config/cobertura/backups/aplicación verificados. Un error del
validador no demuestra defecto del exporter: causa incierta sigueD.

Política y código reutilizables:
[contrato](../../services/common/phase4-skip-policy.yml),
[motor](../../scripts/phase4-skip-policy.py),
[driver](../../scripts/run-skip-exporter-wave.py),
[prueba614/61211](../../scripts/verify-614-61211-isolation.py).
Un intento porCT, directorios/checkpoints nuevos; HALTs históricos no se borran.
180s/7 convencional+watch900s/31, anomalía>=600s sin reset debaseline;
CPU/RAM por identidad/StartedAt/timestamps/cgroup, márgenes y frescura intactos.
Pins, backups externos/PVE, promtool, fuente real, integración incremental,
rollback e idempotencia reales, Prom/AM/Telegram y aceptaciónfinal se mantienen.
El registro se promueve solo tras watcherPASS, sin repetir los ocho aceptados.

CT614 casoB:503 documentado antes de cualquier despliegue; cuatro fingerprints
Docker(id/image/StartedAt/restarts/config_hash) iguales aD034, sin staging/apply.
61211 NocoDB usaNC_DB hostdb, PostgreSQLlocalready/healthy, misma redDockercon
aliasdb yhealth200; no endpoint614/sgtm en dependencias configuradas. No equivale
aUAT de todas las funciones ni demuestra independencia de todo servicio opcional.
[Prueba de lectura](evidence/2026-11-06-d035-isolation-apply.json).
Guardas globales verifican17/17/11 y ocho cadenas y conservarán targetslegacy614.
No se cambian aplicaciones/recursos614, alertas, ocho aceptados niR6/R7.

Ejecutar únicamente con políticaD035 autorizada y prueba de prerrequisitos fresca
(<=300s); al cerrar se vacían permisos y se detiene. La cola de recuperación
[617/615/614](../../services/common/phase4-recovery-queue.yml) no concede permisos.

```bash
python3 scripts/verify-614-61211-isolation.py --output /tmp/phase4-prerequisite-new.json
python3 scripts/run-skip-exporter-wave.py --run integration-<UTC-nuevo> \
  --prerequisite-evidence /tmp/phase4-prerequisite-new.json \
  --output docs/roadmap/evidence/<fecha>-wave.json --execute
```

El comando de ejecución no autoriza reintentos ni otros CT; consultar CURRENT-STATUS
antes de usarlo. La prueba de prerequisitos es de lectura; no es un backup.

## Historial D-034 (contrato sustituido por D-035)

# Fase 4 — política SKIP AND CONTINUE

2026-11-06 11:35 CET. D-034 autoriza614→61211, aplaza617/615. Solo configuraciónProm610
mínima para esos dosCT, no sus exporters niCRM618/EVA622/Grafana611/Blackbox616.
Sin commits/push. Esta política sustituye la barrera histórica que exigía617/615
antes de614 y R4 completo antes de61211, **sin dispensar condiciones de seguridad**.

## Contrato reutilizable

[Política](../../services/common/phase4-skip-policy.yml),
[motor de decisiones](../../scripts/phase4-skip-policy.py),
[driver](../../scripts/run-skip-exporter-wave.py).
Un intento porCT; cada intento en runprivado separado, con suHALT permanente;
HALT-GLOBAL del lote nunca se elimina para continuar. No--all histórico.

|Resultado|Prueba exigida|Avance|
|---|---|---|
|DONE|Todos los gates y watcher final completos|Siguiente CT autorizado|
|BLOCKED / ROLLED BACK|Fallo local probado, originales/app funcionando, recuperación/cobertura/backups seguros|Siguiente autorizado; CT a cola|
|HALT GLOBAL|Fallo común o falta de cualquier prueba de seguridad|Detener lote|

Para saltar, todos deben serTrue: isolated, originals_verified, application_working,
prior_coverage_unchanged, global_monitoring_healthy, recovery_complete, data_safe,
backups_recoverable. Una excepción de validador no demuestra fallo del exporter;
se trata como global/incierta hasta diagnóstico. Si no hubo mutación, no se inventa
un rollback ni un backup: se verifica original inalterado y capacidad no afectada.
**Preflight de aplicación fallido no permite skip si la aplicación sigue fallando.**
Ese requisito procede de la instrucción explícita del propietario, no de un nuevo
umbral. Aislamiento por sí solo no basta. Backups, IaC común, SSH/identidad,
Promglobal, pérdida de cobertura, AM/Telegram, estado incierto, rollback o datos
ponenHALT GLOBAL. No se suben tolerancias ni se repiten intentos fallidos.

## Camino de ejecución y aceptación

Guardas globales antes y después: ocho/nueve fuentes ya aceptadas porAPI,17/17/11UP,
reglas sanas yProm/AMready, contadoresTelegram sin errores nuevos; hashes de24
archivos permiten verificar recuperación byteexacta. Snapshot de lectura **no es**
backup de recuperación; antes de mutar se conserva el backup coordinado verificado.

PorCT: preflight funcional/capacidad/identidad → backups externos/PVE/imágenes y
checkpointProm actual → promtool/config/reglas/discovery → loggersCPU/RAM → digest
exacto/apply/sourceLXC-Docker → integración → rollback real y reapply idempotente →
observación180s/7 (anomalía>=600s sin reset) y cadenaTelegram → watcher900s/31 →
archivo final verificado y promociónDONE. El registro no se promueve antes delwatch.
Fallos posteriores recuperan checkpoint antes de originales y retiran promoción
solo delCT, sin sobrescribir otros aceptados. Clasificación desconocida detiene.

614/61211 usan RAM temporal de la librería revisada: mismo ID/nombre/StartedAt,
timestamp explícito y doble extremo subsegundo sin interpolación; CPU mantiene
sus ventanas. Márgenes20%/512KiB apps,30%/4MiB exporters y25%/8MiB Docker/cgroup
intactos; frescura/gap/PIDs verificables. Proyecto y nombresheld por revisión;
180s/7 convencionales. Los ocho aceptados no se reaplican.
El driver nuevo tiene regresiones locales y ejecución real del camino de preflight
fallido; su camino de despliegue exitoso no se ha probado en esta sesión.

## Ejecución D-034: HALT GLOBAL

Wave `integration-20261106T102530Z`, intento614 `integration-20261106T102530614Z`.
Dos lecturas independientes de salud confirman503 en8091/8092 yDockerunhealthy
para infra-nucleoedge-sgtm-1 ysgtm_preview-1. Puertos18091/18092 no escuchan.
Rutas raíz400/404 no acreditan funcionalidad de ingestión. No se cambian probes
ni puertos para evitar el fallo. El backend del driver repite el contrato original
tras verificar identidad/config y vuelve a fallar.

Guardas devuelven isolated=True, originals_verified=True,
prior_coverage_unchanged=True, global_monitoring_healthy=True,
recovery_complete=True sin cambios activos, pero **application_working=False**.
El motor produceHALT GLOBAL y nunca invoca61211. No es prueba de caída global de
Prometheus: el veto es la condición de salto incumplida.

Estado original614 verificado; sin staging remoto, backup nuevo, apply, reinicio,
recargaProm, cambios de aplicación/recursos/volúmenes ni testTelegram. Ocho aceptados
yProm/AM mantienen identidades/StartedAt/restarts;17/17/11UP, ocho cadenas sanas,
24 archivosProm sin cambios,OOMdelta614=0. Candidatos/observación180s/watch900s,
idempotencia y rollback real **no ejecutados**. No hay aceptación614 ni10/17.
Producción queda **8DONE,3BLOCKED,6PENDING**;61211PENDING sin intervención.
La política cierraBLOCKED con permisosapply/recovery vacíos, sinavance pendiente.
Tiempo:10.8min.36 pruebas pertinentes PASS(9política+14RAM+7rollout+6reentrada).

## Cola de recuperación y siguiente grupo

[Cola versionada](../../services/common/phase4-recovery-queue.yml):617(colisiónheld,
revertido),615(salud503 sin cambios),614(salud503 sin cambios). No se investigaron
617/615 en esta sesión. No se autoriza reparar aplicaciones por migrar exporters.

Siguiente objetivo normal recomendado: **CT61211**, una vez satisfecho el veto de
salud614 o revisada explícitamente esa condición por el propietario. No puede
continuar ahora bajo las condiciones vigentes. La recomendación no activa política
ni solicita dispensa implícita; no comenzarCRM/EVA ni observabilidad. Las fuentes
problemáticas se reservan para recuperación individual al final deF4.

## Reproducibilidad y reanudación

Lectura/local:

```bash
cat docs/roadmap/CURRENT-STATUS.md
cat services/common/phase4-skip-policy.yml
cat services/common/phase4-recovery-queue.yml
python3 -m unittest discover -s tests/monitoring -p 'test_skip_policy.py'
git diff --check
```

Driver de ejecución (solo tras resolver veto, comprobar alcance vigente y habilitar
política porIaC; no ejecutar ahora ni reutilizar elrun cerrado):

```bash
python3 scripts/run-skip-exporter-wave.py --run integration-<UTC-nuevo> \
  --output docs/roadmap/evidence/<fecha>-wave.json --execute
```

La versiónD034 restringe explícitamente la pareja614/61211; cambiar siguiente orden
exige ajustar alcance/versionarlo, no volver a ejecutar614 a ciegas. Constructor
rechaza directorios/evidencias existentes. Guardas SSH estrictas conocidas;
no secretos ni configSSH alterados. Backups/estadosprivados/HALTs previos conservados.

## Evidencias

- [Salud original614](evidence/2026-11-06-d034-614-readonly-preflight.json).
- [Decisión real y pruebas positivas/negativas](evidence/2026-11-06-d034-wave.json).
- [Auditoría final](evidence/2026-11-06-d034-final-audit.json).
- [Tiempo](evidence/2026-11-06-d034-time.json).

Pruebas privadas guardadas en `$HOME/.local/share/mailerblend-recovery/phase4/`,
wave-prefix y run del intento. Los snapshotsglobales contienen configuraciónprivada:
no publicarlos. El logprivado contiene muestras antes/después sin exponerentornos.


## Resultado operativo D035

CaseB614 permitió iniciar61211 sinreparar aplicaciones.61211 pasó controles
iniciales, pero lectorRAMcomún falló alparsear fracciónRFC3339Nano variable:
CaseD/HALT GLOBAL yrollbackverificado. No errorcontable demostrado enexporters.
CaseC dispone de gate de saludtraswatcher antesdepromover; no declararDONE
cuando falta saludfinal. Correcciónparser probada solo local, no reintento.
[Informe completo](CT61211-D035-EXECUTION.md).
