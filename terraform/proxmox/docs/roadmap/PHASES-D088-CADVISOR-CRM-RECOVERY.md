# D088 — cAdvisor623/618 y recuperación de CRM

13 de noviembre de 2026, Europe/Madrid. Incidencia operativa en Fase4.
Exporters & Monitoring Coverage, Fase5. Alerting Optimization y Fase6.
Grafana & Dashboards. Estado: DONE técnico, observación600s/21 PASS.
No reabre ni amplía el rollout histórico. Antecedente:
[D083](PHASES-D083-MONITORING-RECOVERY.md).

## Alcance autorizado

El propietario pide solucionar la alerta repetida cAdvisor Gestoría y los estados
CRITICAL623/618, aumentando moderadamente memoria si es necesario. Se interpreta
como autorización de recuperación acotada, incluidos límites y arranque del CRM
existente; se registra antes de mutar. No otrosCT, nuevasfuncionalidades, recursos
PVE, aplicaciones ajenas, volúmenes, commits ni push.

## Diagnóstico

CT6234096MiB con3570disponibles; CT6186144MiB con4175disponibles. No evidencia
que justifique ampliar RAM de los LXC. Ambos cAdvisor tienen memory.max128MiB,
consumo en el techo, swap y millones de eventosmax:17901473/20539033 albaseline,
OOM0. PSI full instantáneo13,93%/17,07%. Tras subir a256MiB persiste presión:
principal consumo slab_reclaimable≈225/241MB, no solo heap deGo. Se conserva
[evidencia previa](evidence/2026-11-13-d088-before.json) y
[paso intermedio](evidence/2026-11-13-d088-256m-intermediate.json).
No se presume que la caché ya esté liberada ni se ejecuta drop_caches.

CRMAPI618 estaba detenido desde11nov17:30:28UTC, exit0/OOMfalse,
restartunless-stopped; ApplicationContainerMissing FIRING. PostgreSQL623 y
Budibase618 activos. No se atribuye el estado a falta global deRAM.

## Corrección e IaC

[Receta](../../scripts/recover-cadvisor-crm-d088.py) ejecutada porstdin mediante
SSH estricto, known_hosts delpropietario yBatchMode. cAdvisor128→256→384MiB,
CPU0,5 intacta. memory-swap384MiB es techo combinado, no384MiB de swap adicional;
antes era256MiB combinado. memswap_limit igual a mem_limit conserva política
sin nueva asignación de swap, aunque puede quedar swap residual previo.
Actualizados Compose activos y overlays versionados exclusivos
[623](../../services/common/recovery-d088/623/cadvisor-limits.yml) y
[618](../../services/common/recovery-d088/618/cadvisor-limits.yml).
Sin pull, Composeup, recreación ni reinicio deexporters.

CRM: dockerstart delcontenedor existente y restartalways enruntime/Composeactivo,
[Composefuente](../../services/infra-composable-crm/compose/crm-api/docker-compose.yml)
y[overlay](../../services/infra-composable-crm/recovery/healthchecks/crm-api.compose.yml).
Mismo ID/imagen/mounts. Inicio13nov00:11:39UTC; /ready200 yhealthy.
No ensayo de reboot, nuevaimagen, migración SQL ni modificación de datos.

Primer intento devalidaciónCompose falló por EXPORTER_BIND_IP ausente; archivo
restaurado antes dedockerupdate. Receta corregida conIP exacta porCT. Segundo
intento detectó que ComposeactivoCRM esJSON privado, noYAML: límites cAdvisor
ya aplicados, CRM aún sin cambios. Se añadió soporte JSON y se completó.
Sin recreaciones en losintentos. La posterior comparación de mounts requirió
ordenar por destino; la igualdad no depende delorden deDockerinspect.

## Backups y rollback

Inputsoriginales ybaseline privados en /root/monitoring-recovery-d088 de cadaCT,
SHA256 verificado; copia comprimida fueraPVE bajo directorio privado deloperador.
Extracción aislada con hashes3inputs623 y4inputs618 PASS; no publicarCompose
privado. Sin restauraciónDB porque no se cambian datos ni imágenes.

Rollbackcoordinado: validaridentidad actual contra baseline, restaurar cadainput
mediante manifest privado y validarCompose conIP exacta; restaurar límites
cAdvisor128MiB y techo combinado256MiB con dockerupdate. Revertir restartCRM
alvalorbaseline sinpararCRM ni restaurarvolúmenes. Conservar copias yevidencias.
Rollbackproductivo noejecutado: reducir alcuello demostrado provocaría regresión.

## Validación y límites

Prom/AMready200, GrafanaDBok/health200, Gestoría loginlocal200/PGready,
CRMready200. Consultas del dashboard realmente desplegado leídas en611 y
resueltascontraPrometheus: ambosOverall0=HEALTHY, Monitoring1=HEALTHY,
Application2=HEALTHY(readiness), Alertas0; CPU/RAM/disco válidos. RAM≈15%/36%.
[Evidencia dashboard](evidence/2026-11-13-d088-grafana-deployed-queries.json).
ElJSON local difiere deldesplegado; no se sincroniza ni se modificaGrafana.
No se afirma captura visual de navegador ni aceptaciónhumana deTelegram.

Segunda aplicación no cambiaID/StartedAt/imagen/mounts/CPU ni reiniciaCRM.
[Aplicación](evidence/2026-11-13-d088-apply.json),
[verificación](evidence/2026-11-13-d088-verify.json).
Observación mediante [lector](../../scripts/observe-cadvisor-d088.py),
[serie](evidence/2026-11-13-d088-observation.json):600s/21 cada30s,
API targets y lecturadirecta paralela CPU/RAM. 21/21 PASS; máximoscrape0,198s ydirecto0,047s, ceroalertas.
No se modifican timeout, for, reglas, silences, discovery niTelegram.
No se certifica recepción humana de RESOLVED ni seenvía prueba sintética nueva.

Cierre:600,029s monotónicos/21muestras PASS, OOM0 y sin reinicios nuevos;
PSIavg10/avg60 cero enambos. Los sellosUTC se conservan en la evidencia.
CompilaciónPython, validaciónCompose, enlaceslocales ygitdiffcheck PASS.
[Resultadofinal](evidence/2026-11-13-d088-result.json).
Siguiente: vigilancia posterior existente enPrometheus/Alertmanager.
El slab recuperable618 sigue cercano al límite384MiB, con PSI0 y scrapes
estables; no se garantiza estabilidad indefinida ni se aumenta más memoria. Si aparece anomalía,
no declararDONE ni ocultarla medianteumbral oreset delbaseline.
