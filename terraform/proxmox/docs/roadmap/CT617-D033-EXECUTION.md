# Fase 4 — CT617: cierre de reentrada D-033

2026-11-06 11:15 CET. **BLOCKED / ROLLED BACK;8/17 aceptados, sin avance615.**
Run `integration-20261106T100830Z`, iniciadoUTC2026-11-06T10:08:30.206313+00:00. Tiempo total:8.0min.

## Resultado real

Preflight fresco PASS:512MiB/1CPU, aplicaciones/proxy403/backend200,
originales y candidatos previos exactos. Backup exporters46.950.400B y checkpoint
Prom610 nuevos: legibles, hashes externo/PVE coincidentes, imágenes archivadas y
restauración de archivo probada. Config/reglas/discovery17/17/11 promtoolPASS antes
del apply. Históricos no borrados. Nuevo rootprivado/PVE preserva HALTsD031.

Primer apply detiene/renombra Node original y encuentra
`node_exporter-phase4-617-held`, candidatoD031 detenido. En el nuevo run no hay
records que acrediten su hash/ID: helper línea272 rechaza `Held candidate differs`.
No se creó candidato nuevo ni se activó contrato617 enProm. Fallo de preparación de
la reentrada, **no una nueva discrepancia RAM**. Separar proyectoCompose no aislaba
el nombreheld usado por helper. La preparación D032 omitió esa segunda identidad.

Recuperación automática: checkpointProm antes de originales, IDs/imágenes/readiness
originales verificados, apps/config sin cambios. Ocho aceptados idénticos tras
normalizar orden de mounts deDockerinspect;24 archivosProm exactos del checkpoint;
17Node/17cAdvisor/11Blackbox UP y ocho cadenas sanas. CPU/RAM loggers detenidos.
OOM/oom_kill/oom_group_kill delta0; reinicios de apps sin cambios. Stop/start de
Node original fue parte del intento/rollback, no afirmar cero reinicios operativos.

600s/21 y900s/31 **NO ejecutados**: el primer apply falló. Tampoco idempotencia real,
validación del nuevo candidato ni prueba completaTelegram. Prom/AM readyHTTP200;
no testTelegram ni envíos deliberados en esta ejecución. Counters observados en
[evidencia final](evidence/2026-11-06-d033-final-audit.json); no atribuir recepción
humana nueva. Legacy617 restaurado conserva limitaciones físicas/Docker conocidas;
UP no lo convierte en fuente aceptada.615/otros LXC no intervenidos.

## Corrección local posterior, sin reintento

`prepare-617-memory.py` usa ahora nombresheld propios
`node_exporter-phase4-617-ram-v1-held` y `cadvisor-phase4-617-ram-v1-held`, tanto en
apply como rollback. Conserva proyectosram-v1 y candidatosheldD031 sin renombrarlos.
Regresión simula originales+heldprevios, apply→rollback→reapply→segunda aplicación:
solo dos candidatos creados, mismosIDs reanudados, originales restaurados y held
antiguos intactos.14 pruebasRAM+7rollout+6reentrada=27PASS; `git diff --check` PASS.
No modifica contratoRAM, tolerancias, recursos ni pins. Esta corrección local NO
está en el helper del run fallido ni probada en producción.

## Reanudación futura

Política BLOCKED: listasapply/recovery/configProm vacías, automatic_rollout=false.
Reentrada D033 consumida al fallar; no retry automático. Antes de nueva aprobación:
revisar el aislamientoheld, volver a generar manifiesto y revisar los hashes.
Mantener nuevos y antiguos backups, originales, volúmenes, candidatos y HALTs.
La auditoríafresh617 actual sigue verificando los heldD031; no usar archivos de
más de300s ni invocar el runfallido para saltarse suHALT.

Después de una nueva autorizaciónsolo617: run/checkpoint nuevos, procedimiento
[RAM-RCA](CT617-RAM-RCA.md), backups/promtool, rollback/idempotencia reales,
600s/21 más900s/31 y cadenaProm/AM/Telegram antes deDONE. Ante cualquier fallo,
rollback seguro y detener; no615. Sin commits/push realizados.

## Evidencias

- [Ejecución](evidence/2026-11-06-d033-execution.json).
- [Recuperación y backups](evidence/2026-11-06-d033-recovery.json).
- [Originales/apps tras rollback](evidence/2026-11-06-d033-originals-after-rollback.json).
- [Auditoría final](evidence/2026-11-06-d033-final-audit.json).
- [Tiempo](evidence/2026-11-06-617-reentry-time.json).

Backups privados externos:`$HOME/.local/share/mailerblend-recovery/phase4/integration-20261106T100830Z/617/`;
PVE:`/mnt/storage/mailerblend-recovery/phase4/integration-20261106T100830Z/617/`; subdirectorio `monitoring/`
contienecheckpoint. CT617:`/opt/exporter-phase4-pilot/integration-20261106T100830Z-617/`.
No eliminar ni publicar contenido privado; hashes legibles en recuperación.
