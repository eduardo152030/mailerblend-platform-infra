# Fase 7.4 — D075 Fase B: primer intento oficial FP32 instrumentado

## Seguimiento posterior — escalones03–05 y sustitución por D076

03:EporPSICT,04:EOS14pasos/13frames ydecoderiniciado con corteEworker5,841GiB;
05:EporPSIglobal durante referencia.0OOM/PID0;06solo preflight, no se lanzó.
NoWAV. Elpropietario sustituyó elalcance por nuevaRAMfísica yCT10GiB/swap2GiB,
worker9GiB yobjetivo60s: [D076](PHASE7-D076-LONG-NARRATION.md). Elhistóricoinferior
permanece; no se atribuyeWAV a estos escalones.


## Seguimiento — repetición02 completada, resultado E

La corrección `NUMBA_CACHE_DIR=/tmp/numba` pasó: cache/tmpfs escribible porUID999,
128MiB iniciales, importsNumba0.60/librosa0.11/backend correctos. CargaFP32
completada en9,052s; la ejecución atravesó validaciones deparámetrosfloat32 y
llegó a reference_prompt:start, sin generación/decode/WAV. Se detuvo por crecimiento
de swapCT32,445MiB frente aumbral16MiB, no porOOM ni timeout. Total18,611s,
parada3,531s,PID0/Runningfalse/Exit137/OOMKilledfalse. RSSmuestreado3,413GiB,
worker3,287GiB,CT4,886GiB; máximos parciales, noHWM completo. Swapdespués457,94MiB,
0OOM nuevos; Voicebox/profile/originales/configPVE/59targets/Grafana conservados.
No se deduce viabilidad de inferencia completa solo de la carga.
[Evidencia02](evidence/2026-11-11-d075-b02-summary.json).

El propietario ha autorizado después pruebascortas con umbrales graduales, sin
cambiar recursos ni producción; se registra cada escalón aparte. Los informes
inferiores de01 se conservan como histórico.


Estado: **intento único DONE — resultado F; validación FP32 BLOCKED**.
11nov2026, Europe/Madrid. Inicio Docker16:09:50,941UTC (17:09:50,941CET),
fin16:10:00,061UTC. No segundo intento, narración ni cambio productivo.
[Antecedente Fase A](PHASE7-D075-QWEN-HYPOTHESES-PHASE-A.md).

## Resultado y responsabilidad del fallo

**F. Error identificado antes de cargar Qwen.** La importación de qwen_tts/librosa
falló con `RuntimeError: cannot cache function '__o_fold': no locator available for
file '/usr/local/lib/python3.12/site-packages/librosa/core/notation.py'`.

Configuré el worker con filesystem raíz de solo lectura, pero **omití redirigir
NUMBA_CACHE_DIR a su tmpfs escribible**. Los localizadores de caché de Numba no
pudieron utilizar sus ubicaciones habituales. Es un error de preparación del piloto,
no una prueba de que FP32, SDPA, Qwen o la clonación fallen en este hardware.
No hay datos para comparar rendimiento o memoria del modelo con BF16.

Se contó este lanzamiento como el único intento autorizado y se detuvo la intervención.
**0 llamadas de carga de pesos, 0 llamadas de generación, 0 tokens producidos y ningún
WAV.** No se han vuelto a importar/probar el motor ni reiniciado el worker después.
El parámetro solicitado FP32 no llegó a validarse sobre parámetros de un modelo.

Corrección preparada, **no aplicada/ejecutada**: variable del worker aislado
`NUMBA_CACHE_DIR=/tmp/numba`, usando el tmpfs ya existente. Mantener rootFS, modelos y
referencia solo lectura; no montar ni escribir la caché de producción. Véase
[configuración propuesta](../../services/infra-voicebox/pilot-d075-b/numba-cache-fix.proposed.json).
Un nuevo lanzamiento requiere autorización porque el propietario limitó esta
intervención a una prueba. No cambiar recursos ni recomendar ampliación por este fallo.

## Comprobaciones previas reales

Ventana de60s/31muestras, sin motor cargado ni trabajo activo. HostMemAvailable
mínimo **9,345GiB**. CT627current3,767–3,778GiB; swap412,230–412,242MiB, variación
~12KiB, PSI propio fullavg10=0,00%. Hostfullavg10=0,01–2,06%, sin≥2% sostenido10s.
Swapglobal en la ventana:188páginas deentrada/115salida (~0,734/0,449MiB si4KiB),
no actividad creciente significativa deCT; sin pgscan_direct/kswapd niOOM nuevos.
No reinicioCT, swapoff ni vaciado de caché.

Disco19,00GiB disponibles, Voiceboxhealthy/model_loadedfalse,0jobs activos,59targetsUP.
Se aceptó únicamente un **intento acotado**, no una estimación garantizada de éxito:
los pesosFP32 mínimos son~4,043GiB más runtime, referencia, prefill ydecodificador;
los transitorios completos no están medidos. No asumir que todo filecache se libera
inmediatamente. La carga se habría detenido si superaba el presupuesto operativo.

Límites del worker:3CPU/6GiBRAM/6GiBRAM+swap (sin swap adicional del worker),
hilosintraop2/interop1. No son ampliaciones delLXC, que conserva3CPU/7GiB/512MiBswap.
Umbrales externos:CTcurrent6,6GiB,workercurrent5,75GiB,RSS5,6GiB,swapCT+16MiB,
hostdisponible<2GiB,PSIfullhost≥2% durante10s oCT≥1% durante5s,OOMnuevo.
Timeout máximo300s; guard externo295s deja margen deparada y alarma delproceso295s.
Un modelo productivo que empezase a cargarse también detendría el worker.

## Motor, referencia y comando exactos

Motor **oficial qwen-tts0.1.1**, PyTorch2.8.0+cpu yTransformers4.57.3, ya instalados
sin descargar/actualizar. ImagenD069
`sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b`.
Las recetas del fork no se usan para generar: el script importa directamente la
clase oficial Qwen3TTSModel. [Hashes del código oficial instalado](evidence/2026-11-11-d075-b-source.json).
No se atribuye una revisiónGit ficticia al paquetePyPI; se fija versión+SHA de fuente
instalada+imagen. No parches persistentes al motor.

Modelo previsto: **Qwen3-TTS-12Hz-0.6B-Base**, snapshot
`5d83992436eae1d760afd27aff78a71d676296fc`, CPU, `dtype=torch.float32`,
`attn_implementation='sdpa'`, `local_files_only=True`. NoCustomVoice ni cómputoBF16.
Las entradas safetensors existentes almacenadasBF16 serían convertidas aFP32 por
el cargador; esto no equivale a inferenciaBF16. Esta conversión no llegó a ejecutarse.

Referencia deEduardo normalizada24,883s,PCM16mono24kHz,425caracteres exactos,
verificada frente al registroAPI ytexto privado confirmado. Hash de la referencia y
original idénticos albaseline; el original no se recorta ni se modifica. Clonación
previstaaudio+texto/ICL, x_vector_only_mode=False. La referencia/transcripción no se
publican enGit ni enlogs; modelos yreferencia se montanRO.

Lanzamiento ejecutado por pctexec627 desdePVE, equivalente exacto del argvDocker:

```sh
docker run -d --name qwen-d075-b-fp32-01 \
  --network none --no-healthcheck --cpus 3 --memory 6g --memory-swap 6g \
  --pids-limit 96 --user 999:999 --read-only --cap-drop ALL \
  --security-opt no-new-privileges --tmpfs /tmp:rw,size=128m \
  -e HF_HUB_OFFLINE=1 -e HF_HOME=/cache \
  -e OMP_NUM_THREADS=2 -e MKL_NUM_THREADS=2 \
  -e TOKENIZERS_PARALLELISM=false -e PYTHONDONTWRITEBYTECODE=1 \
  -v /srv/voicebox/huggingface:/cache:ro \
  -v /srv/voicebox/pilot-d072/private:/private:ro \
  -v /srv/voicebox/pilot-d075-b/infer.py:/infer.py:ro \
  -v /srv/voicebox/pilot-d075-b/job01:/job:rw \
  --workdir /job --entrypoint python \
  local/voicebox:8af7efe62fab-personal-d069 /infer.py
```

**NUMBA_CACHE_DIR no estaba definido en este comando.** No se añade retrospectivamente
para presentar como ejecutada una configuración corregida. No restaurar ni desplegar
este comando como configuración productiva. Script ysupervisor en
[directorio del piloto](../../services/infra-voicebox/pilot-d075-b/).

## Cómo se limitarían y contarían los tokens

Firma real: generate_voice_clone recibe kwargs; llama a _merge_generate_kwargs.
Ese método elige el argumento explícito max_new_tokens antes que generate_defaults
(del snapshot8192) yantes que elhard_default2048 delpaquete. Después model.generate
lo coloca en talker_kwargs ylo pasa a talker.generate deGenerationMixin.

Petición prevista única:

```python
model.generate_voice_clone(
    text="Hola, soy Eduardo.",
    language="Spanish",
    voice_clone_prompt=prompt,
    max_new_tokens=64,
)
```

La preparación deprompt usa ref_audio/ref_text reales, x_vector_only_mode=False.
64 limita los pasos nuevos de la secuencia autorregresiva delTalker, **no los BPE del
texto ni la suma de todos los codebooks internos**. ElCodePredictor tiene sus propios
pasos por grupo. La implementación construye audio_codes yelimina el stopcode; por
ello se registrarían por separado longitud de sequences, número de hidden_state_steps,
llamadasforward, presencia deEOS yformas reales de códigos acústicos. No se promete
64tokens=64frames ni duración fija. El códec puede recibir referencia+códigos nuevos
para luego cortar el prefijo deaudio; su trabajo puede superar el del fragmento final.

Se prepararon wrappers locales enmemoria para tiempos de carga, referencia/encode,
primerforward(prefill),Talker,coregenerate,decode ywrite, con firma forward preservada.
EOS se detectaría sobre la secuencia real frente alcodec_eos_token_id, yTOKEN_LIMIT
si alcanza elcap sinEOS. Timeout yguarda externa se distinguirían. **Ningún wrapper
de modelo llegó a ejecutarse en este intento**; análisis deaplicación del argumento
por código, no verificación dinámica fingida.

## Mediciones obtenidas

| Etapa / resultado | Medición |
|---|---|
| Importación antes del error | 8,205s hasta fallo dentro del worker |
| Carga modelo / preparación referencia | No alcanzadas |
| Prefill / generación / decode / write | No alcanzados |
| Tokens / tokens porsegundo / EOS | 0 / no aplicable / no observado |
| Duración audio / enlace | NoWAV; no duración ni muestra |
| Total supervisor, incluida parada/verificación | 14,326s |
| RSSHWM del proceso | 506.544.128B /483,078MiB |
| RSS máximo muestreado externo | 494.354.432B /471,453MiB |
| Workercgroup máximo | 586.895.360B /559,707MiB |
| Workeranon/file/kernel máximos | 330.993.664 /249.937.920 /5.488.640B |
| CT627current máximo | 4.735.373.312B /4,410GiB |
| CTanon/file/kernel máximos | 549.273.600 /3.705.630.720 /477.245.440B |
| Swapworker | 0 |
| SwapCT máxima / aumento frentebaseline | 432.181.248B (~412,16MiB) /0 |
| PSIfullhostavg10 máximo durante intento | 0,12% |
| Pico CPUworker por intervalo | 0,865cores, solo importación |
| OOM / oom_kill nuevos | 0/0 |

Los máximos de componentes se tomaron en instantes distintos: no sumarlos como un
único pico. RSSmuestreado puede quedar por debajo delHWM. Memoria medida corresponde
a importación/runtime ycache de librerías, **no a cargar/inferir Qwen FP32**.
No guardaderesursos, timeout, EOS ni límite detokens provocaron el fallo.

## Cancelación y protección final

El proceso salió por su excepción, ExitCode1,OOMKilledfalse. Supervisor comprobó
Runningfalse/PID0; dockerstop sobre worker ya parado tardó0,756s, sin proceso/hilos
inferentes residuales. No fue necesario matar unhilo deVoicebox ni reiniciar servicio
alguno. El límite de cinco minutos y cancelación externa quedaron preparados, pero
**no fueron estresados por una inferencia larga** en esta ocasión.

Voiceboxhealthy, mismoID/imagen/StartedAt/restarts. PerfilEduardo, referencia yoriginal
conservados. ModelosPiper/Kokoro/Qwen siguen disponibles; no motores desinstalados,
archivos borrados ni cambio dehistorial.27configuracionesPVE intactas,otros17LXC sin
cambios, ningún CT618/cAdvisor modificado.59targetsUP,0alertas y0OOM nuevos.
Grafana/database yconsulta aPrometheus por proxy correctas. Los contadores de logs
productivos se guardan sin mostrar contenido privado.

## Recomendación y parada

Corregir únicamente NUMBA_CACHE_DIR del worker aislado altmpfs y comprobar sus
permisos **antes de un eventual nuevo lanzamiento autorizado**. Mantener64tokens,
FP32/SDPA, referenciaexacta, límite300s yguardas. No recomendar másRAM ni concluir
queFP32 mejora/empeora Qwen: **esa comparación sigue sin realizarse**.
No ejecutar una segunda prueba,30/60s ni promover cambios a producción eneste cierre.

Fase7.4 INPROGRESS. D075B intento único concluidoF; validaciónFP32 BLOCKED por
preparación corregible. Corrección propuesta sin ejecutar. Detenido para revisión;
sin commit/push.

## Evidencias

- [Preflight](evidence/2026-11-11-d075-b-preflight.json).
- [Resumen con clasificación F](evidence/2026-11-11-d075-b-summary.json).
- [Serie de mediciones](evidence/2026-11-11-d075-b-measurements.json).
- [Resultado del worker](evidence/2026-11-11-d075-b-worker.json).
- [Fuente instalada/versiones](evidence/2026-11-11-d075-b-source.json).
- [Preservación final](evidence/2026-11-11-d075-b-final.json).

SintaxisPython/JSON, referenciaslocales ygitdiff--check comprobados. Ningún audio ni
transcripción privada incorporados alrepositorio. No se declara generada una muestra.
