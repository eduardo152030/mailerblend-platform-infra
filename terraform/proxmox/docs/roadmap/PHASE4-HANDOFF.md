# Fase 4 — Exporters & Monitoring Coverage: handoff

## D-041 cerrado — 2026-11-06 21:08 CET

**Cobertura de exporters Fase4: DONE —17/17 LXC aceptados técnicamente.**
617/618/615/614DONE;180/300/180/180s,32muestrasCPU/RAM/Docker válidas,
backups/idempotencia yno nuevosOOM/reinicios.13aceptadosprevios intactos,sinrepetir.
615/614siguenHTTP503preexistente: monitorizaciónaceptada,aplicacionesNOsaludables.
CRM3.27.4/DB/datos/duplicadosdetenidos/recursosconservados. Sinrelajartolerancias.
17Node/17cAdvisor/11BlackboxUP;17cadenas;Prom/AM yconfig/secretoTelegramintactos;
0erroresnuevosTelegram,canalD039reutilizado,sin nuevaentrega niconfirmaciónhumana.
16backups y12inputs/CT verificados.24testspertinentesPASS. Tiempo:58.1min.
0BLOCKED/0PENDING deexporters; incidencias deapps ycomplementosheredados abiertos.
AlertasF5,dashboardsF6,seguridadF7 NOcompletados. VigilanciaProm/AMcontinúa;
sin atribuir `for` no probado. PolíticaCOMPLETED/permisosvacíos;ejecución detenida.
SinTerraformapply,commit/push niborrados. [Cierre](EXPORTERS-D041-CLOSURE.md),
[prueba17/17](evidence/2026-11-06-d041-final.json). Próximo: revisión/alcanceF5,
sin ejecución automática ni nuevoCT.

## Historial D-040 y anteriores

## D-040 — tiempos de próximas observaciones — 2026-11-06 20:01 CET

Convencionales/Grafana/Blackbox180s(7muestras),CRM/EVA300s(11),Prom/AM600s(21),
a30s. Ventana fijada al inicio; no modificar intervenciones iniciadas ni repetir
los13aceptados. Mantener todoslosgatesCPU/RAM/Docker/exporters/apps/OOM/reinicios,
Prom/AM/Telegram ybackup/rollback. Vigilancia posterior automática existente en
Prometheus/Alertmanager, con anomalías en estado/historial de alertas ynotificaciones;
sin espera900s adicional. No atribuir reglasfor cuyo período no haya transcurrido.
Generador ydriver conectados aconfiguración porCT;17pruebas afectadasPASS.
No procesos activos ni CT autorizado sin intentar:13DONE/4BLOCKED(617/615/614/618).
Sin cambiosproducción,observacionesrepetidas,commit/push. Reentrada de bloqueados
requiere alcance específico; no se deduce de este cambio detiempos.
[Perfiles](VALIDATION-PROFILES.md), [configuración](../../services/common/phase4-validation-profiles.yml).

## Historial D-039 y anteriores

## D-039 cerrado — 2026-11-06 19:46 CET

**Fase4 IN PROGRESS:13DONE/4BLOCKED/0PENDING sin intentar. Ejecución detenida.**
NuevosDONE:622EVA,611Grafana,616Blackbox,610Prometheus;600s/21muestras cadauno,
CPU/RAM/Docker válidas,backup/idempotencia,apps yrecursos sinregresión,nuevosOOM0.
618CRM BLOCKED/ROLLED BACK porbracketRAMvolátil del propio cAdvisor; originales,
Budibase3.27.4/duplicadosdetenidos/DB/volúmenes ycheckpoint restaurados. SKIPseguro
trasaislamiento; no reintento.617/615/614sinintervención. No relajarumbrales.
Prom/AM sanos,17Node/17cAdvisor/11BlackboxUP,13cadenas. TelegramR6/R7API+4,
0erroresnuevos; sinconfirmaciónhumana. AMconfig/secreto intactos,históricoprevio
accesible; observaciónexterna61023muestrascorrectas,independiente dePromAPI.
16backups deDONE revalidados;25tests pertinentesPASS. Tiempo:81.3min.
PolíticaCOMPLETED/permisosvacíos; sinotrosCT,Tfapply,commit/push ni borrados.
Siguientepropuesta:617→618 individualmente;615/614 aplazados,baseline503 permitido
si monitorizaciónválida/sinregresión. Noejecutar sin nuevoalcanceautorizado.
[Consolidado](CRITICAL-D039-EXECUTION.md), [prueba final](evidence/2026-11-06-d039-final.json).

## Historial D-038 y anteriores

## D-038 — perfiles simplificados; grupo STANDARD vacío — 2026-11-06 17:32 CET

**Fase4 IN PROGRESS:9DONE/3BLOCKED/5PENDING. Sin despliegues nuevos.**
STANDARD180s/7, sinwatch900s ni rollback real repetido cuando existe prueba
compatible; CRITICAL600s/21 con continuidad/recuperación específicas. Aplicación
contra baseline,sinregresión; unhealthy previo no veta aceptación de monitorización.
Telegram real porlote/cambio deconfiguración,AMready y errores estables porCT.
Tolerancias eidentidad/frescura intactas; no sustituir ausentes por0.
Perfiles y evaluación preparados localmente;25pruebas afectadasPASS. No se repiten
pruebas comunes ni compatibilidad larga deaceptados. No se certifica el ejecutor
histórico como nuevo ejecutorSTANDARD; su adaptación requiere un objetivo autorizado.
Verificación actual porlectura:9cadenas sanas,9runtimesaceptados intactos,
17Node/17cAdvisor/11BlackboxUP,Prom/AMready200;Telegram56fallos históricos sin aumento.
Pendientes:618CRM,622EVA,611Grafana,616Blackbox,610Prometheus: **todosCRITICAL**.
Cero convencionalesPENDING autorizados; no modificar617/615/614. Política cerrada,
permisosvacíos. No cambiosproducción/apps/DB/recursosPVE ni commit/push.
Siguiente grupo recomendado:618→622; después611→616→610. Requiere autorización
específica, no concedida aquí. Tiempo:3.4min.
[Perfiles](VALIDATION-PROFILES.md), [plan](evidence/2026-11-06-d038-plan.json),
[lectura producción](evidence/2026-11-06-d038-production-check.json).

## Historial D-037 y anteriores

## D-037 cerrado — 2026-11-06 16:38 CET

**Fase 4 IN PROGRESS: 9 DONE, 3 BLOCKED, 5 PENDING. CT 61211 DONE. Ejecución detenida.**
Reentrada exclusiva svc01 con framework D036 `framework-347ef93c2fca` aplicado
mediante IaC: Node Exporter 1.10.2 y cAdvisor 0.60.6 fijados por digest.
80 pruebas locales PASS y compatibilidad fresca de lectura 8/8 antes de intervenir.
Preflight, backups externos/PVE, promtool, rollback coordinado real y reaplicación
idempotente PASS. Inicial 13 muestras/360,188s; vigilancia 31/901,755s; 44 muestras
CPU/RAM válidas de cuatro contenedores, mismo ID/generación/ámbito y tiempos alineados.
NocoDB HTTP200 y PostgreSQL ready; sin nuevos OOM ni reinicios inesperados.
Prometheus/Alertmanager sanos; 17Node/17cAdvisor/11BlackboxUP y nueve cadenas correctas.
Telegram FIRING/RESOLVED aceptados porAPI (+2 envíos,0 errores); recepción humana
no confirmada. Ocho aceptados y procesosProm/AM sin cambios de identidad/reinicio;
CT614 sigue503 preexistente, originales/config intactos y dependencia independiente.
Cuatro backups legibles y hashes locales/PVE verificados; doce inputs coinciden conIaC.
No se ampliaron márgenes ni se desactivaron comprobaciones.
Política COMPLETED, permisos vacíos y avance automático deshabilitado. NoR6/R7 ni
otrosCT, sin Terraformapply/commits/push. Originales, candidatos, backups y HALTs conservados.
Tiempo al cierre documental: 38.0min excluyendo el intervalo sin actividad
registrado de 145.9min; procedimiento productivo25,3min.
[Informe](CT61211-D037-EXECUTION.md), [aceptación](evidence/2026-11-06-d037-completion.json),
[tiempo](evidence/2026-11-06-d037-time.json). Próximo paso: revisión y autorización
separada del siguiente grupo; no ejecutar automáticamente.617/615/614 quedan para recuperación.

## Historial D-036 y anteriores (no autoriza nuevos despliegues)

## D-036 cerrado — 2026-11-06 13:29 CET

**Fase 4 IN PROGRESS: 8 DONE, 4 BLOCKED, 5 PENDING; sin cambios de producción.**
Framework CPU/RAM común corregido y probado: parser único RFC3339Nano, identidad
completa con ámbito LXC/namespace (hay IDs clonados entre motores), unidades,
validación de valores/historial y lector vivo. RAM sin interpolación; CPU conserva
sus extremos y ventanas. Márgenes y frescura intactos; sin fallback ni ceros ficticios.
80 pruebas locales PASS. Compatibilidad final de lectura **8/8**, 147 muestras
válidas sobre31 contenedores,56 inputs y DockerIDs/StartedAt/restarts intactos;
recursos PVE verificados,17Node/17cAdvisor/11BlackboxUP y ocho cadenas sanas.
Se conserva rechazo inicial de frescura/futuro625 sin muestra completa; la segunda
pasadaPASS no elimina ese antecedente ni demuestra su causa. No cambiar su perfil.
Preparación61211 `framework-347ef93c2fca` solo local; auditoría fresca,
run/checkpoint nuevos y alcance autorizado requeridos antes de reentrada.
No exporters/reinicios/apps/recargas/Telegramtests/Terraformapply/commits/push.
PolíticaBLOCKED y HALTs/backups preservados. Tiempo:44.0min.
[Informe y procedimiento](VALIDATION-FRAMEWORK.md). Siguiente paso: revisar y
reintentar exclusivamente61211 en otra intervención; no otrosCT ni reparar614.

## Historial operativo D035 y anteriores


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

## Historial deD034 y anteriores


## D-034 cerrado — 2026-11-06 11:35 CET

**Fase4 IN PROGRESS:8 DONE,3 BLOCKED,6 PENDING. Lote: HALT GLOBAL.**
SKIP AND CONTINUE implementado mediante política/driver versionados, un intento por
CT y clasificación cerrada. Orden autorizado614→61211,617/615 aplazados.
CT614 falla preflight:sgtm ysgtm_preview originalesunhealthy, /healthy503 en8091/8092.
Originales/appIDs/config preservados y cobertura previa íntegra, pero no se puede
confirmar **aplicación original funcionando**. Ese requisito explícito de D034
veta el salto, incluso sin cambios activos. No se inició61211.
Sin staging remoto, backups nuevos, apply, recargaProm ni reinicios. Cobertura
17Node/17cAdvisor/11Blackbox y ocho cadenas sanas;24 archivosProm sin cambios,
identidades de ocho aceptados yProm/AM intactas. OOMdelta614=0; sin nuevos errores
Telegram en contraste de contadores; no prueba nueva de entrega.180s/900s,
idempotencia/rollback real y métricas de candidatos NO ejecutados por fallo previo.
Política BLOCKED, permisos vacíos, HALTs conservados, sin procesos de avance.
36 pruebas pertinentes PASS. Sin commits/push. Tiempo:10.8min.
[Cierre y evidencia](SKIP-AND-CONTINUE.md), [cola](../../services/common/phase4-recovery-queue.yml).
Siguiente objetivo recomendado:61211, tras resolver el veto de aplicación de614.
No investigar ni intervenir617/615 ahora, noCRM/EVA/Grafana/Blackbox/exporters610.

## Historial previo D033/D032/D031


## D-033 cerrado — 2026-11-06 11:15 CET

**Fase4 IN PROGRESS:8 DONE,2 BLOCKED,7 PENDING. CT617 BLOCKED / ROLLED BACK.**
Run `integration-20261106T100830Z`. Primer apply rechazado por guarda `Held candidate differs`:
el proyectoCompose nuevo seguía consultando el nombreheld histórico. Se detuvo
Node original transitoriamente; no se creó ningún exporter nuevo. Recuperación
coordinada verificada: originales/apps/config intactos, proxy403/backend200,
checkpointProm8 y24/24 archivos exactos, ocho aceptados sin cambios,17/17/11 UP.
Sin nuevosOOM ni reinicios de apps; loggers CPU/RAM detenidos, backups conservados.
**600s/900s, idempotencia y cadenaTelegram NO ejecutadas** por fallo previo; no DONE.
Prom/AM ready200; ningún testTelegram nuevo. Corrección de nombresheld por revisión
más regresión apply→rollback→reapply/idempotencia preparada **solo local**, no aplicada.
27 pruebas pertinentes PASS. Política BLOCKED sin permisos de apply/recovery ni
continuación automática; HALTs históricos y nuevo preservados. No615 ni otrosCT,
sin commits/push. Tiempo:8.0min; ver [cierre617](CT617-D033-EXECUTION.md).
Próximo paso: revisar corrección local de aislamientoheld y autorizar otra reentrada
exclusiva617 si procede; no reutilizar este run ni declarar RAM validada en617.

## Historial de cierre previo


Actualizado:2026-11-05 22:01 CET. **D-031 terminado con bloqueo seguro. Política BLOCKED.**
Sustituye instrucciones históricas D030 y contadores provisionales de9. No repetir
623 ni los siete CT previamente aceptados. No avance automático pendiente.

## A. Objetivo

17/17 LXC, incluidosCRM/EVA, con CPU LXC real cgroup(textfile lxc_cpu_*), RAMLXCFS,
CPU física nativa desactivada, métricas Docker individuales, backups/restauración,
rollback coordinado, idempotencia, estabilidad y cadena exporter→Prometheus→reglas
→AM→Telegram. Targetup/exporter desplegado no prueba fuente fiable ni cadena.
Criterios completos:[fase4](phases/04-exporters-coverage.md). F4 NO DONE.

## B. Estado exacto

**17 DONE técnicos,0 BLOCKED deexporters,0 PENDING derollout;17total. Apps615/614siguen503.**
Prometheus conserva17Node/17cAdvisor/11Blackbox up. Diecisiete fuentes/cadenas fiables,
no diecisiete. Los demás mantienen cobertura legacy sin promover a fiable.

|CT|Servicio|Estado|Node/cAdvisor reales|Disponibilidad técnica|Métricas/Prometheus|
|---|---|---|---|---|---|
|624|infra-journal-web|DONE técnico|1.10.2/v0.60.6|Web200|LXC/Docker y cadena aceptados|
|626|infra-journal-api|DONE técnico|1.10.2/v0.60.6|API200|LXC/Docker y cadena aceptados|
|625|infra-journal-db|DONE técnico|1.10.2/v0.60.6|PGready|LXC/Docker y cadena aceptados|
|613|infra-hola|DONE técnico|1.10.2/v0.60.6|Sin app|LXC/Docker y cadena aceptados|
|621|infra-project-gestion|DONE técnico|1.11.0/v0.60.6|Focalboard200|LXC/Docker y cadena aceptados|
|620|infra-excraper|DONE técnico|1.10.2/v0.60.6|Workers200 y Redis|LXC/Docker y cadena aceptados|
|619|infra-pulpo|DONE técnico|1.10.2/v0.60.6|n8n200/PGready|LXC/Docker y cadena aceptados|
|623|infra-gestoria|DONE técnico|1.11.1/v0.60.6|Odoo200/PGready|LXC/Docker y cadena aceptados|
|617|infra-orbit|DONE técnico D041|1.10.2/v0.60.6|Proxy403 esperado/backend200,sinregresión|LXC/Docker/cadena,backup/idempotenciaPASS|
|615|infra-mailerblend-edge|DONE técnico D041|1.10.2/v0.60.6|HTTP503preexistente,sinregresión;NOsaludable|LXC/Docker/cadena,backup/idempotenciaPASS|
|614|infra-nucleoedge|DONE técnico D041|1.10.2/v0.60.6|HTTP503preexistente,sinregresión;NOsaludable|LXC/Docker/cadena,backup/idempotenciaPASS|
|61211|svc01|DONE técnico D037|1.10.2/v0.60.6|NocoDB200/PGready; apps sin reinicios|LXC/Docker y cadena aceptados; backups/rollback/idempotencia PASS|
|618|infra-composable-crm|DONE técnico D041|1.10.2/v0.60.6|UI/health/ready200;Budibase3.27.4preservado|LXC/Docker/cadena,backup/idempotenciaPASS|
|622|infra-eva-assistant-bot|DONE técnico D039|1.11.1/v0.60.6|API/Focalboard200/PGready|LXC/Docker/cadena;21/600s,backups/idempotencia;Telegramporlote|
|611|infra-grafana|DONE técnico D039|1.10.2/v0.60.6|Grafana200|LXC/Docker/cadena;21/600s,backups/idempotencia;Telegramporlote|
|616|infra-blackbox|DONE técnico D039|1.10.2/v0.60.6|Salud200;11targetsconservados|LXC/Docker/cadena;21/600s,backups/idempotencia;Telegramporlote|
|610|infra-prom|DONE técnico D039|1.10.2/v0.60.6|Prom/AMready200;sinreinicio|LXC/Docker/cadena;21/600s,backups/idempotencia;Telegramporlote|

Backups/idempotencia: los ocho DONE previos conservan su evidencia histórica;
no se reaplicaron para auditarlos. CT61211 añade cuatro archivos verificados
local/PVE, rollback coordinado y segunda aplicación sin recreación/recarga D037.
617 permanece revertido;615/614 no tienen cambios activos. Los cinco PENDING no
han pasado los gates de migración. La auditoría histórica de35archivos es anterior
aD037; no equivale a una nueva restauración de todos los servicios.

## C. Trabajo IaC y validaciones

Terraform+inventarioYAML+scripts/Compose; pins por digest en phase4-images.json,
estados en exporter-migration.yml. No cambios de recursosPVE/apps/DB/volúmenes.

D031 introdujo `resume-623-cadence.py`: revalida originales/held, crea backup
fresco de exporters y nuevo checkpointProm610, archiva HALT sin borrar, usa proyecto
Compose cadence30 exclusivo para623, conserva el candidato anterior. Ensaya
rollback/reanudación y segunda aplicación con mismosIDs; observa600s/21. La
cadencia fija también se prepara para nuevosR4/R5; siete aceptados no se alteran.

`apply-incremental-config.py` valida config/reglas y discovery real con promtool de
la imagen instalada, sin red/escritura en runtime durante validación.17/17/11 y
unicidad comprobados antes de aplicar; file_sd sin reload, SIGHUP solo si cambia
regla; IDs/StartedAt deProm/AM no se recrean. Baselines y hashes rechazan drift.

`recover-approved-wave.py` deja preflight fallido sin cambios o restaura checkpoint
antes de exporterslegacy; `rollback-post-watch-617.py` revoca provisional y restaura
solo617/checkpoint8. Específico al estado previo: **ya ejecutado, no repetirlo**.
Política permite recovery separado de apply; actualmente ambos vetados al cierre.

[623 PASS](evidence/2026-11-05-623-execution.json),
[617 final](evidence/2026-11-05-617-execution.json),
[615 preflight](evidence/2026-11-05-615-blocker.json),
[auditoría](evidence/2026-11-05-final-audit.json),
[reproducibilidad](evidence/2026-11-05-reproducibility-final.json).
56 inputs activos de exporters+24 archivos Prom coinciden con generadores/registro
y baselines privados. No dependencia /tmp local para servicios; salidas locales
.runtime son preparación o evidencia, no prueba de despliegue.

## D. Incidencias y causas

619(D028/D029):128MiB generó presión;256MiB aprobado. Compose encuentra por etiquetas
un candidato renombrado: proyecto exclusivo evita reutilización de rechazado.
CPU se comparaba cacheada contra Docker actual, descartando timestamps. Corregido
por ID/StartedAt, mismo instante/ventana y cgroup, manteniendo max(1s,3%), sin
normalización porCPU en acumulativos. CarreraPID0 del lector corregida.619 pasó
21/600,442s y watcher31/901,725s, sigue DONE. [RCA](CT619-CPU-RCA.md).

623: dinámica30→60s y jitter1 permiten esperas hasta120s, incompatible con frescura90s;
hueco observado113,635s. La muestra original fallida no está completa, no atribuir
con certeza única a test-nginx. D031 fija30s, dinámica/jitter desactivados; no cambia
umbrales, privilegios, sockets ni límites. Node1.11.1 conservado según pin y runtime verificados,
por digest del candidato autorizado. Candidato viejo y originales retenidos.
Resultado21/600,804s +watch31/901,544s PASS, Odoo/PG disponibles, sin nuevosOOM ni
reinicios de apps; memoria.max registra reclaim histórico, no afirmar cero eventos
max/high por tenerOOM0. [Diagnóstico](evidence/2026-11-03-623-cadence-root-cause.json).

617: inicial13/360,537s y TelegramAPI+2/0errores PASS, pero postwatch a120,026s
falla RAM analytics-ingest-gateway:47.448.064B cAdvisor vs61.263.872B Docker,
cgroup60.858.368B; diferencia13.815.808B>12.252.774,4B(20%). TimestampcAdvisor
anterior unos7,18s. No concluir error de exporter ni falso positivo sin RAM de
instantes equivalentes. Se conserva muestra completa; el historial continuo de
esa ejecución registra CPU, **no RAM histórica subsegundo**. No reconstruirla.
Posible siguiente diagnóstico: RAM gauge con timestamps iguales y lecturas Docker/
cgroup acotadas; no reutilizar sin más interpolación monótona de contadorCPU para
RAM, que puede bajar. No subir20% ni eliminar comprobación para pasar.
Watcher31/901,797s FAIL,>=600s desde anomalía; rollback617 y retirada del registro
completo. [Fallo exacto](evidence/2026-11-05-617-post-watch-failure.json).

615: ambos /healthy503 y contenedoresunhealthy heredados; preflight detuvo antes
de cambios. Reparación funcional/apps no autorizada por D031.614 también503 en
lectura anticipada, no se intervino. Ese veto histórico fue sustituido por D035 para problemas preexistentes aislados; D037 acepta61211.

## E. Producción y preparación

Producción: nueve CT corregidos, incluida reentrada61211 con frameworkD036 y
cadencia30s. Los otros ocho aceptados conservaron sus inputs y runtime.617 tiene
originales1.10.2/0.47.2 y candidatos detenidos;615/614 originales sin modificar,
503preexistente.618/622/611/616/610 siguen sin migración de exporters. Prom610
recibió solo cambios mínimos de configuración de integración/reversión porCT,
con backup/promtool/recarga controlada, manteniendo17fuentes y11Blackbox.

Prom/AM sanos, sin regla temporal de prueba. Telegram: cuatro confirmaciones
humanas históricas624/626/625/613; ensayos posteriores solo aceptaciónAPI.
61211 añade FIRING/RESOLVEDAPI+2/0erroresD037. F3UATWaiver no se extiende aF4;
CPU>90%/for10m no se demuestra con esta prueba temporal.

El código comúnD036 está aplicado a61211 y preparado localmente para candidatos
futuros; no se reaplicó al resto ni demuestra compatibilidad deR6/R7. Conserva
especificidades de recursos/sockets porCT. No commits/push; árbol Git amplio con
staged/unstaged/untracked heredados. No indexar cambios ajenos ni publicar backups.
Riesgos y secretos heredados siguenF7. [CierreD037](CT61211-D037-EXECUTION.md).

## F. Seguridad y recuperación

D03761211: backups locales yPVE, hashes y procedimiento en
[CT61211-D037-EXECUTION](CT61211-D037-EXECUTION.md). Checkpoint previo8 y estadofinal9;
no restaurar un checkpoint histórico sobre producción actual sin plan coordinado.


Run principal:integration-20261102T223431Z. La reentrada623D031 usa checkpoint nuevo
`monitoring-d031-<UTC>` bajo privado623, y directorioProm `integration-<UTC>-623`.
Rutas/hashes exactos en evidencia623 y auditoría35 backups.

- Externo privado:$HOME/.local/share/mailerblend-recovery/phase4/.
- PVE:/mnt/storage/mailerblend-recovery/phase4/.
- CT:/opt/exporter-phase4-pilot/<run>-<CT>/;624 usa directorio piloto sin sufijo.
- Prom610:/opt/infra-prom/.runtime/<run>-<CT>/; config /opt/infra-prom/config/,
  Compose real /opt/infra-prom/docker-compose.yml.
- Históricos:pilot-624-20261102T161242+0100, journal-20261102T190629Z,
  integration-20261102T204936Z(P0/R1), parcial613 yV2 conservados.

No borrar imágenes, originales, volúmenes, baselines, HALT615 ni HALT617. Rollback:
resolver/retirar test; checkpointProm antes de legacyexporters; verificar IDs,
imágenes/readiness/apps y fuentes aceptadas. No restaurar el checkpoint7 de623
sobre un estado con otrosCT aceptados: respetar checkpoints coordinados.
[Runbooks](PROGRESSIVE-ROLLOUT.md), [P0/R1](P0-R1-EXECUTION.md),
[Journal](JOURNAL-EXECUTION.md). No duplicar con comandos manuales improvisados.
SSH BatchMode=yes, StrictHostKeyChecking=yes, UserKnownHostsFile=$HOME/.ssh/known_hosts;
no defaults inseguros, keyscan como aceptación ni configuraciónSSH del dueño alterada.
No mostrar env/tokens/estados/archivos de backup completos.

## G. Pendientes y dependencias

NoCTpendiente debundleexporters. Losincidentes617held/618RAM/615-614aceptación
se cierran para monitorización;HTTP503de615/614 no reparados. RevisiónF5dealertas
(predicados/for/routing),F6dashboards yF7hardening separados. ComplementosF4aún
noejecutados (jobpropioGrafana,sondasJournal/fuentePVE) eINC001–005 conservados.
No ampliar elalcance ni asumirUATpor17/17.

## H. Reanudación

Solo lectura, usando salidas nuevas:

```bash
cat AGENTS.md docs/roadmap/CURRENT-STATUS.md docs/roadmap/PHASE4-HANDOFF.md
cat docs/roadmap/EXPORTERS-D041-CLOSURE.md services/common/phase4-execution-policy.yml
git status --short
git diff --check
python3 scripts/phase4-validation-profiles.py --output /tmp/phase4-next-plan.json
python3 scripts/check-incremental-chain.py --ct 614 --service infra-nucleoedge --output /tmp/phase4-next-614.json
```

Elplan debe devolver17aceptados,0bloqueados,0pendientes. No apply ni reutilizarD041,
ni ejecutar--all/rollbackautomático sobrecheckpointshistóricos. Backups/secretos
privadosfueraGit; nocontenidoenv/logscompletos. Políticacerrada,permisosvacíos.

Prompt sugerido:

> Lee AGENTS.md, ROADMAP, CURRENT-STATUS, DECISIONS D041, PHASE4-HANDOFF y
> EXPORTERS-D041-CLOSURE. Confirma porlectura17/17exporters aceptados sin repetir
> despliegues. Prepara revisiónF5dealertas ypendientes complementarios, separando
> 615/614HTTP503preexistentes. No modificarproducción,apps/datos/recursos ni hacer
> commit/push. Presenta unalcance concreto antes deejecutar la siguiente fase.

## I. Paradas

Fallo de validación/probe/watcher veto irrevocable a avance: mantener baseline,
observar>=600s desde anomalía y restaurar estado seguro. No dispensar por muestras
posteriores limpias. Parar por SSH/TLS, drift no explicado, backup/hash/restauración,
OOM/reinicio/PSI, métricas CPU/RAM inconsistentes, ausencia/frescura, huecos>2s,
Prom/AM/Telegram o idempotencia. No CPU cero ni fallback físico por ausencia.
R2–R5 min180s/7;623 tras incidencia600s/21;R6/R7 600s/21; watcher900s y Prom/AM
continuos. DatosdirectosLXC15s, Prom45s con scrape30, métricasDocker90s; no ampliar
límites. Aceptación final incluye watcher, no basta PASS inicial.

[Tiempo/evidencias](evidence/2026-11-05-resume-time.json). Sesión terminada con
bloqueo seguro; sin otro lote ni procesos de avance programados.

Cierre final: 2026-11-05 22:04 CET. Tiempo transcurrido registrado: 58.9 minutos (incluye observaciones y recuperación). 31 pruebas de regresión PASS; enlaces locales y `git diff --check` PASS; Prometheus/Alertmanager ready HTTP200; sin procesos activos de rollout. Sin commit/push.


## D-032 — diagnóstico y preparación617, sin despliegue

2026-11-06 10:35 CET. Se mantiene8/2/7 y políticaBLOCKED.
Defecto temporalRAM confirmado en validador, causa histórica única no demostrada.
480 lecturas617 Docker/cgroup coinciden; control623 cinco contenedores alineados
PASS;44 regresionesPASS. Ocho aceptados sin cambios de IDs/hashes; no615.
Node623 realmente1.11.1; texto anterior1.10.2 corregido por evidencia runtime.
[Informe617, mejoras comunes y procedimiento exacto](CT617-RAM-RCA.md).
Despliegue requiere revisión/aprobación nueva; no usar el prompt previo como
permiso de apply ni habilitar política por esta preparación.


## Seguimiento D-042 — consolidación Git

2026-11-06 (Europe/Madrid). El propietario autoriza commits/push normales de IaC
segura revisada; sustituye las prohibiciones históricas de commit/push solo para
esta consolidación. No autoriza producción. Ver [auditoría](GIT-CONSOLIDATION-D042.md).
Cobertura17/17 D041 conservada; pendientes de apps y complementos sin aceptación nueva.
