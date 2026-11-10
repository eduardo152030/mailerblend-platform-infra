# Auditoría del trabajo acumulado

> Nota de vigencia D059,2026-11-09: este archivo conserva antecedentes fechados.
> Estado actual en [CURRENT-STATUS](CURRENT-STATUS.md). Rolloutexporters17/17
> cerradoD041;503de614/615resueltosD044/D048, healthchecksD051corregidos,
> F5aceptadaD050 yFleetF6desplegadoD052–D058. No reutilizar permisos ni siguientes
> pasos históricos como autorizaciónactual. Seguridad/CI/DRsiguenpendientesF7.

Fecha: 2026-11-02, Europe/Madrid. Se revisaron README, Makefile, inventario, scripts,
Compose, reglas, catálogos, provisioning y los runbooks anteriores. No había AGENTS.md
aplicable en esta raíz ni sus ancestros inspeccionados; se añade para mantener las
reglas de continuidad solicitadas. Convención observada: documentación Markdown en
español, inventario YAML, un directorio por servicio y scripts centrales.

## Git y procedencia

Base Git observada: `ceb2e79` (`updates`). El árbol ya contenía cambios extensos antes
de esta intervención; no corresponde al último commit por sí solo. No se ha ejecutado
reset, stash, limpieza de archivos ajenos, publicación ni commit indiscriminado.
Los estados Terraform no se han impreso ni modificado en esta reorganización.

| Grupo de cambios previos | Implementación encontrada | Estado real / límite de prueba |
|---|---|---|
| infra-prom, apply-monitoring, secretos por archivo y validadores | Archivos locales modificados/nuevos, runbooks y tests | Despliegues anteriores documentados y APIs actuales operativas; los candidatos F4 se distinguen del runtime |
| Telegram y Blackbox | Receptor, plantillas, catálogo y reglas; cuatro catálogos antiguos retirados localmente | Entrega aceptada por propietario; 11 sondas base reales, dos Nucleotecnológico; fallo de aplicación aún activo |
| CRM | RAM inventario 6144, override de etiquetas, overlay/helper conservador, backups y checks | Recuperación EJECUTADA y aceptada con dispensa UAT; no una propuesta pendiente |
| EVA | Logging, mantenimiento informativo, journal y helpers de recuperación | Limpieza/rollout EJECUTADOS, ~34% libre, originales conservados; digest y healthcheck no corregidos |
| Terraform main/variables/defaults/state | Mezcla de cambios anteriores y estado actualizado por la recuperación | No aplicar globalmente; hay deriva y recursos nuevos. Estado rastreado es riesgo de seguridad, no evidencia de aprobación |
| Journal y Gestoría | Inventarios y directorios nuevos sin commit al iniciar | CT/apps existen en runtime; Journal web/API responden. No se ha demostrado por hash que todo el código local coincida con lo desplegado |
| sync_service.py EVA y otros archivos ajenos | Cambios previos presentes | No se han desplegado ni atribuido a esta reorganización; procedencia/despliegue específico no establecidos |
| Herramientas | promtool/amtool oficiales en rutas /tmp | Usadas para validación anterior/actual; instalación reproducible pendiente F7 |

`git ls-files` confirma que `terraform.tfstate`, su backup, `terraform.tfvars` y
`services/infra-prom/perm.env` son heredados rastreados. No se publica su contenido.
El `.env` nuevo de monitoring está ignorado y no rastreado; eso no corrige el riesgo
histórico. La política de “secretos fuera de Git” es una decisión aprobada con deuda
abierta, no un cumplimiento global certificado.

## Distinción de evidencias

- **Local:** archivos y tests demuestran preparación, no ejecución remota.
- **Desplegado:** PHASE2-EXECUTION y APIs/runtime contrastados acreditan recuperación
  y disponibilidad; su aceptación ahora está registrada en D-011.
- **Actualización posterior:** templates `docker-compose.phase4.yml` y overlays del
  piloto aplicados solo en CT 624; ver PILOT-624. Targets globales 17+17, job Grafana
  y sondas Journal siguen sin desplegar. Los defaults heredados no se sustituyen automáticamente.
- **Aceptado:** F3 por decisión expresa con dispensa, sin inventar UAT. Los tres
  healthchecks, digest y Nucleotecnológico no heredan ese estado DONE.

La entrega actual sigue siendo un conjunto de cambios de trabajo, pendiente de commits
curados. No hay publicación. Antes de versionar el conjunto previo hay que revisar
archivos nuevos y excluir secretos/estado; no ejecutar `git add .` sin esa revisión.
El roadmap y AGENTS se añaden de forma acotada al índice Git, sin crear un commit.
No se añade indiscriminadamente el trabajo previo ni sus estados/secretos.
Los enlaces de documentación se validan contra el árbol local; no certifican que los
archivos enlazados ya existan en un checkout del último commit.

## Evidencias técnicas

- [Auditoría Prometheus](evidence/2026-11-02-monitoring-audit.json).
- [Auditoría de los 17 CT](evidence/2026-11-02-runtime-audit.json).
- [Segunda lectura sin cambios de producción](evidence/2026-11-02-runtime-final-readonly.json).
- [Comparación de estabilidad CRM/EVA](evidence/2026-11-02-stability.json).
- [HTTP, LXCFS, API Docker y módulos efectivos](evidence/2026-11-02-supplementary-audit.json).
- [Informe F4 y candidatos](PHASE4-AUDIT.md).


## Actualización del piloto CT 624

El piloto ya se ha ejecutado: [PILOT-624](PILOT-624.md). Se añaden helpers de
aplicación/rollback, muestreo/observación, overlays y collector CPU acotados a CT 624,
con sus tests y evidencia numérica. Se distinguen de los catálogos globales todavía
sin desplegar. La documentación y los archivos del piloto se añaden de forma curada
al índice, sin commit/publicación y sin incluir estados, secretos o trabajo ajeno.


## Preparación del lote Journal API/DB

Aceptación técnica CT 624 registrada D-017. F4-10/F4-11: reglas CPU, validadores,
generación local de bundles 625/626 y catálogos preparados; pruebas locales y
consultas de solo lectura acotadas a esos CT. No hubo despliegue/descarga/backup
nuevo ni recarga de Prometheus. Evidencias de recursos y render Compose sin staging
remoto; las copias/restauración/idempotencia reales quedan para el lote aprobado.
Ver JOURNAL-625-626 y CPU-CONTRACT. Los inputs desplegados de CT 624 no cambiaron.


## Ejecución Journal bajo D-019

Lote 626→625 completado y técnicamente validado: ver JOURNAL-EXECUTION. Scripts de
staging/backup/rollout/archivo/revalidación versionados, inputs por hash, dos backups
privados por CT antes/después con originales conservados; evidencia pública sin Env.
No hubo cambios en aplicaciones/DB/Proxmox ni discovery global. Se añadieron plan
R1–R7 y manifiesto determinista de 14 restantes, sin ejecutarlos. No confundir el
snapshot local anterior NOT_DEPLOYED con los nuevos informes de ejecución.


## Integración incremental y aceptación D-020/D-021

626/625 aceptados técnicamente; F4-11 DONE — Accepted. Se preparó P0 desde snapshot
privado real de CT 610 (solo lectura, no backup de rollback), conservando config y
14 targets legacy. Reglas CPU excluyentes/estado unverified, inventario esperado y
MissingTarget; candidato local 17 mixtos, sin Grafana/sondas nuevas. R1 CT 613 con
preflight de solo lectura y bundle derivado, no desplegado. Registro IaC: tres CPU
verificadas; integración/cadena vacías. No hubo mensajes/reloads/restarts/descargas.
106 tests y discovery real validan preparación, no entrega real. Evidencias y runbooks
INCREMENTAL-INTEGRATION y R1-613. Scripts/archivos del lote anterior conservados.
