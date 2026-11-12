# D078 — propuesta local, no desplegada

Objetivo: texto completo→Generar→un único WAV con Eduardo. Primero recuperar margen
para preparar la misma referencia; no fragmentar el texto por un fallo previo al
Talker. [Diagnóstico](../../../../docs/roadmap/PHASE7-D078-QWEN-DIAGNOSIS.md).

## Primera corrección propuesta, requiere autorización

`cache-reclaim-plan.json` enumera cinco blobs de imágenes de containerd de CT627:
1,05GiB residentes observados, candidatos a consejo `POSIX_FADV_DONTNEED`.
No contiene opción de ejecución. No se ha enviado consejo alguno ni borrado nada.

No ejecutar drop_caches global, Docker prune, memory.reclaim indiscriminado, ni
reiniciar CT/Voicebox para ocultar el problema. No tocar caché HF, referencias,
checkpoints, perfiles, bibliotecas desempaquetadas ni otros LXC.

Antes de una futura acción: verificar mismos ficheros regulares/inmutables y que no
hay inference/build/pull/export activo; medir memoria y residencia por fichero.
Aplicar únicamente tras autorización y volver a medir. La sugerencia no garantiza
recuperar todas las páginas; si no restablece margen, detener el paso dependiente.
No cambiar el umbral9,5GiB ni los demás límites.

La previsión aritmética, no una medida futura, es baseline5,30–5,44→4,25–4,39GiB y
pico observado9,70–9,78→8,65–8,73GiB si se recuperasen esos1,05GiB. Añadir preflight
predictivo basado en incremento observado≈4,25–4,48GiB y margen conservador; el
preflight actual comprueba estado instantáneo y host, pero no el coste de arranque.

## Recuperación preparada

`recovery_policy.py` solo clasifica resultados ya verificados: no crea intentos ni
lee/modifica producción. Seis tests sintéticos, sin modelos. Si hay checkpoint
íntegro/EOS/identidad coincidente y procesos parados, ofrecer solo B por acción
explícita. Ausente: informar que hace falta A nuevo, con otro UUID de intento y
vínculo al historial original; no reutilizar/borrar la carpeta anterior. Parcial o
inválido: conservar y revisar. Nunca repetir A automáticamente.

La integración debe separar generation_id y attempt_id; conservar error original,
registrar el nuevo intento de forma atómica y mostrar una acción acorde al estado
real. La existencia de un directorio no demuestra la existencia de códigos.

## Robustez posterior, separada del primer cambio

Persistir prompt de referencia completo (`ref_code`, `ref_spk_embedding`, flags ICL
más hashes/modelo/backend/dtypes), no únicamente audio ni códigos de una narración.
El cache se invalida si cambia cualquier identidad. R debe cargar solo encoder de
referencia y speaker encoder; usar la fábrica completa en R repetiría el pico.
Finalizar R antes de cargar Talker. A debe cargar únicamente Talker, sin encoder,
speaker encoder ni decoder; B sigue300/context25. Mantener FP32 y referencia exacta.

Esto requiere cargador selectivo y validación de igualdad con los componentes
oficiales; no está implementado ni declarado equivalente acústicamente. El código
instalado admite prompt reutilizable, pero su fábrica actual carga todos los
componentes: no hay un flag público que implemente esta separación.

## Próxima validación propuesta

Tras nueva autorización de mantenimiento y ensayo: verificar caché/margen real;
probar una narración continua de duración objetivo55–60s, sin dividir texto, con
telemetría alrededor de load/encode/speaker/prefill/generación/commit/decoder.
Confirmar EOS, un único checkpoint final, A terminado antes de B, WAV único,
duración real y escucha. Sin relleno, cambio de tempo ni reintentos automáticos.
No ampliar max_new_tokens1024, presupuesto900s, recursos o guardas en ese ensayo.
Si falla antes de generación, no insistir ni presentar segmentación como solución.
