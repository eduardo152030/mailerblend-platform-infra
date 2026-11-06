# Roadmap de infraestructura

## D-042 — consolidación Git — 2026-11-06T21:20:11+01:00

F7-01 DONE para IaC de monitorización curada: push normal SSH confirmado de cinco
commits nuevos y cuatro previos; origin/main y main iguales en `44c0e8b` tras ese
push (0ahead/0behind). Cierre documental separado, con verificación final en sesión.
425 rutas versionadas en el push principal,230 tests y validadores Prom/AM PASS;
cero hallazgos de secretos nuevos en selección/historial saliente. Respaldo privado
verificado. Árbol no limpio: EVA funcional y aplicaciones Gestoría/Journal
conservadas fuera del alcance; secretos/estado locales ignorados. F7 global
IN PROGRESS, F7-04 y rotación de secretos históricos pendientes; F4exporters17/17
conservado, no nueva validación productiva. Sin despliegues ni reinicios.
[Informe](GIT-CONSOLIDATION-D042.md), [evidencia](evidence/2026-11-06-git-consolidation.json).
Siguiente paso: rotación de secretos históricos y revisión separada de cambios
de aplicaciones; F5/F6 y complementos siguen pendientes.

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

## Historial anterior a D036


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

## Historial previo aD035


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

## Historial de cierres anteriores


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


## Seguimiento D-032 — 2026-11-06 10:35 CET

Fase4 IN PROGRESS. **8 DONE,2 BLOCKED,7 PENDING sin cambios de producción.**
Diagnóstico617 y código local preparados; despliegue NO autorizado en esta tarea.
Defecto confirmado: RAM cacheada comparada con lectura actual. Causa única del
fallo histórico no demostrable sin RAM histórica equivalente; no atribuir error
a cAdvisor. 480 lecturas617 Docker/cgroup coincidentes; control623 cinco
contenedores alineados PASS;44 pruebas locales PASS. Ocho aceptados y56 inputs
intactos,17/17/11 up y cadenas sanas. CT623 Node real1.11.1 (errata textual anterior).
Política BLOCKED/HALTs conservados; no615 ni reinicios/despliegues/commits/push.
[Diagnóstico y procedimiento617](CT617-RAM-RCA.md). Próximo paso: revisión del
diagnóstico y autorización exclusiva617 antes de habilitar la ejecución.


Actualizado: 2026-11-03 (Europe/Madrid). Fuente central de seguimiento para Proxmox,
Terraform, Docker Compose, Prometheus, Alertmanager, Telegram, Grafana y aplicaciones.
Para retomar el trabajo, leer primero [CURRENT-STATUS](CURRENT-STATUS.md) y después
la fase activa. Las decisiones están en [DECISIONS](DECISIONS.md).

## Estado real

| Fase | Objetivo y alcance | Estado | Implementación / producción / aceptación |
|---|---|---|---|
| [1. Monitoring Foundation](phases/01-monitoring-foundation.md) | Base Prometheus/Alertmanager, persistencia y discovery | DONE | Base desplegada y verificada por API; cobertura completa y calidad quedan en F4 |
| [2. Telegram Alerting & Blackbox Deduplication](phases/02-telegram-blackbox.md) | Entrega FIRING/RESOLVED y evitar incidentes equivalentes | DONE | Desplegada, entrega confirmada por propietario, 11 sondas aceptadas |
| [3. Infrastructure Recovery — CRM & EVA](phases/03-infrastructure-recovery.md) | Recuperar capacidad/servicios preservando datos | **DONE — Accepted with UAT Waiver** | Ejecutada y técnicamente validada; aceptación formal del propietario el 2026-11-02 |
| [4. Exporters & Monitoring Coverage](phases/04-exporters-coverage.md) | Métricas correctas y cobertura de los17servicios | **DONE — coberturaexporters** | D04117/17; complementosheredados abiertos; alertas/dashboards/seguridad no incluidos |
| [5. Alerting Optimization](phases/05-alerting-optimization.md) | Umbrales, severidad, rutas, inhibición y mensajes | TODO | Configuración básica existente; optimización pendiente, depende de métricas fiables |
| [6. Grafana & Dashboards](phases/06-grafana-dashboards.md) | Dashboards útiles con datos y ámbitos correctos | TODO | Grafana disponible; configuración/provisioning y aceptación visual pendientes |
| [7. IaC Reliability, Security & Disaster Recovery](phases/07-iac-security-dr.md) | Despliegues seguros, herramientas reproducibles y DR sostenido | TODO | Hay mejoras parciales desplegadas; faltan seguridad global, CI, política DR y cierre Git |

Cada ficha contiene objetivo, alcance, dependencias, tareas, riesgos, entregables,
criterios de aceptación y evidencias. DONE se refiere al alcance definido, no implica
que hayan desaparecido todos los problemas heredados del proyecto.

## Numeración histórica

No renombrar evidencias ni perder sus referencias:

| Documentación anterior | Fase central actual |
|---|---|
| “Fase 1” de [DEDUPLICATION.md](../../services/infra-prom/DEDUPLICATION.md) | Fase 2 |
| “Fase 2” de [PHASE2-INCIDENTS.md](../../services/infra-prom/PHASE2-INCIDENTS.md) y [PHASE2-EXECUTION.md](../../services/infra-prom/PHASE2-EXECUTION.md) | Fase 3 |
| Investigación de aislamiento LXC y Docker | Fase 4 |
| Antiguas propuestas de optimización / documentación | Redistribuidas entre F5 y F7 |

## Cómo se actualiza

1. Identificar fase/tarea y autorización antes de actuar. Registrar ampliaciones.
2. Separar cuatro hitos: **local**, **validado**, **desplegado**, **aceptado**.
3. Usar TODO, IN PROGRESS, BLOCKED o DONE. Documentar causa y salida de un bloqueo.
4. Vincular resultados fechados y criterios, sin secretos. Los JSON de auditoría son
   instantáneas, no garantías permanentes de disponibilidad.
5. Al finalizar, actualizar ficha, este índice, CURRENT-STATUS y decisiones nuevas.
6. Revisar Git y enlaces. No confundir cambios sin commit con evidencia de producción.
   El [inventario de trabajo previo](WORK-AUDIT.md) distingue cambios locales y runtime.

La aceptación de F3 dispensa expresamente la UAT manual adicional; **no demuestra que
todos los flujos funcionales hayan sido probados**. Los tres healthchecks heredados,
el digest diario de EVA y Nucleotecnológico continúan registrados como pendientes.

## Próxima puerta — cobertura17/17 cerrada D-041

SinCTpendientes ni bloqueados demonitorización. RevisaralertasF5 ycomplementos
heredados antes deuna nuevaautorización.615/614503 ylosotrosINC siguen registrados,
no reparados por elrollout. No repetir aceptados ni continuar--all.
[Handoff](PHASE4-HANDOFF.md), [cierre](EXPORTERS-D041-CLOSURE.md).
