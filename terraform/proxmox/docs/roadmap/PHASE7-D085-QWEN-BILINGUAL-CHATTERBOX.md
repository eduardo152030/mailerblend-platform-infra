# Fase 7.4 — D085: Qwen bilingüe, Chatterbox Multilingual y efectos

**Actualización D086:** candidato bloqueado por incompatibilidad USER/entrypoint;
rollback D081 verificado. No volver a desplegar este tag sin corregir y probar
el arranque real bajo nueva autorización. [Diagnóstico D086](PHASE7-D086-QWEN-CHATTERBOX-VALIDATION.md).

12 de noviembre de 2026, Europe/Madrid. **Preparación DONE; despliegue TODO;
ensayos reales TODO; aceptación acústica TODO.** D081 continúa ACCEPTED / PRODUCTION.
No se ha cambiado el servicio productivo, ejecutado inferencia real ni hecho commit/push.

## Resultado y límites de aceptación

Existe una imagen candidata completa con UI y backend, un paquete coordinado de
controller/worker y un entorno Chatterbox aislado en SSD. Las pruebas sin voz pasan.
**No equivale a tener inglés o Chatterbox funcionando en producción** ni a demostrar
calidad, duración, latencia o pico de memoria de una generación Chatterbox.

Confirmaciones solicitadas por el propietario:

1. Chatterbox utilizará el fichero de referencia existente de Eduardo, comprobado
   por SHA y montado RO. Su procesamiento nativo combina embedding de hablante,
   códigos acústicos de referencia T3 y condicionamiento del decoder S3Gen; no usa
   códigos/checkpoints Qwen. Perfil, transcripción y grabaciones no se modifican.
2. El límite240 es exclusivo Chatterbox. Qwen conserva1200caracteres, semilla42,
   FP32,0.6B,A/B/checkpoint,300/context25,900s y sus guardas14/9/8,2GiB.
3. Las dependencias efectivas están fijadas por versiones y hashes. La dependencia
   Perth que upstream declara desde master se sustituye únicamente en metadata
   de construcción por un commit completo. No hay VCS flotante en el paquete instalado.

Los efectos Robotic, Radio, Echo Chamber y Deep Voice están preparados como
selecciones por generación. Se reutilizan los cuatro presets nativos, ya presentes
en producción, y el DSP existente. No se cambia el efecto predeterminado del perfil.

## Recuperación del candidato D083 y Qwen

Los16 archivos D083 conservan sus hashes. Pasan10tests Python y4UI originales.
Se reutilizan adaptador, validaciones, política de idiomas y worker; no se rehace
la implementación. Es/en llega desde formulario→API→request.json→agente→worker;
el worker mapea **es→Spanish / en→English** al llamar al modelo. Las pruebas D083
simulan esa invocación real y comprueban referencia/transcripción,FP32,semilla ycheckpoint.
No se traduce la referencia española ni se activa x-vector-only.

La API conserva perfil Eduardo/modelo0.6B/semilla42/sin instrucciones ni personalidad.
Otros idiomas se rechazan. La política nueva delega Qwen a la validación D083 y
aplica límites separados a Chatterbox. Corrige también el default model_size0.6B
heredado de Qwen cuando una solicitud Chatterbox no incluye ese campo.

Referencia existente: WAV PCM16 mono,24000Hz,24,882667s; transcripción425caracteres.
Los hashes coinciden con el contrato previo. Chatterbox realiza sus recortes internos
habituales en memoria (T3≈6s/S3Gen≈10s), además del encoder de hablante, sin recortar
ni escribir el archivo. Qwen mantiene su preparación original audio+texto.

## Chatterbox: selección y mantenimiento

Se selecciona **Chatterbox Multilingual V3 general**, no original inglés, Turbo ni
Single Language Pack. Fuente oficial fijada:

- Chatterbox `ab55923c27757c90cfcc407baa57dc25a7d25217`, etiqueta de paquete0.1.7.
- Pesos `ResembleAI/chatterbox@5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18`.
- Perth `ff1c8ac55a976971245cdd53c18d6131ca00d993`, paquete1.1.0.
- Fork Voicebox `8af7efe62fab8d33e2a5dfbedabaa45f68a5184f`.

El nombre de paquete0.1.7 por sí solo no distingue el V2 instalado de este V3.
El fork tenía backend nativo Multilingual, pero cargaba V2 por defecto y estaba
excluido por la admisión CT627. Se conserva su integración de perfiles/historial;
se reemplaza su factory candidata por un adaptador de cola, sin cargar ML en la app.

Código y modelo declaran MIT; se conservan los avisos de subcomponentes, incluidos
S3Gen/CosyVoice y dependencias. [Modelo oficial fijado](https://huggingface.co/ResembleAI/chatterbox/blob/5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18/README.md).
El repositorio oficial anuncia retirada de mantenimiento desde agosto2026: riesgo
real para soporte y futuras incompatibilidades; no se infiere soporte comercial.
[Estado de upstream](https://github.com/resemble-ai/chatterbox).

## Dependencias y entorno aislado

Imagen base de worker existente e inmutable bcc5c14f…, Linuxx86_64/Python3.12.16.
Nuevo venv persistente `/srv/voicebox/chatterbox-d085/venv`, visible como `/cb/venv`
solo en workers candidatos. No se actualiza PyTorch ni se instala nada en VoiceboxD081.

| Componente | Versión efectiva |
| --- | --- |
| torch / torchaudio |2.6.0+cpu /2.6.0+cpu|
| transformers / diffusers |5.2.0 /0.29.0|
| numpy / librosa |1.26.4 /0.11.0|
| safetensors / s3tokenizer |0.5.3 /0.3.0|
| resemble-perth |1.1.0, commit anterior|
| Construcción |uv0.12.13; setuptools80.9.0; wheel0.45.1; uv_build0.12.7|
| UI |Bun1.3.14 fijado por hash; bun.lock congelado del fork|

113distribuciones instaladas:111versiones comprobadas contra lock, más los dos
paquetes fuente fijados. Instalación con require-hashes y build-constraints;
chatterbox se construye desde fuente fijada y se instala sin resolver de nuevo deps.
No paquetes CUDA/NVIDIA/triton. uv no conserva el hash del archivo Perth en
archive_info de direct_url.json; la URL sí contiene el commit y la integridad se
comprueba mediante el lock con require-hashes y el archivo fuente verificado.

Imports reales de torch/torchaudio/librosa/Perth/diffusers/transformers y clase
Multilingual PASS, con loaders de pesos bloqueados. CPU AVX2/FMA del i5-6500 y3vCPU;
FP32 explícito, sin BF16. Referencia y tokenizador no necesitan GPU.
La advertencia inicial de cache home RO se corrige fijando HF_HOME aislado;
se comprobó lookup Cangjie offline con hardlink al archivo verificado, sin duplicar
pesos. El recurso Perth de watermark37,43MB está incluido y verificado sin cargarlo.

## Descarga selectiva y disco medido

Se descargaron únicamente5archivos, **3208844550bytes (≈2,989GiB)**:
t3_mtl23ls_v3.safetensors, s3gen.pt, ve.pt, grapheme_mtl_merged_expanded_v1.json y
Cangjie5_TC.json. Se excluye conds.pt: no se instala una voz predeterminada de terceros.
[Revisiones y hashes completos](../../services/infra-voicebox/candidate-d085/models.lock.json).

Durante la descarga: comprobaciones cada64MiB y por archivo, límite12GiB de
crecimiento, rootfs>20GiB y pool físico≥20%libre. Todos los controles pasaron;
archivos parciales se habrían conservado ante fallo, sin reintentos automáticos.
Checksums LFS o gitblob y SHA256 final, fsync y renombrado atómico.

| Métrica | Antes | Final |
| --- | ---: | ---: |
| Disponible dentro CT627 |65,494GiB|60,025GiB|
| Ocupado rootfs |28,093GiB|33,561GiB|
| Entorno nuevo completo, incluido modelos/cache/contextos |0|4,796GiB físicos|
| Libre físico thin pool |124,235GiB|124.155GiB|
| Libre físico thin pool (%) |≈31,05%|31.03%|
| Reserva mínima del pool |80,017GiB|Respetada|

Captura final 2026-11-12T18:53:16.479677+00:00 UTC. El disco sigue100GiB local-lvm/SSD, CPU3,
RAM15360MiB yswap2048MiB. No cambian rutas Docker/containerd/Qwen. El nuevo uso
reutiliza también bloques thin ya asignados; no sumar el crecimiento lógico como
asignación física nueva ni considerar100GiB una reserva exclusiva.
La imagen candidata tiene≈1,203GiB lógicos totales y comparte capas D081; no se
suma otra vez ese tamaño a du. Backups previos e imágenes intermedias conservados.

## Memoria: medición y estimación separadas

**Medido**: proceso de imports, RSSmáximo615388KiB (≈601MiB). Preparación auxiliar
limitada a1CPU/2GiB, sin modelos cargados. memory.events acumuló367eventos max en
hijos limitados; memory.events.local delCT conserva max0, OOM/kill0. No afirmar que
615MiB sea el máximo de instalación ni el pico del modelo completo.

Lectura sin deserializar tensores: T3 contiene535989248parámetrosF32 y2143956992bytes;
S3Gen1056169264bytes de storages yVE5694472. Al cargar, from_local retiene diccionarios
T3/S3 a la vez que los parámetros: estimación de pico de arranque≈6–7GiB incluyendo
imports/duplicados; **no es una medición de carga**. Activaciones/decoder todavía
pendientes de medir. No se cuantiza ni se reutilizan estimaciones BF16 de Qwen.

Controles propios CB preparados: hard8GiB, parada7GiB, CT14GiB sin cambios,
300s totales,400tokens T3, EOS obligatorio antes de decoder y audio de piloto≤20s.
Preflight proyecta baselineCT+7GiB+0,5GiB≤14, host disponible≥10GiB ysin presión local.
La captura de preparación CT1,956GiB/host20,464GiB/swap0/PSIlocal0 lo supera;
se debe repetir inmediatamente antes de cualquier ensayo. Último CT2,229GiB,
swap0 yPSIlocal0; no OOM ni errores kernel I/O/ext4 nuevos.

## Código y exclusión mutua

[Archivos y procedimiento reproducible](../../services/infra-voicebox/candidate-d085/README.md):
política, adaptador, agente, supervisorCB, worker, readiness, overlaysAPI/UI,
lock de dependencias/modelos/fuentes, construcción UI eimagen, fixtures ybackup.

Una cola, un motor pesado, un flock PVE existente. Qwen conserva su supervisor y
A→checkpoint→B; CB tiene su propio proceso yresultado. No precarga. Antes de cambiar,
se verifica PID0/cgroup vacío y memoria; cancelación/timeout matan todo el worker.
No nuevo servicio ni puerto. Networknone en inferencia y montaje RO de entorno,
modelos, fuente y referencia; solo el directorio deljob es escribible.

El release CB propuesto tiene enabled=false. Solo se anuncia si heartbeat fresco,
protocolos, bundle, receipt de dependencias y manifiesto del modelo coinciden.
Historial conserva engine/lang/seed existentes y recibe un único WAV final.
Retry/Regenerate conID conservado devuelve409 **antes de tocar la fila**, sin repetir
Talker. Un nuevo Generar crea otro intento explícito; checkpoints Qwen anteriores
no se borran ni se reanudan automáticamente. No se cambió el esquemaSQLite.

## Efectos y pruebas sin voz

Se reutilizan Robotic (flanger), Radio (filtros/distorsión), Echo Chamber
(delay/reverb) y Deep Voice (pitch shift). Selector candidato accesible y con esos
cuatro primero; mantiene otros presets y el default sin efecto. DSP se aplica al
WAV de salida después de liberar el workerML; referencia y perfil siguen intactos.
Se conserva versión limpia interna y un único WAV procesado predeterminado.

| Verificación | Resultado |
| --- | --- |
| Hashes candidatoD083 |16/16 intactos|
| Tests D083 |10Python +4UI PASS|
| Tests D085 |11Python +5UI PASS|
| Imagen candidata: API real con ejecución simulada |14comprobaciones PASS|
| Envío de efectos a ambos motores |8comprobaciones PASS|
| DSP sobre señal sintética |4presets PASS, salida finita, input inmutable|
| Presets en DB temporal aislada |4creados/listados; DB productiva no tocada|
| UI completa |TypeScript + Vite PASS; reproducción desde archivo fijado PASS|
| Compatibilidad dependencias |113paquetes, pipcheck eimports PASS|
| Lookup offline y recurso watermark |PASS, sin cargar pesos|
| Referencia/perfil/checkpoints/datos históricos |111archivos intactos;1perfil/1ref/6WAV|
| Producción yotrosLXC |Mismo ID/inicio/imagen;27configs idénticas, otros17sin cambios|

Las pruebas no juzgan parecido, acento ni pronunciación; el DSP sintético no es
una prueba acústica con Eduardo. Advertencia de Vite por bundle>500kB heredada,
no error. No se procesa la grabación personal para probar efectos.

Imagen candidata construida, **sin desplegar**:
`local/voicebox:d085-candidate` / `sha256:19af4754968dacacbb9104f8ea40826dbea4f9f772992397cf322802d7babbfe`.
D081 sigue usando09774c5b…; worker originalbcc5c14f… yfuentes activas idénticos.

## Backups y rollback

D082 accepted-final revalidado por SHA. D084 completo19GBdecimales/17,651GiB en HDD
releído: SHA3fa4107c… coincide; restauración de archivos ya acreditada D084, no DRboot.
Nuevo backup coherente de datos/config/jobsD085:117archivos, SQLiteok,6WAV y1referencia,
restaurado fueraPVE yverificado por manifiesto. SHA
9ac082cf85ac771a632abc4000b2f198b1de7b6c95c896aeae131d6021a390d1.
Copia HDD `/mnt/storage/d085-before-deploy/application.tar.gz` (82,49MB) ycontroller
PVE/unidad/config627 separados; copia privada externa alhost. No se borran anteriores.

Antes de despliegue futuro, refrescar/revalidar ese backup si hay cambios posteriores.
Rollback coordinado: cola vacía yworkers muertos, imagen app/UI D081 máscontroller
PVE ysrcCT originales; deshabilitarCB. Conservar SQLite, historial, nuevosjobs,
checkpoints, modelos yrootfs100GiB. No reducir disco ni alterar otrosLXC.

## Plan autorizable y punto de parada

1. Autorizar exclusivamente despliegue candidato enCT627. Revalidar salud, snapshots,
   disco≥20%pool, memoria ysin inferencias; backup fresco yfuentes/imágenes recuperables.
2. Coordinar app/UI, controller yworker; supervisor/guardasQwen intactos. Habilitar
   receiptCB después de verificar hashes. No unidad/puerto/recursos nuevos.
3. Comprobar capacidades es/en, modelos disponibles, perfil e historial, descarga
   WAVexistente, cola/cancelación ysegunda aplicación sin recreación innecesaria.
4. Con aprobación acústica explícita, ejecutar **solo A→B→C**, de uno en uno,
   sin efectos ycon la misma referencia. Preflight entre trabajos; cancelar ante guarda,
   conservar evidencias yno repetir automáticamente. SiA falla, detener la secuencia.
5. Entregar WAV ymediciones para escucha; no declarar ganador ni calidad aceptada
   antes de oírlo elpropietario. Efectos con voz real requerirán revisión posterior;
   no se aplican alclon de referencia ni se usan para evaluar fidelidad inicial.

| Ensayo | Texto exacto | Controles/coste esperado |
| --- | --- | --- |
| A:QwenEnglish |This is a test to see if I can speak in English.|FP32,3CPU,hard9GiB/stop8,2/CT14,900s; latencia inglesa no medida|
| B:CBSpanish |Hola, soy Eduardo. Esta es una prueba de mi voz utilizando Chatterbox en español.|FP32,3CPU,hard8/stop7/CT14,300s; pico yvelocidad pendientes|
| C:CBEnglish |Hello, my name is Eduardo. This is a test of my cloned voice using Chatterbox in English.|Mismos controlesCB; posible acento español de la referencia|

Se medirán carga, tokens/EOS, decoder, RSS/anon/file/cgroup/swap/PSI/CPU/OOM,
latencia total yduración WAV. No ensayos largos ni repetición automática.
**Intervención detenida aquí**: preparar no autoriza despliegue ni esos tres audios.

## Evidencias

[Disco ypreservación](evidence/2026-11-12-d085-resources-final.json),
[descarga controlada](evidence/2026-11-12-d085-model-download.json),
[dependencias instaladas](evidence/2026-11-12-d085-dependencies.json),
[imports](evidence/2026-11-12-d085-imports.json),
[API yefectos](evidence/2026-11-12-d085-api-effects-tests.json),
[componentes delmodelo](evidence/2026-11-12-d085-model-components.json),
[backup restaurado](evidence/2026-11-12-d085-backup-verified.json).
