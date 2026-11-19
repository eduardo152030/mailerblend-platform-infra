# Fase 7.4 — D-091: corrección de PR15 y narración interna Chatterbox

19/11/2026, Europe/Madrid. Implementación y validación local; **sin despliegue ni
inferencia ML**. La aceptación de D-089 sigue limitada a las muestras allí aceptadas.
La Fase 7 global permanece IN PROGRESS.

## Hallazgos de revisión

El trabajo histórico de 361 caracteres agotó 400 tokens sin EOS. Eso demuestra
agotamiento de salida en ese trabajo, no OOM ni un umbral universal de caracteres.
La revisión del PR original identificó:

- Cambiaba `candidate-d085/chatterbox_worker.py`, mientras producción usa el worker
  optimizado de `validation-d089` (hash histórico `331f12b8…202d68`).
- Eliminaba la instalación de `bounded_inference`: desaparecía la protección real
  de 400 tokens/EOS anterior al decoder; upstream solicita 1.000 por defecto.
- El divisor podía perder la cola o superar 300 caracteres. Contraejemplos exactos:
  `('x'*249+'. ')*4+'TAIL'` y `'Hola. '*200`.
- La prueba de concatenación no ejecutaba una concatenación real. La referencia
  se preparaba nuevamente en cada llamada y faltaban manifiestos coherentes.

## Corrección implementada

Se restaura el worker histórico D-085 y sus pruebas originales. El cambio funcional
vive en `validation-d089/chatterbox_worker.py` y `chatterbox_chunks.py`:

1. Un job, un proceso, una carga FP32 optimizada `assign=True`; sin modificar Qwen.
2. Tokenizer verificado por fragmento antes de cargar pesos. Referencia original
   verificada por hash y preparada una vez con `prepare_conditionals`.
3. Hasta ocho fragmentos de 150 caracteres, con preferencia por puntuación/espacios.
   La concatenación del texto es exactamente igual al original, incluidos blancos.
   Se reserva capacidad para la cola; no se trunca texto ni se admite un fragmento
   final ilimitado. 150 es una elección conservadora, **no garantiza EOS**.
4. Cada llamada usa la referencia preparada (`audio_prompt_path=None`), 400 tokens
   y EOS obligatorio antes del decoder. No hay reintentos automáticos.
5. WAV mono PCM16, 24 kHz, máximo 20 segundos **por fragmento**. Un WAV final, con
   pausas explícitas de 50 ms entre fragmentos y máximo agregado de 80 segundos.
   Esta propuesta cambia la semántica de duración final del candidato; producción
   conserva su límite anterior hasta otro despliegue autorizado. La continuidad
   acústica y la naturalidad de las pausas siguen sin validar.
6. Presupuesto **global** de 300 segundos, no 300 por fragmento. Se conservan
   supervisor externo, cancelación, exclusión mutua, hard 8 GiB, parada 7 GiB y
   guarda CT19 GiB. No hay cambios de recursos, pesos, precisión o efectos.
7. El supervisor candidato distingue OOM confirmado por Docker, error EOS del
   resultado y salida con causa desconocida; no etiqueta toda salida como OOM.

## Persistencia, fallos y recuperación

El job persistente contiene `chatterbox-chunks/manifest.json` y `000.wav`, etc.
El manifiesto guarda identidad de modelo/referencia/backend/política, índice,
longitud y SHA256 del texto, estado, frames, frecuencia,
SHA256 del WAV, tokens y EOS; no copia la grabación ni los embeddings privados.
Cada fragmento completo y manifiesto se escribe mediante temporal, fsync y rename.
El WAV final se publica únicamente cuando todos los fragmentos son válidos y están
ordenados. Se comprueban formato, muestras finitas, duración e integridad.

Un fallo preserva fragmentos y resultado, sin publicar audio incompleto. La presencia
del directorio impide repetir el job implícitamente. **No se implementa reanudación
automática ni una API de recuperación**: las piezas completas quedan disponibles
para diagnóstico o recuperación explícita futura, tras verificar identidad, hashes
y autorización. SIGKILL puede dejar un fragmento `running`; no debe aceptarse como
completo. Los checkpoints Qwen nunca se leen como artefactos Chatterbox.

## Validación y reproducibilidad

Entorno local Python 3.12, numpy1.26.4, soundfile0.13.1, cffi1.17.1,
pycparser2.22 y PyYAML6.0.2. Suite Voicebox completa: **92 PASS**; UI: **9 PASS**. WAV sintéticos reales,
sin torch instalado, pesos ni referencia personal. Pruebas de división aleatoria,
contraejemplos, orden y pausas, checksum, formato, EOS, cancelación, timeout,
duración, conservación tras fallo y orquestación del worker con modelo simulado.
El fixture D089 aísla imports para no reutilizar accidentalmente `engine_policy`
de D085. Se amplía readiness para exigir también el módulo de fragmentación.

Los hashes objetivo en `source-lock.json` y `deployment-lock.json` reflejan el
candidato. Se conservan `original_*`, evidencias D089, modelo, referencia y digests
OCI históricos. El nuevo supervisor se incluye en el overlay objetivo. Las recetas
históricas D089 conservan precondiciones de su despliegue original: **no ejecutar
`deploy.py` directamente sobre producción actual**; se requiere una transacción
nueva con baseline real, backup y rollback antes de un despliegue futuro.

## Siguiente paso y límites de la conclusión

Tras revisión y fusión autorizadas, preparar un despliegue acotado con backup,
readiness y rollback. Solo después de autorización de ese alcance, probar primero
un texto que requiera dos fragmentos y luego la narración de trading, una vez cada
uno. Registrar tiempo total, EOS por fragmento, RAM y calidad acústica. Los 1.200
caracteres son admisión de entrada: **no está demostrado que quepan en 300 segundos**.
No declarar que la narración larga funciona por haber pasado pruebas sintéticas.
