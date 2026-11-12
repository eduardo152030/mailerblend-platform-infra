# Fase 7.4 — D080: CT627 con15GiB y ensayo continuo

Seguimiento: **12noviembre2026, Europe/Madrid**; marcas de evidencia en UTC.
**Recursos DONE técnicos; ensayo continuo completado, WAV28,56s.**
Objetivo55–60s pendiente; calidad del nuevo audio pendiente deescucha.

## Autorización y método

Propietario autoriza15360MiB RAM exclusivamente CT627; CPU3,swap2048MiB ydisco50GiB
intactos. Guarda CT14GiB, workerhard9GiB yresto de parámetros conservados. La última
instrucción autoriza continuar después de la validación con el texto completo y un
WAV final, sin segmentación ni reintentos automáticos. No arquitectura R/A/B.

Mismo procedimiento IaC existente D076: inventario YAML, precondiciónTerraform y
Notes regeneradas; plan guardado dirigido exclusivamente a627 yrevisado. El proveedor
BPG0.94 marca reinicio al actualizar memoria: se usa receta versionada de ampliación
en caliente y después refresh-only del estadoTerraform; no apply general ni deploy-all.
No se presenta el plan normal como aplicado directamente por el proveedor.

## Preflight físico

Host MemTotal33533042688bytes=31,23GiB. MemAvailable≈21,5GiB antes del cambio;
el incremento de límite5GiB no es asignación física inmediata. Incluso si627 llenase
el nuevo límite desde su uso inicial, la estimación de memoria disponible global
conserva alrededor de11GiB; no es una reserva garantizada frente a cargas futuras.
Hay swap y PSI global previos; se registran explícitamente yno se atribuyen a627.
CT627: swap0 y PSI local0 en preflight. No OOM nuevo.

## Cambio efectivo y guardas

- RAM live cgroup16106127360bytes (15GiB); swap2147483648bytes (2GiB).
- CPU3 ydisco50GiB conservados. Sin reboot ni recreación deVoicebox oCT627.
- Plan normal revisado: solo `svc["infra-voicebox"]`, memory ydescription; sin creación
  ni destrucción. Tras reconciliar estado, plan dirigido final: **cero cambios**.
- Guarda CT14GiB; workerduro9GiB/sinswap yparada8,2GiB intactos.
- Swap delta128MiB/techo1920MiB, PSIlocal5%sostenido10s, host guards, cancelación
  ypresupuesto900s conservados. FP32/Base0.6B/3hilos/300-context25 sin cambios.
- Preflight predictivo conserva incremento4,5GiB yreserva0,5GiB, ahora contra14GiB.
  Inicial4865777664bytes; proyección10234486784bytes: PASS.

Archivos: inventarioVoicebox, main.tf, NOTES ygenerados; guards/supervise enpilot-d077;
recetas [maintenance-d080](../../services/infra-voicebox/maintenance-d080/README.md).
La imagenappD079 ylos componentes ML permanecen iguales; solo se reinicia elagente
supervisor dedicado627 para adoptar sus nuevas constantes de recursos.

## Backups y verificaciones previas

Backup externoD079 verificado nuevamente porSHA; restauración SQLite ya comprobada.
Backup configuración627 ysupervisor previos enPVE `/opt/voicebox-qwen-627/backups/d080-before`.
Imágenes yvolúmenes conservados. 77archivos protegidos idénticos albackup;
filas perfil ymuestras idénticas; antiguos jobs ycheckpoints intactos.
Voicebox healthy, agentactive, node/cAdvisor627HTTP200; sin inferencias previas.
Espacio libre20045807616bytes. 22tests checkpoint/guardas y16inventario PASS.
Comprobación inicial deendpoints corregida de localhost aIPLAN donde escuchan;
no se modificaron exporters para corregir esa comprobación.

Rollback: detener/esperar cualquierworker antes derestaurar supervisor respaldado y
reducirRAM a10240 solo conuso real suficientemente inferior; revertir inventario,
precondición yNotes coordinadamente yreconciliarTerraform. No reducir límite bajo
un proceso activo ni restaurar datos devoz para deshacer un cambio derecursos.

## Ensayo único

JobAPI `7f348e97-7721-4f4e-827d-cf7e1458c045`.
Texto original573caracteres, SHA256
`c09d243905eac563e8379e6bc496a32347f3c1dc445ed577e8240baacfc47972`.
No se publica transcripción privada ni grabación original enGit. Misma referencia
Eduardo confirmada. Una sola llamadaPOST/generate, sin retries del transporte.
A→checkpoint persistente→liberaciónA→B300/context25. Resultado técnico completado, detallado abajo.

## Riesgos y siguiente paso

La ampliación no garantiza duración, velocidad ni consumo deldecoder. Se medirá
la duración real delWAV; no se rellenará con silencio ni se afirmarán60s sinmedición.
Narraciones5–10min quedan fuera deesta validación ydel límite actual1200caracteres/900s.
Monitorización central Prometheus tenía incidencia previa; node/cAdvisor directos
no acreditan toda lacadena central. Ningún otroLXC ni pipeline modificado. Sincommit/push.

## Resultado final del único ensayo

[Escuchar WAV en Voicebox](http://192.168.1.127:17493/audio/7f348e97-7721-4f4e-827d-cf7e1458c045).
Texto573caracteres continuo enuna sola llamada API, historialcompleted, errornull.
El audio dura **28,56segundos**, no55–60. No se modificó texto, velocidad ni se añadió
silencio; esta ejecución acredita ese texto yduración, no una narración60s ni5–10min.
No se ejecuta segundo intento automáticamente. Calidad/fidelidad ycontenido íntegro
requieren escucha delpropietario: EOS yWAVválido no sustituyen esa aceptación.

| Etapa/medida | Resultado |
| --- | --- |
| Carga Talker, intervalo evento |3,462s|
| Referencia preparada, desde inicio worker |23,426s|
| Generación Talker |251,073s;358tokens de secuencia;EOS verdadero;~1,426tokens/s|
| Proceso A, incluyendo preparación |274,603s; supervisión286,534s|
| Checkpoint completo |669×16int64;312pasos referencia+357generados;SHAverificado|
| Liberación A |PID0, runningfalse, cgroupvacío; BsinTalker/encoder|
| Proceso B |63,458s; supervisión74,276s; bloques300/context25|
| Tiempo total agente |362,182s (~6min2s), inferior alpresupuesto900s|
| WAV |685440muestras,24kHz,mono,PCM16;28,56s|
| PicoCT A / B muestreado |8,612GiB /6,121GiB|
| RSSHWM worker A / B |5,592GiB /2,474GiB|
| Pico anónimo CT A / B, muestreado |4,690GiB /2,171GiB|
| Pico file CT A / B, muestreado |3,849GiB /3,555GiB|
| Pico kernel CT A / B, muestreado |0,405GiB /0,396GiB|
| SwapCT máximo |4096bytes; crecimiento4KiB, sin crecimiento sostenido|
| PSIlocal full avg10 máximo |0,36% enA;0% enB|
| CPUCT acumulada A / B |634,295s /128,763s; incluye procesos residentes|
| MemAvailable host mínimo A / B |16,815GiB /19,028GiB|
| Eventos CT |high251→251,max0→0,OOM0→0; hostOOM0→0|

Los picos porcomponente no son necesariamente simultáneos. RSSHWM delproceso capta
picos que elmuestreo periódico delsupervisor puede omitir. No equiparar worker.current
conRSS ni atribuir la caché a memoria anónima. Elpico observado quedó incluso bajo
la antigua guarda9,5GiB: **este resultado no demuestra que15GiB sean el mínimo**.
Sí demuestra que la nueva admisión permitió completar este caso con holgura y las
guardas activas, después de la recuperación selectiva previaD079.

Checkpoint persistente privado:
`/srv/voicebox/qwen-worker/jobs/7f348e9777214f4e827dcf7e1458c045/checkpoint`.
Conservado también fuera deCT enarchivo privado; recuperaciónNPY desde otro proceso
validada con dimensiones,dtype,hashes yEOS, sin cargarQwen. Ambos jobs fallidos D078
continúan conservados ysincheckpoint. Ningúnoriginal devoz sepublica.

WAV brutoDecoder SHA `99ebe0e51047ce27971c619864e9d0401dae706f27e6ef993ce293cd740406a2`;
WAVdescargadoVoicebox SHA `ad10f32754ca80bd0e0e4c32d951710b7fa42c4907c73a2c39fc8193e9eab511`.
Difieren por normalización deVoicebox, habilitada enla petición; igual número de
muestras yduración. Ambos conservados, sinprocesar lareferencia.

## Cierre y coherencia operativa

Voicebox conserva imagenD079, ID, inicio yrestartcount0. Agente activo; workers
terminados. Perfil/muestras y77archivos protegidos iguales albackup; historial
incorpora exclusivamente elnuevo resultado. No inferencias activas alfinal.
Recursos finales15GiB/3CPU/2GiBswap/50GiB yguardas14GiB/worker9GiB verificadas.
Copias activas de supervisor yguardas PVE yrevisión inmutable CT coherentes; se
conservaron las versiones previas. Referencias10GiB/9,5GiB eninformes yrecetas
históricos no se reutilizan como política actual; README señalan su sustitución.
La receta de recursos aplicada porsegunda vez no cambia nada ni reinicia servicios.

Los17configPVE ajenos son idénticos a baseline. Sus contadores max pueden avanzar
por cargas propias; no se confunden conOOM ni conmodificaciones nuestras. Node y
cAdvisor627HTTP200 alfinal. GrafanahealthHTTP200/databaseok. Prometheus9090 sigue
inaccesible, incidencia anterior; no se reparó ni se afirma cadena central sana.
No cambios otrosLXC/pipeline, modelos, datos, backups niR/A/B; sincommit/push.

Evidencias: [host](evidence/2026-11-12-d080-preflight-host.json),
[plan](evidence/2026-11-12-d080-plan-reviewed.json),
[Terraform final](evidence/2026-11-12-d080-terraform-final.json),
[resize](evidence/2026-11-12-d080-resize.json),
[guardas](evidence/2026-11-12-d080-guards-consistency.json),
[preflight](evidence/2026-11-12-d080-preflight-final.json),
[resultado ymediciones](evidence/2026-11-12-d080-result.json),
[checkpoint recuperable](evidence/2026-11-12-d080-checkpoint-backup-verified.json),
[postflight](evidence/2026-11-12-d080-postflight.json),
[idempotencia recursos](evidence/2026-11-12-d080-resize-idempotent.json),
[final](evidence/2026-11-12-d080-final.json).

**Fase7.4 IN PROGRESS.** Siguiente: escuchar esteWAV yconfirmar voz/contenido;
después preparar un texto cuya duración natural seaproxime a60s yvalidarlo enun
ensayo separado. No extrapolar28,56s a60s ni ampliar texto/parámetros silenciosamente.
