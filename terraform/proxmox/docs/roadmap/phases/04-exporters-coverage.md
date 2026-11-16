> D041: **DONE coberturaexporters17/17**, sinbloqueadosderollout.

## IA-CHAT — integración desplegada y estabilidad PASS (2026-11-13, Europe/Madrid)

Fase 7. IaC Reliability, Security & Disaster Recovery; complementos de Fases 4 y 6.
Implementación y pruebas técnicas DONE: CT 630/631 adoptados en Terraform sin
recreación, plan acotado no-op y 18 entradas anteriores del estado intactas.
YAML y configuración canónica por servicio, inventario individual/global y Notes
actualizados. CPU cgroup y RAM LXCFS verificadas; Node Exporter nativo en ambos,
cAdvisor solo en 631 y cinco targets nuevos. Prometheus/Blackbox integrados de
forma aditiva; Grafana Fleet/Details contempla cAdvisor N/A en 630.

PASS: 600 segundos / 21 muestras sin anomalías, 136 consultas reales de Grafana,
reinicio de ambos CT, autenticación, chat, visión, thinking, búsqueda, RAG e historial.
Segunda aplicación sin escrituras de configuración, recargas ni reinicios.
Backup final de 631 verificado por SHA256/zstd/tar; README operativo en PVE.
27 hashes de configuración PVE protegidos iguales; CT 627 no intervenido.
Sin commits ni push.

Voz funcional con calidad limitada: small/int8, 4 de 5 palabras correctas en el WAV
sintético (WER 20 %). Con RAG/STT y exporters, 631 alcanza 2,69 GiB residentes /
2,85 GiB de working set; propuesta de 4096 MiB sin aplicar, límite de 3072 MiB
conservado. Cuenta y Knowledge técnicos retirados; primer administrador disponible.

Aceptación completa IN PROGRESS: reservas DHCP, administrador y UAT móvil/voz del
propietario. Restauración funcional y recepción Telegram FIRING/RESOLVED de las
nuevas cadenas no realizadas. No declararlas aceptadas bajo el contrato F4 ni cerrar
la Fase 7 global. Siguiente paso: propietario reserva DHCP, crea su administrador,
prueba voz/móvil y valora el margen de RAM; coordinar después la aceptación de
alertas de 630/631. [Informe vigente](../IA-CHAT-EXECUTION-2026-11-13.md).

> Complementos abiertos; F5 aceptada, Fleet F6 desplegado y seguridad F7 pendiente; [cierre](../EXPORTERS-D041-CLOSURE.md).

# Fase 4. Exporters & Monitoring Coverage

Estado: **DONE — coberturaexporters17/17; complementosheredados abiertos**. Actualizado: 2026-11-09 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo

Conseguir métricas correctas y cobertura explícita de los 17 servicios, con fuentes y ámbitos identificables.

## Alcance y dependencias

Node Exporter/LXCFS, cAdvisor/Docker/cgroup del LXC, Journal, métricas de Grafana y separación de disponibilidad. Sin cambios de aplicaciones o recursos Proxmox no revisados.

Dependencias: F3 aceptada; inventario real y fuentes de gestión; aprobación posterior de piloto/rollout. Las alertas/dashboards de F5/F6 dependen de esta calidad.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F4-01 | Auditar los 17 CT, targets y fuentes reales | DONE | Snapshot de solo lectura; límites LXCFS vs /proc Docker; API Docker 400 para v1.41 |
| F4-02 | Corregir fuente CPU/RAM de Node Exporter | DONE | 17 fuentesLXC/cgroup/LXCFS verificadasD041 |
| F4-03 | Recuperar métricas individuales cAdvisor | DONE | 17 cAdvisor0.60.6,métricasDockerindividuales verificadas |
| F4-04 | Completar Journal: Node, cAdvisor, web/API/readiness DB | DONE | ExportersD041; sondasweb/API D054 y pg_isready periódicoD057. No certifica integridad SQL ni discovery automático |
| F4-05 | Recoger métricas del propio Grafana | TODO | /metrics conocido; job ausente en lecturaD059. Sonda HTTP GrafanaD054 es otro contrato |
| F4-06 | Separar host PVE, LXC, Docker y aplicación | IN PROGRESS | MétricasLXC/Docker desplegadas; PVEestado/uptimeCT D056 y saludF6. Observabilidad completa del host y contratos restantes pendientes |
| F4-07 | Aprobar y ejecutar piloto CT 624; validar estabilidad/idempotencia | DONE | Aceptado técnicamente por el propietario D-017; ocho criterios cumplidos, rollback y segunda aplicación sin cambios; ver PILOT-624 |
| F4-08 | Corregir healthchecks heredados con contratos verificados | DONE | D051: Budibase/API CRM/Focalboard corregidos y validados, sin cambiar imagen/datos; UAT aparte |
| F4-09 | Cerrar aceptación 17/17 con evidencia de producción | DONE | 17/17aceptados porperfilesD040/D041;evidenciafinalproducción |
| F4-10 | Compatibilidad CPU e integración incremental | DONE | ContratosCPU e integración17/17;sin fallbackfísico |
| F4-11 | Preparar y ejecutar lote Journal API/DB CT 626→625 | DONE | PASS técnico ambos; 600,960/601,019 s, backups previos/posteriores, rollback y segunda aplicación reales. Accepted por propietario D-020; integración CPU P0 verificada; ver JOURNAL-EXECUTION |
| F4-11A | Journal API CT 626: exporters, backup/rollback, estabilidad e idempotencia | DONE | Accepted por propietario D-020; integración CPU P0 verificada |
| F4-11B | Journal DB CT 625: exporters, backup/rollback, estabilidad e idempotencia | DONE | Accepted por propietario D-020; integración CPU P0 verificada |
| F4-12 | Preparar rollout progresivo de los 14 LXC restantes | DONE | Rollout17/17completado;noCTpendiente |
| F4-13 | Integración y aceptación global 17/17 | DONE | Integraciónexporters/targets/recording17/17;alertasfor/global complementos separados |
| F4-14 | R1 CT613 con integración y rollback coordinado | DONE | PASS técnico: 21/600,967s, backup V2 reparado/verificado; entrega confirmada |

## Implementación, validación, despliegue y aceptación

Diecisiete CT aceptados técnicamente; D041 cerrado sin continuación. La matriz distingue PASS, en curso y pendientes. La cobertura17/17 estácerrada; loscomplementosheredados restantes conservansuestado explícito.

## Riesgos

Una imagen moderna no demuestra compatibilidad nested LXC. cgroup:host se refiere al LXC, no debe exponer otros CT. Socket Docker sigue siendo sensible incluso montado ro. Instalar targets Journal antes del exporter genera alertas falsas. Nuevas etiquetas cambian fingerprints. Cambiar procfs no convierte todas las métricas de kernel compartido en recursos exclusivos del CT.

## Entregables

Candidatos Compose, imágenes fijadas, catálogos generados, pruebas, informe técnico y matriz de cobertura; después evidencia del piloto y rollback.

## Criterios de aceptación

1. **17/17 LXC obligatorios, incluidos CRM y EVA:** Node y cAdvisor corregidos y recogidos sin duplicados durante laventanaaprobada D040:180s/7convencionales-Grafana-Blackbox,300s/11CRM-EVA,600s/21Prometheus,a30s. Sin esta cobertura y validación global F4 no es DONE.
2. Capacidad CPU/RAM y filesystem coinciden con Proxmox/LXCFS. El consumo CPU debe coincidir con cgroup real: se comprobó que los tiempos procfs filtrados seguían siendo físicos. Verificar uso/tasas y frescura lxc_cpu_*, no solo número de CPU; no usar 4 CPU/15,5 GiB para todos.
3. Para cada contenedor Docker activo esperado: CPU, RAM e identidad disponibles y contrastadas con Docker/cgroup. Excluir deliberadamente originales de recuperación detenidos; una serie root no cumple.
4. Grafana job up=1 y build/process metrics; tres Journal con exporters y sondas cuyo contrato esté identificado. TCP PostgreSQL no se acepta como integridad SQL.
5. Diferenciar caída del collector, del LXC, del contenedor y del endpoint. Fuente del host PVE documentada; si falta, conservar tarea abierta, no inventarla a partir de LXC.
6. Sin nuevos OOM/PSI ni regresiones CRM/EVA; imágenes/datos de aplicaciones intactos, rollback verificable y segunda aplicación sin recreaciones.
7. Cada CT exige cadena Exporter→Prometheus→Reglas→AM→Telegram verificada, no solo exporters; no avanzar al siguiente sin integración. Revisión/aceptación del propietario tras piloto/rollout. Cobertura/integración global cerradaD041; no atribuir recepción humana nueva a cada CT. Cadena globalF5 recibida y aceptadaD050. Complementos4/5 permanecen separados del cierreexporters.

## Seguimiento vigente D059

17/17 Node/cAdvisor UP,18 Blackbox UP; Journal funcional periódico y saludFleet
resueltosD054/D057, healthchecks D051. JobGrafana sigue ausente y hostPVE completo
no aceptado. [Evidencia](../evidence/2026-11-09-d059-documentation-audit.json).

## Evidencias y referencias

- [PILOT-624](../PILOT-624.md) y [resumen numérico](../evidence/2026-11-02-pilot624-summary.json).
- [PHASE4-AUDIT](../PHASE4-AUDIT.md), [matriz](COVERAGE-MATRIX.md).
- [Auditoría runtime](../evidence/2026-11-02-runtime-audit.json), [Prometheus](../evidence/2026-11-02-monitoring-audit.json), [comprobaciones adicionales](../evidence/2026-11-02-supplementary-audit.json).
- [Node candidato](../../../services/common/node-exporter/docker-compose.phase4.yml), [cAdvisor candidato](../../../services/common/cadvisor/docker-compose.phase4.yml), [imágenes](../../../services/common/phase4-images.json).
- [Generador](../../../scripts/gen-prom-targets.py), [contratos Journal](../../../services/infra-prom/config/journal-probes.yml).
- [Validador de evidencia](../../../scripts/validate-phase4-evidence.py), [tests](../../../tests/monitoring/test_phase4_coverage.py).

- [Contrato CPU](../CPU-CONTRACT.md), [lote preparado](../JOURNAL-625-626.md), [validación local](../evidence/2026-11-02-journal-batch-validation.json).

- [Rollout progresivo](../PROGRESSIVE-ROLLOUT.md), [orden generado](../evidence/2026-11-02-progressive-rollout-plan.json).

- [Resultados Journal](../JOURNAL-EXECUTION.md) y [runtime final](../evidence/2026-11-02-journal-final-runtime.json).

- [Integración incremental](../INCREMENTAL-INTEGRATION.md), [R1 preparado](../R1-613.md), [estados IaC](../../../services/common/exporter-migration.yml).


## Historial de ejecución — sustituido por D041 y seguimientos posteriores

Los estados y permisos siguientes corresponden a sus fechas; no son el estado
vigente ni autorizan reejecuciones. Consultar [CURRENT-STATUS](../CURRENT-STATUS.md).

### Seguimiento 2026-11-03 08:38 CET — recuperación CT 619 pendiente

Consulta SSH estricta de solo lectura: exporters originales, n8n y PostgreSQL
activos, sin OOMKilled y con cero reinicios Docker. n8n responde HTTP 200 en la
IP documentada del LXC; PostgreSQL acepta conexiones. La prueba inicial por loopback
fue rechazada; no se interpreta como caída de la aplicación.
Dos pruebas locales de la propuesta pasan. Se propone elevar exclusivamente el
límite de cAdvisor CT619 de 128 a 256 MiB, conservando recursos LXC y aplicaciones,
con preflight, backups/rollback, idempotencia y observación >=600s/21 muestras.
**BLOCKED:** falta aprobación expresa de ese cambio de recursos según AGENTS.md;
«continua» permite retomar diagnóstico, pero no especifica aprobar esta ampliación.
No se desplegó ni reinició nada; 6/17 sigue siendo el último registro validado,
no una revalidación global actual. D-025 conserva su alcance; CT623 y siguientes
detenidos. Siguiente paso: aprobación del ajuste acotado y revalidación de gates.
[Evidencia de seguimiento](../evidence/2026-11-03-619-resume-readonly.json).


Seguimiento 2026-11-03T08:41:46.043145+01:00: **D-028 / recuperación619 IN PROGRESS**.
Propietario aprueba P-012 (cAdvisor256MiB); revalidación previa y ejecución acotada
con rollback/600s pendientes. No equivale a despliegue ni aceptación. D-025 vigente.


### Estado vigente D-028 — 2026-11-03 09:02 CET

**Fase 4 IN PROGRESS; CT619 BLOCKED_ROLLED_BACK; cobertura validada6/17.**
P-012 aprobada y ejecutada localmente/en producción con candidato256MiB; no aceptada
como recuperación completa. Fuente puntual, integración, ensayo de rollback y segunda
aplicación pasaron; observación FAIL:27 muestras/780,579s,10 fallidas, primera a180,125s
y extensión600,454s conservando baseline. Diagnóstico independiente:14 discrepancias
CPU cAdvisor/Docker en36 muestras; pico cgroup cAdvisor24,2MiB, sin OOM/reinicios
ni eventos max en esas muestras. Hipótesis de desfase de caché pendiente de demostrar.

Regla temporal retirada y checkpoint coordinado restaurado; originales activos,
candidatos128/256 y Node conservados detenidos. n8n/PostgreSQL disponibles. Seis
cadenas previas revalidadas por API tras rollback;17 Node/17 cAdvisor/11Blackbox.
CT623 y posteriores sin iniciar; R6 excluido. No hubo commits/push. La prueba
Telegram de619 no se declara aceptada por fallar la ventana; ninguna recepción
humana nueva atribuida. D-025/D-028 conservan alcance, sin aprobar otros recursos.

Siguiente paso: contrastar CPU cAdvisor/Docker con timestamps equivalentes y preparar
una validación reproducible, manteniendo tolerancias y HALT hasta resolver el gate.
No avanzar ni repetir despliegue por el solo hecho de tener256MiB. Los registros
anteriores de aprobación pendiente y bloqueo SSH son históricos y quedan sustituidos.
[Evidencia D-028](../evidence/2026-11-03-619-d028-recovery.json).


D-029: investigación de causa CPU619 **IN PROGRESS**, sin nuevo despliegue.
El HALT permanece hasta diagnóstico y regresiones verificables. Alcance autorizado
registrado en DECISIONS; cronometraje en evidence/2026-11-03-619-cpu-investigation-time.json.


D-029: causa identificada en timestamps del validador; corrección IaC y19
regresiones locales PASS. Reintento exclusivo619 **IN PROGRESS**, pendiente de
backups/gates/observación600s; no se considera aún integrado.


D-029: observación de619 corregida en curso, sin PASS provisional. La carrera
del lector está corregida y probada; candidato e identidades sin cambios desde
el checkpoint idempotente. Causa y fórmulas en ../CT619-CPU-RCA.md.


Estado D-029 2026-11-03T09:38:57.825130+01:00: **CT619 PASS técnico, cobertura7/17**.
21 muestras/600,442s; CPU de cuatro contenedores alineada y validada, backups
externos/rollback/idempotencia y cadena TelegramAPI +2/0errores. Sin recepción
humana atribuida. Vigilancia posterior900s activa; continuación automática623
y siguientes D025 iniciada, R6 excluido. Causa raíz corregida; no aceptación
globalF4. Ver CT619-CPU-RCA y evidencia2026-11-02-rollout-619.json.


D-029 vigente:619 PASS estable900s;623 vetado por frescura de CPU, observación
extendida previa a rollback;7/17 aceptados técnicamente. CT617 y posteriores no
iniciados. No aceptación globalF4 ni nuevas autorizaciones de recursos/apps.


Resultado vigente D-029:619 PASS técnico y vigilancia posterior PASS;7/17.
623 BLOCKED_ROLLED_BACK por timestamp CPU>90s, tras ventana extendida600,511s;
originales/apps/checkpoint7 verificados, candidatos retenidos. CT617 y posteriores
no iniciados, no se relajan gates. Siguiente paso: determinar cadencia/frescura623
y registrar fallo íntegro antes de otro intento.
[Evidencia](../evidence/2026-11-03-623-halt-rollback.json),
[RCA619](../CT619-CPU-RCA.md), [tiempo](../evidence/2026-11-03-619-cpu-investigation-time.json).


## Cierre controlado D-030 (vigente)

Fase IN PROGRESS; sesión cerrada, rollout suspendido.7 DONE técnicos,1 BLOCKED/
ROLLED BACK (623),9 PENDING.623 original verificado; cadencia fija solo preparada,
no desplegada por alcance Prom610 excluido. No continuar R4/R5/R7 ni CRM/EVA.
Auditoría:27 backups,49 inputs exporters y24 Prom coinciden;17/17/11 targetsup,
siete cadenas aceptadas. No se repiten idempotencia/restauración en auditoría de
lectura ni se declara aceptación global. Siguiente sesión:623 con nuevo alcance.
[Handoff](../PHASE4-HANDOFF.md), [cierre](../evidence/2026-11-03-phase4-close-audit.json).


Reanudación 2026-11-05 D-031:623 IN PROGRESS, revalidación de lectura antes de
cualquier cambio; Prom610 autorizado solo configuración623, no exporters.
Siete DONE históricos no se repiten. Integración R4/R5 pendiente de aclaración
por límite610 del adjunto. Sin nuevo despliegue ni aceptación todavía.


D-031 2026-11-05T21:27:13.239137+01:00: **CT623 DONE técnico,8/17**.21 muestras/600,804s;
backup fresco exporters y checkpointProm610, promtool config/reglas/discovery
17/17/11, rollback/idempotencia y TelegramAPI+2/0errores PASS. Vigilancia900s
activa. Iniciada continuación617, sin modificar exporters610 ni CT excluidos.


## Resultado vigente D-031 — 2026-11-05

8 DONE técnicos;617 BLOCKED_ROLLED_BACK por watcherRAM,615 BLOCKED_NO_CHANGES
por aplicación503,7 PENDING.623 completado con cadencia30s y watcher PASS.
Inicial617 PASS no equivale a aceptación final: watcher31/901,797s FAIL,
rollback de originales/apps/checkpoint8 verificado.614 yR5 sin iniciar.
35 backups y56 inputs exporters/24 Prom coinciden. No scripts de avance activos,
política BLOCKED. Próximo617, diagnósticoRAM temporal, luego salud615 fuera alcance.
[Handoff](../PHASE4-HANDOFF.md), [auditoría](../evidence/2026-11-05-final-audit.json).


### D-032 — diagnóstico RAM617 y contrato común

2026-11-06 10:35 CET. F4 IN PROGRESS,8 DONE/2 BLOCKED/7 PENDING; producción sin
cambios. Validador RAM temporal preparado localmente y44 regresiones PASS, control
de lectura623 PASS; causa única histórica no demostrada. Política BLOCKED; no
615 ni aplicar sin aprobación posterior. [Informe](../CT617-RAM-RCA.md).


### D-033 — reentrada617 detenida y revertida

2026-11-06 11:15 CET.8DONE/2BLOCKED/7PENDING. Guardaheld impidió primer apply;
originales/apps/checkpoint8 restaurados. Ventanas600/900 no ejecutadas; noDONE.
Corrección de nombresheld local y27 pruebasPASS; no redeploy ni615. PolíticaBLOCKED.
[Cierre](../CT617-D033-EXECUTION.md).


### D-034 — SKIP AND CONTINUE y veto de seguridad614

2026-11-06 11:35 CET.8DONE/3BLOCKED/6PENDING. Política/driver preparados y
probados;614app503 enpreflight, originalsin cambios; falta condiciónappfuncionando
para saltar. HALT GLOBAL;61211noiniciado.36 pruebasPASS, sin umbrales modificados.
[Procedimiento y cierre](../SKIP-AND-CONTINUE.md).


### D-035 — baseline porcasos y61211 revertido

2026-11-06 12:24 CET.614CaseBpreexistente noimpide61211independiente; sóloseintervino61211.
Inicial13/360,225sPASS,watch31/903.637sFAIL por lectorRAMcomúnRFC3339Nano,
HALT GLOBAL/rollbackverificado.8DONE/4BLOCKED/5PENDING.52pruebasPASS; fixparser
solo local,no reintento niR6/R7. [Cierre](../CT61211-D035-EXECUTION.md).


### D-036 — framework CPU/RAM estabilizado localmente

2026-11-06 13:29 CET.80regresionesPASS,compatibilidad de lectura8/8(31contenedores),
56inputs/identidades/recursos sin cambios. Fuentecomún de parser/captura/scope
yvalidación, revisiónhash/auditfresh61211 preparados;sin despliegue ni aceptación
nueva.8DONE/4BLOCKED/5PENDING,políticaBLOCKED. [Informe](../VALIDATION-FRAMEWORK.md).

## D088 — incidencia cAdvisor623/618 y CRM

13 de noviembre de 2026 (Europe/Madrid), DONE técnico. Recuperación autorizada
por el propietario, acotada a623/618: límite cAdvisor128→384MiB en caliente,
CPU y RAM PVE intactas; CRMAPI618 arrancado sin recreación y restartalways.
Backups/restauración aislada e idempotenciaPASS. Dashboarddesplegado indica
HEALTHY/0alertas para ambos. Observación600s/21 PASS: cero timeouts/alertas, sin OOM ni reinicios nuevos.
Siguiente: vigilancia existente; recepción humana Telegram no verificada.
[Informe y evidencias](../PHASES-D088-CADVISOR-CRM-RECOVERY.md).
No modificar aceptación previa ni dar por aceptados pendientes heredados.

## Auditoría de capacidad y respaldos — 13 de noviembre de 2026

Auditoría DONE, ejecución TODO: cAdvisor619/61211 con presión activa y620menor;
propuesta selectiva sin rollout. Clones9618/9622 candidatos a retirada conservando
fuentes618/622; checksum actual pendiente. Raíz90%, traslado delbackupVM100 aHDD
solo propuesto. Hardwareinventariado sinbenchmark. Sin cambios productivos ni
commit/push; no se aceptan pendientesglobales de la fase.
[Informe y siguiente paso](../CAPACITY-BACKUPS-AI-AUDIT-2026-11-13.md).

## Capacidad y limpieza autorizadas — 13 de noviembre de 2026

DONE técnico del alcance aprobado:619/61211a384MiB y620a256MiB,600s/21 porCT,
idempotencia/backupsexternosPASS; sin OOM/reinicios ni cambios de aplicaciones.
Clones9618/9622 retirados conservando fuentesverificadas/configs. BackupVM100
trasladado alHDD conSHA256/zstd/VMAverifyPASS antes de eliminar origen.
Raíz35%/41,60GiB libres; pool178,64GiB libres.25configsPVEajenas idénticas,
18cAdvisorUP/ceroalertas, saludHTTP200. Sin commit/push ni cierre de pendientes
globales. Siguiente: vigilancia existente, sin ampliación automática de alcance.
[Resultado y límites](../CAPACITY-APPROVED-EXECUTION-2026-11-13.md).


## IA-CHAT — ampliación de alcance aprobada: patrón del repositorio y observabilidad

13nov2026 Europe/Madrid. El propietario solicita integración reproducible completa de
630/631 en Terraform/inventario YAML, docs/inventory, monitorización y Grafana como
el resto del pool; autoriza los cambios necesarios para ello. Aprobación limitada
a los dos CT nuevos y modificaciones aditivas de observabilidad que los incorporen,
con backup/rollback, validación e idempotencia. No rollout global de exporters,
no cambios de aplicaciones/recursos de otros CT y **627 excluido por completo**.
Sin commit/push ni aumento automático de RAM631. Mantener DHCP y reservas pendientes,
unprivileged, volúmenes/modelos y contratos CPU/RAM del repositorio.

Estado IN PROGRESS: la receta pct aislada anterior no basta como cierre del patrón
solicitado; preparar adopción Terraform sin recreación, SSH verificado si procede,
exporters apropiados para630sinDocker y631conDocker, integración aditiva enPrometheus/
Blackbox/Grafana e inventario. Conservar cambios previos ajenos. La validación devoz
sigue pendiente tras corregir WHISPER_MODEL persistido; no declararla aprobada.
