# Fase 7.4 — D068: ensayo finito y operación Voicebox

[Estado y evidencia](../../../docs/roadmap/PHASE7-D068-VOICEBOX.md).
La autorización es únicamente CT627, máximo7GiB,CPU3/swap512/disco50; ningún otroCT.

`probe.py` instrumenta runtime/carga, llamadas talker/predictor, logits finitos y
rangoEOS, producción de códigos ycodec. Revisión localHF fijada ycache sololectura,
NUMBA_CACHE_DIR independiente, usuario explícito. No aplicar elprobe como backend
productivo ni presentar la salida truncada por el cap diagnóstico comoTTS aceptado.
`supervisor.py` vive enPVE fuera del CT; cgroup/RSS/swap/OOM/CPU/PSI ytargets de
servicios restantes. Corta a6,5GiB,swapcrece64MiB,OOM,host<1,5GiBdisponible,
PSIfullavg10>=2%,45s sinprogreso o plazo finito. Los16frames de diagnóstico no
son PruebaA completada; tras veto no se pasa a15–30s ni al texto120–150palabras.

D068 se detuvo en la fase diagnóstica. No reejecutar por interpretar esta receta
como aprobación de más pilotos. La evidencia demuestra progreso del generador,
no identifica deforma concluyente la causa de600s ni valida elcodec completo.

`piper/` es una alternativa distinta: es_ES-sharvard, hablante1 F, ONNXCPU; añade
registroAPI/esquemas/presets, exclusión de motores yserialización de trabajos.
Piper usa solo77MB de pesos; no descarga unHFrepo completo. Build offline con
wheels fijados, fuentes yarchivo deimagen verificados. ImagenD063 siempre retenida.
El motor Base se prepara sin modelo ni grabaciones, guardado contra referencias
inventadas; su prueba real depende del propietario. La operación estable no
mantiene CustomVoice activo ni lo sustituye por una clonación ficticia.

Antes de actualizar: backup coherente y restorefueraPVE, guardar receta/lock y
cadaoverlay de la última versión estable, comprobar imagen exacta ytargets.
`piper/activate.py` y `piper/rollback.sh` son la transacción acotada con pruebaAPI
femenina/masculina, guard deBase y recuperaciónindependiente systemd. Se conserva
todo lo creado; una recuperación no borra perfiles ni muestras. Unmarcador dePASS
técnico no acredita escucha humana. El fallback deRAM3GiB queda para presión
persistente/inseguridad de recursos; tras liberar elworker la presión se normalizó
yse conserva elobjetivo7GiB expresamente autorizado. No relajar losumbrales paraQwen.
