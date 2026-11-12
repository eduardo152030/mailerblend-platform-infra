# Fase 7.4 — D077: ensayo real y Voicebox productivo

11 de noviembre de2026, Europe/Madrid; evidencias UTC conservadas.
**Ensayo aislado DONE; voz/texto aceptados; integración productiva DONE técnico.**
Fase7.4 IN PROGRESS: narración55–60s no se probó con este texto corto.

## Autorización y alcance

El propietario autorizó un único ensayo A→B con un texto nuevo exacto y, además,
modificar Voicebox para uso productivo. Se registró la ampliación antes de ejecutar.
Después escuchó el WAV y confirmó: **«Sí, voz y texto correctos»**. No se presume
aceptación de otros textos, voces o duración larga.

Texto utilizado,216caracteres, sin comillas envolventes ni cambios:

> Hola, soy Eduardo. Bienvenidos a un nuevo análisis de trading. Hoy vamos a revisar el mercado y buscar oportunidades de entrada. Recuerda que una buena gestión del riesgo es fundamental para proteger nuestro capital.

Se preparó jobnuevo `bienvenida01`, conservando narracion01 y los trabajos anteriores.
Referencia normalizada real y transcripción exacta425caracteres, verificadas por hash;
sin editar ni recortar original. CT6273vCPU/10GiB/2GiBswap; Base0.6B/FP32/CPU/SDPA,
3hilos/interop1, semilla42, max_new_tokens1024, decoder300/context25. Todas las guardas
se conservaron. No CT618, otrosLXC, pipeline, commit ni push.

## Ensayo único y medidas reales

Preflight independiente del supervisor pasó antes de cargar. La observación60s
registró host disponible mínimo21,40GiB, PSIlocal0 y swap estable. Hubo una lectura
adelantada del fichero local de observación cuando aún estaba vacío; no fue fallo
de recursos. El supervisor hizo su propio preflight y las31muestras se verificaron
al completar la observación. No afirmar que se esperó su fichero final antes de
arrancar: se corrige esa distinción en esta evidencia.

| Medición | Resultado |
| --- | --- |
| Carga A |3,44s |
| Referencia |312pasos, mismo archivo/transcripción |
| Talker |136tokens de secuencia, incluido EOS;95,547s;1,423tokens/s |
| Salida acústica nueva |135×16 códigos; prefijo referencia312×16 |
| Checkpoint |447×16 int64; commit atómico, checksum y readback PASS |
| A, tiempo de worker/supervisión |118,693s /130,105s |
| A, RSSHWM |5,592GiB; máximo muestreado4,566GiB |
| A, pico cgroup worker/CT |4,158GiB /8,141GiB |
| B |Solo decoder; no Talker ni encoder cargados |
| B, tiempo de worker/supervisión |42,078s /52,438s |
| B, RSSHWM /pico cgroup worker |2,276GiB /1,674GiB |
| B, pico cgroup CT |5,660GiB |
| CPU A, media/máximo muestreados |2,10 /2,69cores;251,67CPU-s |
| CPU B, media/máximo muestreados |1,90 /2,79cores;81,22CPU-s |
| Tiempo total del ensayo |183,041s |
| WAV |10,8s;24kHz;mono;PCM16;259200muestras |
| Swap CT/worker, PSIlocal, nuevos OOM |0 /0;0%;0 |
| Finalización |EOS, ambos procesos PID0/cgroup vacío, contenedores efímeros propios retirados |

RSS muestreado, RSSHWM y cgroup son métricas diferentes; no sumarlas ni confundir
filecache con memoria anónima. El texto es distinto del largo D076 por instrucción
expresa: no es una comparación causal de igual entrada ni prueba de decoder60s.
Se demuestra funcionamiento real separado y B sin Talker, con menor consumo
observado. No se ejecutó120 ni otro intento, ni otra inferencia para validar la API.

WAV SHA256:`881542af39639c5fbc82802206c4bd039ed76cd60d94a86c1cb2cea8deac8517`.
Checkpoint privado en `/srv/voicebox/pilot-d077/jobs/bienvenida01/checkpoint`, también
copiado fuera del CT en un archivo privado de81920bytes. No códigos ni grabaciones
en Git. Las cifras temporales provienen de procesos independientes; no suman con
exactitud el wall-clock total por overhead de SSH y supervisión.

## Despliegue productivo real

[Fuentes y operación](../../services/infra-voicebox/production-d077/README.md).
Cambios versionados: adaptador, agente dedicado, overlay afirmado contra el código
instalado, Dockerfile, stage/deploy/rollback, publicación idempotente del WAV y
observación; Compose, image-lock, deploy.sh y documentación. Fuentes D077 de
checkpoint/runtime/guardas se reutilizan sin cambiar parámetros de inferencia.

- Voicebox: imagen `local/voicebox:qwen-isolated-d077`, ID
  `sha256:7c747589727a4d283ae5cc0b549b522d5d0cd4602572a032d5b846127382547b`.
  Reemplazo solo de su contenedor, conservando volúmenes/perfil/historial y puertoLAN.
  La app no carga Qwen: adaptador por cola de archivos privada, sin socket Docker.
- PVE: `voicebox-qwen-627.service`, sin puertos nuevos, exclusivamente CT627;7,2MiB
  residentes observados, MemoryMax256MiB. Mantiene visibilidad de memoria física y
  cgroups del host. Solo ejecuta A/B mediante supervisores exclusivos de627.
- Worker ML usa la imagen original fijada por SHA, por lo que conserva exactamente
  backend/modelo probado. Se mantiene CT3CPU/10GiB/2GiB y hardworker9GiB; app conserva
  su límite6200m/memswap6600m. No se ampliaron recursos en esta intervención.
- Modelo/API por defecto0.6B, semilla efectiva42. Qwen procesa el texto entero,
  sin chunking de texto ni retry automático. Hasta1200caracteres, idiomaes,
  perfilEduardo confirmado, personalidad/instrucciones desactivadas. Otros tamaños
  y motores pesados no autorizados se rechazan antes de cargar. Kokoro/Piper conservados.
- A finaliza antes de B; B carga únicamente271entradas decoder.*, preserva contexto,
  frecuencia y recorte oficial, y nunca necesita Talker residente. Checkpoint privado
  inmutable para B por ambas rutas de montaje; fallo conserva códigos y métricas.
- Fallo/reinicio del agente no repite Talker. Cancelación escribe señal y espera al
  supervisor/cgroup propio. La recuperación de un decoder fallido sigue controlada,
  sin reintento automático ni cambio a120. No precargar Qwen desde Models.

Imagen originalD069 conservada, nuevo runtime archivado fuera de CT y fijado en lock.
`deploy.sh` detectaD077 para no usar la preparación histórica de modelos. Una segunda
aplicación de deploy PASS mantuvo exactamente mismo ID/StartedAt de Voicebox.
Notes627 sincronizadas con el estado actual; solo cambió su descripción PVE.
Terraform refresh-only revisado y aplicado, seguido de plan dirigido627 con cero
cambios. No se usó apply mutante ni se reinició CT para sincronizar notas.

## Backup, incidentes y rollback

Backup previo de datos, originales, DB y configuración:68archivos,75.593.783bytes,
copia externa verificada por SHA256/manifest y restore SQLite`integrity_check=ok`.
Los modelos HF de solo lectura no se duplicaron; no se modificaron. Lock/imagen
anteriores íntegros conservados como rollback. La nueva imagen se archivó también
fuera de CT; hash exacto en image-lock y evidencia de archivo.

El primer candidato tenía dos módulos nuevos600 propiedadroot. El smokeUID999 lo
detectó; **el despliegue empezó pese a esa comprobación fallida**, error de secuencia
operativa. Se restauraron Compose/imagen anteriores y se verificó health. Se corrigió
COPY con propietario999 y se añadió un gateUID999 obligatorio dentro de deploy.py,
antes de cualquier cambio de unidad o app. El despliegue corregido pasó.

Durante la publicación del WAV, un fichero nuevo quedó600/root al ejecutar el
importador como root; la descarga falló. Solo se reconciliaron propietario/modo de
ese WAV, con hash comprobado. El publicador ahora exige UID999; repetición idempotente
PASS y descarga completa/idéntica confirmada. No se cambiaron permisos del filesystem
original ni de grabaciones previas. Estas incidencias son de integración, no fallos
del ensayo ML. Las evidencias y el rollback se conservan; no se ocultan.

Rollback operativo versionado restaura únicamente Compose/imagen original y
deshabilita el agente dedicado. No restaura el DB antiguo por defecto ni elimina
nuevos WAV/checkpoints: conservar datos prevalece. Se comprobó vuelta real a imagen
original durante la incidencia; no se confunde con un mero script preparado.

## Validaciones y aceptación

- 17 tests de persistencia/guardas y6tests nuevos de adaptador/cola/cancelación:
  **23PASS en el runtime candidato**, sin pesos ni audio nuevos. El Python local
  carecía de soundfile para5tests del adaptador; se ejecutaron con sus dependencias
  reales en la imagen, sin instalar paquetes en host.
- Factory real y default0.6B probados como UID999 antes de sustituir Voicebox.
- Publicación idempotente del WAV aceptado: un único registro nuevo en el historial
  real de Eduardo, engineqwen/model0.6B/seed42; sin TTS adicional. Perfil y samples
  completos tienen hash de filas idéntico al backup. Generaciones3→4, sin borrar.
- APIhistorial y descarga byteidéntica PASS;1.7B rechazado400 antes de inferencia.
- Observación posterior **180,88s/7muestras PASS**: misma ID de app, healthy, agente
  activo/NRestarts0, exporters locales200, swap0, sin nuevosOOM ni ERROR/Traceback/
  HTTP5xx desde el inicio de esa ventana. PicoCT5,47GiB, mayoritariamente caché.
- Originales/referencia/transcripción y modelos conservados; otros LXC sin cambios.
  Prometheus9090 tenía una incidencia previa, no intervenida; Grafana/targets centrales
  no se dan por aceptados mediante checks locales. No se modificó Prometheus ni CT618.
- **Voz/texto del WAV10,8s aceptados expresamente**. La UAT de narración55–60s no se
  ha realizado. Tampoco una segunda inferencia real a través de la app: el límite de
  un ensayo se respetó. La integración se validó por componentes y API de datos;
  la próxima generación nueva de usuario recorrerá por primera vez UI/API→agente→A/B.

## Uso y siguiente paso

[Voicebox](http://192.168.1.127:17493): Eduardo — Mi Voz, Qwen0.6B, español,
semilla42 y personalidad desactivada. Generación en cola, un motor a la vez;
cancelación desde la UI, historial y descarga habituales. No cambiar memoria/guardas.

[Escuchar/descargar la muestra aceptada](http://192.168.1.127:17493/audio/225c8772-6b09-52b0-9580-c0001fff4bcb).
Este enlace sirve el WAV del ensayo, sin tempo, relleno ni audio regenerado.

Siguiente paso de Fase7.4: uso controlado desde Voicebox y, con alcance específico,
validar una narración55–60s. No se ejecuta otro ensayo automáticamente. Mantener
Qwen para la voz personal aceptada; seguir midiendo latencia y memoria de textos
largos. No continuar OpenVoice como motor principal. Sin commit ni push.

## Evidencias

- [Ensayo real](evidence/2026-11-11-d077-real-result.json).
- [Medidas A/B](evidence/2026-11-11-d077-real-measurements.json).
- [Despliegue e idempotencia](evidence/2026-11-11-d077-production-deploy.json).
- [Backup e imagen archivada](evidence/2026-11-11-d077-production-backup.json).
- [Observación](evidence/2026-11-11-d077-production-observation.json).
- [API y WAV aceptado](evidence/2026-11-11-d077-production-api.json).
- [Conservación y estado final](evidence/2026-11-11-d077-production-final.json).
