# Fase 7.4 — D079: recuperación selectiva y admisión predictiva

Seguimiento: **12 noviembre 2026, Europe/Madrid**. Evidencias UTC.
**Corrección desplegada y validada; ensayo continuo BLOCKED por preflight.**
No se cargó Qwen ni se inició una generación. No hay nuevo WAV, tokens, EOS,
checkpoint ni ejecución de Decoder B. No se consumió un intento de inferencia.

## Resultado medido

El 12nov a07:07UTC se solicitó POSIX_FADV_DONTNEED una sola vez sobre cada uno
de los cinco blobs exactos del [manifiesto D078](../../services/infra-voicebox/proposals/d078/cache-reclaim-plan.json).
Se verificaron tamaño, inode, ausencia de FD/mappings activos, cola vacía y ausencia
de operaciones Docker incompatibles. No se borraron archivos/imágenes ni se hizo
drop_caches global. Identidad de archivos e imágenes conservada.

| Memoria CT627 | Antes, bytes | Después, bytes |
| --- | ---: | ---: |
| Total cgroup |6000422912|4867538944|
| Anónima |386854912|385949696|
| File |5260390400|4131409920|
| Kernel |353161216|350179328|
| Swap |0|0|

File y residencia de los cinco blobs bajaron exactamente **1128980480bytes,
1,051445GiB**. El total bajó1132883968bytes; su diferencia incluye variación de
otros componentes, no debe atribuirse toda al consejo POSIX. PSI local avg10=0,
sin nuevos OOM durante la reclamación.

## Preflight y parada

La admisión usa el total actual, sin descontar hipotética caché recuperable:
**CT inicial +4,5GiB de incremento previsto +0,5GiB de reserva ≤9,5GiB**.
El incremento observado en D077/D078 fue4,25–4,48GiB; se redondea hacia arriba.
La reserva es una política conservadora, no una predicción exacta del pico.

Lectura final:4866977792bytes (**4,533GiB**). Proyección10235686912bytes
(**9,533GiB**), guarda10200547328bytes. Faltan35139584bytes (**33,51MiB**)
para admitir con esta reserva. Las tres lecturas estabilizadas previas también
rechazaban la admisión. Por instrucción del propietario **se detiene sin POST
/generate**, sin cambiar constantes, sin más reclamaciones ni reintentos.
Host disponible en la comprobación:22500844kB (~21,46GiB); PSI host full avg10
12,57%, distinto del PSI local0. La RAM libre del host no sustituye el límite CT.

## Implementación desplegada

- Nueva imagen `local/voicebox:qwen-isolated-d079`, ID
  `09774c5b7c535185c901557ddb6c69a4f8bb38ceff2c6998e19bab403b8e94ea`.
- [guards.py](../../services/infra-voicebox/pilot-d077/guards.py) y
  [supervise.py](../../services/infra-voicebox/pilot-d077/supervise.py): gate antes
  de crear/cargar el worker Talker. Guardas de parada anteriores intactas.
- [Adaptador](../../services/infra-voicebox/production-d079/isolated_backend.py):
  diferencia ausencia de checkpoint de carpeta existente no validada. Nunca inicia
  B sin validación completa ni repite A automáticamente. Los dos jobs fallidos
  permanecen intactos. El usuario debe solicitar un intento nuevo explícito tras
  corregir la causa; no se habilita reintento automático del ID anterior.
- [Reclamación reproducible](../../services/infra-voicebox/production-d079/reclaim.py),
  stage/deploy/backup en el mismo directorio. Compose e image-lock actualizados.
- Worker ML, referencia, FP32, A→checkpoint→B300/contexto25 sin cambios.
  Preparación reutilizable de referencia NO implementada.

36 pruebas sin modelos PASS; smoke de fábrica con UID999 PASS. Mensajes probados
sobre los dos IDs reales sin inferencia y sin modificar sus evidencias. Segunda
aplicación: mismo ID/StartedAt, sin recreación. Voicebox healthy, supervisor activo.
Se reinició exclusivamente Voicebox y su supervisor dedicado durante el despliegue.

## Preservación y rollback

Backup previo de datos, originales, jobs y configuración en CT, con copia privada
fuera de CT627; SHA y restauración SQLite verificados,83archivos de manifiesto.
Imágenes anteriores conservadas. Nueva imagen reproducible desde fuentes y base;
no se exportó otro archivo de imagen para evitar recalentar los blobs. Archivo de
rollback D077 verificado previamente, no sustituido por una promesa de backup nuevo.

78archivos de datos/originales/jobs cotejados: única variación `agent-heartbeat.json`,
esperable por el supervisor activo. Archivos protegidos, filas de perfiles, muestras
 e historial iguales al backup. Los dos jobs fallidos siguen sin checkpoint;
no son recuperables mediante B. Recursos/configuraciones PVE no modificados.
Consultar evidencia final para contadores de eventos: un incremento high no es OOM.
No se generó audio adicional para probar Kokoro/Piper; permanecen instalados y
preservados. No se afirma una validación end-to-end de monitorización central.

## Evidencias y siguiente paso

[Reclamación](evidence/2026-11-12-d079-cache-reclaim.json),
[preflight](evidence/2026-11-12-d079-preflight-final.json),
[despliegue](evidence/2026-11-12-d079-deploy.json),
[idempotencia](evidence/2026-11-12-d079-deploy-idempotent.json),
[mensajes](evidence/2026-11-12-d079-message-validation.json),
[backup](evidence/2026-11-12-d079-backup-verified.json),
[estado final](evidence/2026-11-12-d079-final.json).

Fase7.4 IN PROGRESS. Corrección DONE técnica; narración continua BLOCKED, sin UAT.
Recomendar una siguiente intervención acotada para identificar y reducir memoria
inicial adicional, sin ampliar recursos ni relajar la reserva a posteriori. La
preparación reutilizable de referencia sigue como optimización estructural separada.
No ejecutar nuevos ensayos con esta autorización tras esta parada. Sin commit/push.
