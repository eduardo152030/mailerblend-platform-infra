# Fase7.4 — revisión PR15 Chatterbox

19/11/2026, Europe/Madrid. Revisión completada; corrección y validación de narración
larga **BLOCKED / CHANGES REQUIRED**. No se han ejecutado inferencias, procesado
WAV, modificado producción, fusionado, publicado comentarios, hecho commit ni push.

## Conclusión

No se puede confirmar que PR15 haya solucionado Chatterbox. Está abierto y sin
fusionar; el worker desplegado no contiene fragmentación. La idea de fragmentar
en un único worker evita el conflicto de directorios, pero este parche tiene fallos
que pueden omitir texto o aceptar audio sin comprobar EOS.

[PR15](https://github.com/eduardo152030/mailerblend-platform-infra/pull/15),
head `9505e13bea69a29b398143c01db0b42487b9e6af`.
[Evidencias](evidence/2026-11-19-pr15-chatterbox-review.json).

## Hallazgos, por prioridad

### P1 — falta la llamada que impone400tokens y EOS

En [worker, líneas78–87](https://github.com/eduardo152030/mailerblend-platform-infra/blob/9505e13bea69a29b398143c01db0b42487b9e6af/terraform/proxmox/services/infra-voicebox/candidate-d085/chatterbox_worker.py#L78),
execute deja de llamar `bounded_inference(model,stats)` y pasa directamente al bucle
model.generate. La función bounded sigue definida, pero no se instala. Por tanto,
CB.max_tokens=400 no controla la inferencia y su validación de EOS no se ejecuta.
Un test que llama a bounded manualmente sigue pasando y no detecta este fallo de
integración. Es necesario comprobar el recorrido execute→generate con dobles de
modelo, incluyendo ausencia de EOS y límite efectivo de tokens por fragmento.

### P1 — el divisor pierde texto o excede300caracteres

En [líneas21–34](https://github.com/eduardo152030/mailerblend-platform-infra/blob/9505e13bea69a29b398143c01db0b42487b9e6af/terraform/proxmox/services/infra-voicebox/candidate-d085/chatterbox_worker.py#L21),
el bucle puede alcanzar4fragmentos conservando texto residual que no devuelve.
La alternativa que añade todo el resto evita esa pérdida solo en algunos casos,
pero permite un fragmento mayor que300. Reproducción exacta de la función del PR,
extraída por AST sin importar el worker, sin Torch/modelos/audio:

| Entrada sintética | Longitud | Fragmentos | Resultado |
|---|---:|---|---|
| `('x'*249+'. ')*4+'TAIL'` | 1008 | 250,251,251,251 | Omite5caracteres finales, incluido TAIL |
| `'Hola. '*200` | 1200 | 299,300,300,301 | Supera el máximo de300 |
| Entrada del test max_chunks del PR | 45000 | 300,300,300,44100 | El test no exige máximo de tamaño |

Los dos primeros casos son válidos bajo la política1200. No se puede aceptar
un WAV como narración completa si el divisor puede descartar parte del texto.
Si4fragmentos no bastan al respetar los cortes elegidos, debe fallar explícitamente
o redistribuirlos dentro de una política definida; nunca truncar ni ignorar el cap.

### P1 — se modifica el worker antiguo, sin integrar el runtime optimizado

El PR solo cambia candidate-d085/worker y su policy, además de un test. CT627 monta
`src-input1200-3987cab-r2` y ejecuta el worker optimizado D089, SHA256
`331f12b86aff72bb3a5d1816add1ea25f7b7c98690c01e869d367e03de202d68`.
El hash coincide con el receipt activo. Ese worker no tiene `_split_text` y sí
conserva assign=True, el auxiliar chino diferido, eventos y bounded_inference.

La implementación debe portarse a validation-d089 y su política efectiva, con
manifiestos/locks coherentes, conservando las optimizaciones. Copiar el worker
antiguo del PR encima del desplegado perdería esas protecciones y su hash ya no
coincidiría con el release; fusionar Git por sí solo no despliega nada.

### P2 — persistencia y unión incompletas

La referencia se vuelve a pasar como audio_prompt_path en cada fragmento; no hay
preparación única de referencia como promete el plan. Los estados de chunks solo
se acumulan en RAM hasta el finally; un SIGKILL por guarda/timeout puede impedir
que se escriban. No hay lógica para recuperar parciales ya completados. El WAV final
se escribe directamente al nombre definitivo, perdiendo la escritura atómica previa.

`_concat_wav` no verifica igualdad de sample rate/canales ni prepara uniones o pausas.
El límite20s cambia de WAV final a cada fragmento y falta definir/documentar el
presupuesto total y medir que cabe en300s. No se acredita continuidad acústica con
un np.concatenate ni con haber definido4fragmentos.

### P2 — las pruebas no acreditan generación completa

El supuesto test de concatenación no llama `_concat_wav`: si soundfile existe,
se salta; si no existe, termina sin comprobar nada. Las clases nuevas también se
definen después de unittest.main: una ejecución directa del archivo no las recoge,
aunque discovery sí podría hacerlo. Faltan casos de pérdida de texto dentro de1200,
límites por fragmento y recorrido execute, EOS, fallo intermedio, recuperación,
cancelación y duración global. No se ejecutó aquí la suite completa ni se atribuye
un fallo al entorno: solo se reprodujo la función pura y se revisó la cobertura.

## Producción y alcance de la comprobación

Lectura SSH estricta19/11/2026 15:50:16UTC (16:50:16Europe/Madrid): Voicebox healthy,
Qwen y Chatterbox es/en ready, entrada1200, sin trabajos activos. Imagen218dc413…,
worker331f12b8…, sin chunking y todavía con400tokens. Por tanto sigue disponible el
contrato anterior para audio corto aceptado; **no se ha demostrado resuelta la
narración larga ni el PR está desplegado**.

No se solicitan nuevas generaciones para repetir un fallo conocido. Siguiente:
corregir estos bloqueos en una versión aislada del worker realmente desplegado,
con pruebas sin modelos y plan de validación controlada; después revisar autorización
para ensayo real y despliegue. No se cambian recursos, guardas, Qwen ni otros LXC.
