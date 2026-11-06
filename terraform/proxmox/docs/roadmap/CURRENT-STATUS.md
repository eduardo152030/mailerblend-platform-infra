# Estado actual del proyecto

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

## Estado real

17DONE:624/626/625/613/621/620/619/623/61211/622/611/616/610/617/618/615/614.
0BLOCKED deexporters,0PENDING derollout.615/614 mantienen503 yalertas;noapphealthy.
Losproblemas deaplicación no reabren retrospectivamente laaceptación de métricas.

## Hitos conservados

F1 y F2 DONE. Journal624/626/625 aceptados técnicamente por propietario.
**F3 DONE — Accepted with UAT Waiver:** verificaciones técnicas y restauraciones
pasaron; CRM/EVA operativos según comprobaciones. UAT manual no ejecutada y dispensada
por propietario; no demuestra todos los flujos funcionales. Ver
[PHASE2-EXECUTION](../../services/infra-prom/PHASE2-EXECUTION.md).
CRM/EVA no fueron modificados durante este lote.

## Pendientes heredados

| ID | Pendiente | Seguimiento |
|---|---|---|
| INC-001 | Healthcheck Budibase y Redis externo | F4-08 TODO |
| INC-002 | Healthcheck API CRM usa wget ausente | F4-08 TODO |
| INC-003 | Healthcheck Focalboard usa curl ausente | F4-08 TODO |
| INC-004 | Digest diario EVA, crontab/apk heredados | F7-07 TODO |
| INC-005 | Nucleotecnológico / CollectEndpointDown, RCA pendiente | Conservar sus dos sondas; no dar por reparado |
| R-001 | CoberturaLXC17/17cerrada; fuentePVE explícita aún pendiente | ComplementoF4 |
| R-002 | Promoción global del contrato CPU y compatibilidad dashboards | F4-10/13 pendiente, F6 |
| R-003 | Secretos/estado/hardening heredados | F7 TODO, no corregidos por Journal |
| R-004 | Árbol Git amplio pendiente de commits curados | F7-01, [WORK-AUDIT](WORK-AUDIT.md) |

Roadmap y decisiones siguen como fuente central; secretos y backups privados fuera de Git.

Cierre final: 2026-11-05 22:04 CET. Tiempo transcurrido registrado: 58.9 minutos (incluye observaciones y recuperación). 31 pruebas de regresión PASS; enlaces locales y `git diff --check` PASS; Prometheus/Alertmanager ready HTTP200; sin procesos activos de rollout. Sin commit/push.

CierreD032: 2026-11-06 10:56 CET. Tiempo registrado: 39.1min. Enlaces locales, secreto-signaturas y `git diff --check` PASS; sin commit/push/staging. [Validación local](evidence/2026-11-06-617-local-validation.json).
