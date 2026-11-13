# Fase 7.4 — D-088: optimización de memoria Chatterbox y puerta D-089

13 de noviembre de 2026, Europe/Madrid. Evidencias originales conservan UTC.

## Resultado y alcance

Diagnóstico y candidato aislado completados; aceptación técnica de inferencia **BLOCKED**.
D-089 **STOP, sin despliegue ni audio**: falta demostrar con mediciones margen para
condicionamiento, generación y decoder. Una carga exitosa no satisface esa condición.
El mensaje D-089 recibido termina en «Si cualquier»; no se infieren condiciones omitidas.
Las condiciones explícitas ya impiden continuar.

Se ejecutaron exactamente las dos cargas autorizadas, sin referencia personal ni TTS.
Original terminó por error controlado; candidata completó. Ambos hijos recogidos,
contenedores detenidos, sin OOM ni swap del worker. No se repitieron cargas.
[Eventos y métricas filtrados](evidence/2026-11-13-d088-voicebox-memory.json).

## Causa demostrada

`from_local` conserva state_dict mientras construye otros componentes. La carga nativa
copia parámetros: al terminar T3 había 2.143.956.992 bytes de estado y cero bytes
compartidos con parámetros. Tras S3Gen, estados y módulos ocupaban conjuntamente
6.405.951.080 bytes de almacenamiento único. El candidato comparte exactamente
3.200.126.256 bytes mediante `load_state_dict(assign=True)` y reduce esa unión a
3.205.824.824 bytes: 2,980 GiB de duplicación evitada en esa fase.

Esta es una causa verificable del pico de carga, pero no demuestra que explique todo
el fallo D-087 ni caracteriza las activaciones de inferencia aún no ejecutadas.
D-087 alcanzó 7,696 GiB cgroup, con anon 4,326 y file 3,352 GiB; file_mapped 2,171
es subconjunto de file. RSS no se suma a cgroup. La caché no es toda inmediatamente
recuperable; no se cambió su contabilidad ni se ejecutó fadvise/drop_caches.

## Comparación medida

| Medida | Original | Candidata |
|---|---:|---:|
| Tiempo del proceso | 46,38 s, error tokenizer | 38,88 s, éxito |
| Pico RSS muestreado | 6,556 GiB | 4,557 GiB |
| Pico PSS en eventos | 6,536 GiB | 4,538 GiB |
| Pico cgroup muestreado | 4,408 GiB | 2,684 GiB |
| Pico anon worker | 4,363 GiB | 2,365 GiB |
| Pico file worker | 0,034 GiB | 0,343 GiB |
| Pico CT | 11,785 GiB | 10,095 GiB |
| Swap worker / OOM | 0 / 0 | 0 / 0 |

Los picos son independientes, no deben sumarse entre sí. RSS baja aproximadamente
1,999 GiB. Las cargas terminaron en cgroups distintos: el original falló antes del
protocolo de comparación compartida. La atribución de páginas ya cacheadas varía;
la diferencia cgroup no es una comparación de caché fría ni ahorro garantizado.
Se leyó completamente cada almacenamiento y se comprobó igualdad con los pesos;
no se presenta un mmap sin tocar como ahorro. Las fases VE/T3/S3 comunes permiten
comparar antes del cambio independiente del tokenizer.

## Candidato implementado

Código en `services/infra-voicebox/memory-d088/`: telemetry, load_probe, contracts,
driver, supervise_load y source-lock. Instrumentación persistente por fase mediante
JSONL/fsync, métricas cgroup/stat/PSI/eventos y RSS/HWM/PSS; seguimiento deduplicado
de storages con referencias débiles, sin registrar tensores, audio o transcripciones.
Hooks de condicionamiento, tokens y decoder preparados, **no ejecutados**.

Se conserva el constructor CPU oficial, pesos y precisión FP32. Solo se aplica
assign=True a la carga exterior de VE/T3/S3; no se usa meta, cuantización, trim,
gc forzado ni modificación de paquetes instalados. Buffers no persistentes están
materializados, trim_fade coincide con el nativo, pesos coinciden exactamente.
El watermarker nativo también se construyó, sin procesar audio.

El original encontró un segundo bloqueo: el tokenizer inicializa siempre un
segmentador chino que intenta escribir `/home/voicebox/.pkuseg` sobre filesystem
solo lectura. El candidato difiere únicamente esa inicialización hasta uso chino.
Los métodos originales de tokenización es/en y vocabulario permanecen intactos;
sus IDs se compararon con datos sintéticos. No se descargó el segmentador ni se
cambiaron permisos. Esta corrección ocurre después de las fases comparadas y no
se atribuye a ella el ahorro de pesos. Chino queda sin validar.

Compatibilidad sustentada en contratos sobre PyTorch 2.6.0+cpu real y el
[código PyTorch fijado](https://github.com/pytorch/pytorch/blob/v2.6.0/torch/nn/modules/module.py).
Motor Chatterbox fijado a `ab55923c27757c90cfcc407baa57dc25a7d25217`;
[loader oficial](https://github.com/resemble-ai/chatterbox/blob/ab55923c27757c90cfcc407baa57dc25a7d25217/src/chatterbox/mtl_tts.py).
Los hashes de modelo y entorno se conservan en source-lock; no referencias flotantes.

## Validaciones y limitaciones

Suite local completa: 69 tests, 61 PASS, 7 errores por dependencia `soundfile` ausente
en el Python local y 1 fallo en fixture heredado `test_d087_readiness`. No se ha
demostrado PASS de toda la suite; es un segundo bloqueo explícito de D-089. No se
modifican fixtures heredados ni dependencias productivas para ocultar esos resultados.
Tres pruebas locales nuevas PASS. Doce contratos únicos en entorno fijado PASS:
copy frente a assign, unión de storages, lectura completa, weight_norm, LSTM,
buffers CPU/no persistentes, incompatibilidad meta no persistente, hooks sin datos
privados, imports sin carga y tokenización es/en con auxiliar chino diferido.
Una preparación previa sin pesos detectó confusión entre PID Docker dentro del CT
y PID del cgroup en PVE; se corrigió y añadió regresión. No consumió un intento real.
Una desconexión SSH posterior a la candidata no perdió resultados persistentes;
se comprobó después PID 0, hijo recogido y sesión finalizada.

No se probó calidad acústica, preparación personal, generación o decoder. Tampoco
se ha demostrado margen bajo caché fría. No se declara Chatterbox aceptado ni listo
para producción. La optimización de carga es prometedora, no un certificado TTS.

## D-089: condiciones y siguiente validación

| Condición | Estado |
|---|---|
| Dos intentos controlados y procesos liberados | PASS |
| Duplicación demostrada y reducción RSS real | PASS |
| Carga completa optimizada, sin OOM/swap/guarda | PASS |
| FP32, pesos, módulos y referencia intactos | PASS |
| Margen medido de generación y decoder | **NO DEMOSTRADO** |
| Suite completa existente y nueva | Véase resultado de cierre; no sustituye inferencia |
| Qwen es/en saludable | PASS |

Por la condición explícita del propietario, D-089 queda BLOCKED antes de backup de
despliegue o cambios productivos. No hay autorización efectiva para saltar esta puerta.
Propuesta pendiente: un ensayo aislado español que mida condicionamiento, generación
y decoder con los hooks preparados, antes de despliegue. Requiere autorización
específica porque D-088 excluye TTS y D-089 lo condiciona a evidencia aún ausente.
Texto propuesto: «Hola, soy Eduardo. Esta es una prueba de mi voz utilizando
Chatterbox en español.» Referencia original solo lectura, sin efectos, sin reintentos,
FP32, CPU3, stop7/hard8/CT19 GiB, 300 s, máximo240 caracteres y cola exclusiva.
Conservar WAV para aceptación humana; detener ante fallo sin habilitar producción.
No se garantiza que quepa ni se estima margen restando simplemente 2,684 de 7 GiB.

## Producción y recuperación

Lectura final 2026-11-13 02:44:11 UTC: Voicebox healthy, mismo ID/imagen/StartedAt,
USER999:999, capacidades cero, agente activo; Qwen es/en ready, Kokoro/Piper ready,
Chatterbox deshabilitado. Configuraciones PVE comparadas sin cambios; 105 archivos
protegidos intactos, tres checkpoints válidos con EOS; SQLite íntegra, 1 perfil,
1 referencia y 8 generaciones. WAV D-081 HTTP200 y checksum conservado.
No inferencias residuales ni OOM nuevos. CT conserva20GiB/3CPU/2GiBswap/100GiB;
CT PSI10s0, host disponible21,78GiB y thin pool libre30,98% en la lectura final.

No hubo despliegue que revertir. Para abandonar el candidato basta con no activarlo;
se preservan imágenes, pesos, backups y evidencias. Evidencias privadas fuera de Git
en `~/.local/share/mailerblend-recovery/voicebox-d088-memory/`, y en HDD PVE
`/mnt/storage/d088-memory*`; no contienen grabación personal. No borrar estos artefactos.
Sin cambios de recursos, otros LXC, pipeline, commit ni push.
