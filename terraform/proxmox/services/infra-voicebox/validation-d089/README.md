# D-089 — validación aislada y producción

Estado vigente tras reanudación autorizada: Chatterbox es/en disponible, inglés
validado una vez por API; aceptación acústica pendiente. Véase `resume/README.md`
y el informe D089. La parada descrita más abajo es antecedente histórico.

Fase7.4. Esta receta no habilita Chatterbox automáticamente.

El worker reutiliza exactamente `load_probe.py` y `telemetry.py` de D088, FP32,
assign=True y auxiliar chino diferido. Añade ejecución TTS original, eventos de
referencia/tokens/decoder, límite400tokens/EOS obligatorio, validación WAV y SHA.
No incluye grabación ni transcripción. `source-lock.json` fija el código candidato,
controles productivos existentes, modelo, entorno y huella de referencia.

`supervise_isolated.py --execute-once` se ejecuta en PVE con SSH estricto y solo
tras suite completa PASS y autorización. Usa la misma exclusión y funciones de
preflight/parada productivas, Docker cgroup v2, CPU3, RAM8GiB/swap0, stop7GiB,
CT19GiB,300s. Montajes venv/modelos/referencia/source RO y job privado RW.
Marca `started.json` impide repetir el ensayo; conserva contenedor parado, logs,
eventos y resultados. No elimina ni mueve cachés/modelos. Cancelación mediante
señal al supervisor o `job/cancel.flag`; no liberar lock hasta PID0/cgroup vacío.

Preparación privada CT: `/srv/voicebox/validation-d089/{source,job}`.
No compartir `job` ni montar el conjunto de datos de producción: solo WAV de
referencia original RO. Evidencias y fuentes externas: `/mnt/storage/d089` en PVE.

Tests: la suite completa se monta RO en `/suite`, mismo digest Docker del worker
y venv fijado en `/cb/venv`. Ejecutar `/cb/venv/bin/python -m unittest discover
-s tests/voicebox -p 'test_*.py' -v`, UID999, red ninguna y sin modelos/referencia.
Reproducir readiness estable por separado y conjuntamente; el fixture usa import
por identidad de archivo para evitar el módulo legado retenido por otros tests.

El despliegue no está autorizado por el simple PASS de los tests: depende del
resultado real y del margen medido durante generación y decoder. Ante fallo,
detenerse, conservar evidencias y Qwen operativo; no reintentar automáticamente.

Resultado de esta intervención: ambos WAV españoles válidos/idénticos, pero
observador local perdió ruta. STOP, inglés no ejecutado, receipt deshabilitado.
Overlay instalado, Qwen intacto; no reactivar automáticamente. Informe D089 en
`docs/roadmap/PHASE7-D089-CHATTERBOX-PRODUCTION-VALIDATION.md`. No usar
`--action verify` esperando enabled=true sobre el estado final deshabilitado.
El helper final distingue generación Qwen ajena activa de un residuo Chatterbox.
