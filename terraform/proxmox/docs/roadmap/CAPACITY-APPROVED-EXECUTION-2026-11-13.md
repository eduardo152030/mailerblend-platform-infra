# Capacidad y limpieza — ejecución autorizada

13 de noviembre de 2026, Europe/Madrid. Fase4. Exporters & Monitoring Coverage y
Fase7. IaC Reliability, Security & Disaster Recovery. Estado: DONE técnico.
[Propuesta y diagnóstico](CAPACITY-BACKUPS-AI-AUDIT-2026-11-13.md).

## Autorización y alcance

El propietario responde «autorizo la propuesta». Autoriza ejecutar los ajustes
selectivos619→61211→620, retirada de clones9618/9622 y traslado verificado del
backup históricoVM100. No es aprobación de rollout global ni de recursosPVE,
otrosCT, reglas, discovery, aplicaciones, inferencias, commits ni push.
Aprobación registrada antes de aplicar en ROADMAP/CURRENT-STATUS/DECISIONS.

## Ejecución y seguridad

[Receta exporters](../../scripts/capacity-approved-20261113/exporter.py),
[driver secuencial](../../scripts/capacity-approved-20261113/rollout.py) y
[receta almacenamiento](../../scripts/capacity-approved-20261113/storage.py).
SSH estricto con known_hosts del propietario y BatchMode. Scripts porstdin,
sin desplegar ni ejecutar scripts históricos de rollout/eliminación masiva.
Almacenamiento independiente se verifica en paralelo con baja prioridadI/O yCPU.

619: memoria256→384MiB, techo combinado RAM+swap512MiB conservado;61211:
128→384MiB/techo384;620:128→256MiB/techo256. No hay ampliación deRAMLXC.
CPU y contenedores existentes conservados. Overlays Git exclusivos porCT.

Antes de aplicar cadaCT: backup de sus tres inputs activos en directorio privado,
copia fueraPVE, extracción aislada y hashes contra manifest. Baseline de todos
los contenedores activos. Composeconfig conbindIP real; dockerupdate en caliente.
Segunda aplicación debe conservar ID/inicio/restarts/imagen/CPU/mounts/apps.
Observación600s/21 porCT con Prometheus18cAdvisorUP, CPU LXC y métricasDocker
CPU/RAM, salud de contenedores, ausencia de alertas del objetivo, OOMdelta0 y
presión final. Excepción produceHALT yrollback de eseCT, sin avanzar al siguiente.
No se modifican for, timeouts ni silences para aparentar estabilidad.

Rollbackexporter: verificar identidad contra baseline, restaurar inputs según
manifest y Composeconfig, dockerupdate a memoria y techo combinado anteriores.
No restaurar datos ni reiniciar aplicaciones. No se prueba rollback productivo
si provocaría regresar al cuello de memoria; recuperabilidad de inputs sí probada.

Almacenamiento: /mnt/storage verificado como filesystem montado distinto deraíz;
configuraciones9618/9622 exportadas en HDD con hashes, apagados/aislados/sinmounts
adicionales/snapshots/locks, volúmenesexactos y sin referencias desde otrosCT.
Fuentes618/622 se conservan: SHA256 contra recibos históricos y lectura completa
zstd/tar con configuraciónPVE presente antes dedestruir clones. Revalida los
archivos utilizados en restauraciones históricasF3; no es nuevo ensayoDRfuncional.

Backup100: copia nueva sin sobrescrituras en HDD, hash de origen durantecopia y
SHA256 completo de destino, fsync, validación completa zstd→VMAverify. Solo si
ambos procesosPASS se publica destino y se retira el archivo origen exacto.
Fallo conserva origen/copiatemporal; logs privados fueraGit. No borrar backups
fuente618/622, Voicebox, ISOs, volúmenes ajenos ni imágenes derollback.

## Resultados verificados

| CT | Memoria cAdvisor | Techo RAM+swap | Observación | Resultado |
|---|---:|---:|---:|---|
|619|384 MiB|512 MiB|601,27s /21 muestras|PASS, PSI final0, idempotenciaPASS|
|61211|384 MiB|384 MiB|601,10s /21 muestras|PASS, PSI final0, idempotenciaPASS|
|620|256 MiB|256 MiB|601,42s /21 muestras|PASS, PSI final0, idempotenciaPASS|

Los tres mantienen ID/imagen/inicio/mounts/CPU, cero OOM y reinicios nuevos;
contenedores de aplicaciones conservados.18 targets cAdvisor UP durante cada
muestra; CPU LXC y métricasDocker CPU/RAM presentes. Máximos de scrape durante
observación0,372/0,633/0,016s respectivamente. No se presentaron anomalías niHALT;
no se ejecutó rollback productivo. Backups externos de configuración extraídos y
verificados antes de cada aplicación. Segunda aplicación porCT sin cambios.

Clones9618/9622 retirados, configuraciones privadas enHDD y fueraPVE, extracción
externa comprobada. SHA256 de fuentes618/622 coincide con recibos y lectura
completa zstd/tarPASS:200150 entradasCRM y registroEVA en recibo. Se conservan
ambos respaldos fuente, bundleCRM y copia cifradaEVA. No nuevo ensayoDR funcional.
Se revalidaron identidades/aislamiento/volúmenes sin referencias ajenas antes de
cada destroy.25 configuracionesPVE restantes idénticas albaseline.

BackupVM10037149277192bytes trasladado a
`storage:backup/vzdump-qemu-100-2025_03_23-23_03_29.vma.zst`.
SHA256origen/destino `b0ded7e248a7fc0e3d957155554355762d390e7c2a3fa64ce0b2c4795cd1b1f2`;
ambos procesos zstd yVMAverify terminaron0 antes de retirar origen. Copia final
registrada porProxmox, permisos0600 y sidecarSHA256 conservado. No se ha arrancado
VM100 ni restaurado su disco: validación de integridadVMA, no aceptación funcional.

| Almacenamiento | Antes | Después |
|---|---:|---:|
|RaízSSD|90%,7,00GiB libres|35%,41,60GiB libres|
|ThinpoolSSD|69,06% usado,≈123,79GiB libres|≈55,35%,178,64GiB libres|
|HDD|≈1311,08GiB libres|1276,49GiB libres|

Los clones liberaron≈54,9GiB físicos delpool; variación neta depende también de
escrituras de otrosCT durante la intervención. La raíz recuperó≈34,6GiB por
trasladoVM100. No se confunden90GiB virtuales con espacio físico.

Segunda revisión de almacenamiento de sololecturaPASS: clones/configs/volúmenes
ausentes, origenVM100 ausente y destino/tamaño/sidecar correctos, fuentes618/622
conservadas. No se repiten destroy/copy/unlink ni rehash de35GiB sin nueva causa.
No se sobrescribieron respaldos ni se borraron otros originales/ISOs/rollback.

Salud final: n8n, NocoDB, CRM, EVA, Focalboard, Prometheus yAlertmanager HTTP200;
PostgreSQL619/61211 ready, Redis620PONG. CeroalertasFIRING al cierre. No se envió
pruebaTelegram ni se atribuye recepciónhumana nueva a esta intervención.

## Evidencias y cierre

- [Resumen final](evidence/2026-11-13-capacity-execution-summary.json).
- Exporters [619](evidence/2026-11-13-capacity-execute-619.json),
  [61211](evidence/2026-11-13-capacity-execute-61211.json),
  [620](evidence/2026-11-13-capacity-execute-620.json).
- [Recibo almacenamiento](evidence/2026-11-13-capacity-storage-execution.json),
  [capacidad final](evidence/2026-11-13-capacity-storage-final.json),
  [segunda revisión](evidence/2026-11-13-capacity-storage-second-review.json).
- ConfigsPVE [antes](evidence/2026-11-13-capacity-execution-pve-before.json) y
  [después](evidence/2026-11-13-capacity-execution-pve-after.json).
- [SaludHTTP](evidence/2026-11-13-capacity-execution-health.json).

Recibos sanitizados enGit; configuraciones y logVMA privados fueraGit.
CompilaciónPython, enlaceslocales, JSON ygit diff --check PASS; revisión deldiff
propio sin secretos. Cambios ajenos conservados. Sin commit/push.

Intervención DONE técnica; las fases4/7 conservan sus pendientes globales.
Siguiente: vigilancia existentePrometheus/Alertmanager; no ampliar a otrosCT ni
limpiar otras copias sin nuevo alcance. Los respaldos618/622 son históricos del
2nov y no pasan a ser backups recientes por esta verificación. La eliminación de
clones se recupera mediante restauración y aislamientoF3, no medianteundo.
