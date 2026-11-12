# Fase 7.4 — D-070: cancelación Qwen y alternativas CPU

Intervención iniciada el 10 de noviembre y verificada el **11 de noviembre de 2026,
Europe/Madrid**. Cancelación/recuperación y comparación: **DONE**. Narraciones largas
con Qwen: **BLOCKED**. La muestra corta aceptada en D069 conserva esa aceptación.
No se ha desplegado, descargado ni cargado ningún motor nuevo.

## Generación diagnosticada y cancelación

Trabajo `d7ce3d31-fa43-4cd8-bd44-0b990ac53da2`, perfil Eduardo — Mi Voz
`1fd00418-2a79-4178-883f-af6c3f5e07ee`, Qwen Base 0.6B, texto de 896 caracteres.
La duración aproximada de 55 s es la intención del propietario; **no existe un WAV
completo que permita verificar esa duración**.

Las marcas históricas siguientes son **UTC** del 10 de noviembre:

| Evento | Evidencia |
|---|---|
| Inicio | 21:30:06.218803Z, registro de generación |
| Encode de referencia | 2,637 s, finalizado a21:30:09.029590Z |
| Prompt completo | 22,531 s, finalizado a21:30:28.920309Z |
| Entrada a generación de tokens | 21:30:28.927792Z, sin evento de salida antes de cancelar |
| Cancelación API registrada localmente | 21:50:02.790622Z, aproximadamente20min después del inicio |
| Reinicio autorizado solo Voicebox | StartedAt21:52:36.871049Z |

La API respondió `Generation cancellation requested`, y el historial pasó a
`failed` con `Generation cancelled`. Sin embargo, la medición posterior mostró
**1,972 núcleos ocupados**, RSS3.789.548 KiB, cgroup aproximadamente4,67 GiB y
swap de 55.382.016 bytes, sin OOM. No se confundió la respuesta HTTP con la parada física.

El código real de `services/task_queue.py` cancela la tarea asyncio, mientras que
`backends/pytorch_backend.py` ejecuta la inferencia bloqueante mediante
`asyncio.to_thread`. Cancelar la espera no mata ese hilo nativo; se observó exactamente
ese desacoplamiento. El backend no propaga un evento de cancelación a generación de
tokens/codec. La librería instalada admite por defecto hasta 2048 tokens nuevos.
Eso no demuestra que se hayan generado 2048 ni que fallen las condiciones EOS:
**no se midió el contador de tokens de este trabajo**.

Se localiza el tiempo dentro de la generación autorregresiva, después de extraer
la referencia y antes de convertir el resultado al WAV. No hay prueba de fallo de
la grabación, OOM, ni de un deadlock concreto; CPU alta indica cómputo persistente.
No se repitieron pruebas largas para intentar distinguir bucle de generación y
rendimiento insuficiente. Se documenta la causa demostrada de la cancelación
incompleta, sin atribuir una causa numérica no observada al generador.

Al no disponer de parada aislada segura, se solicitó y obtuvo autorización expresa
para **reiniciar únicamente el contenedor Docker Voicebox**. Se conservó su imagen,
ID, mounts, base de datos, perfil y referencias. CT627 no se reinició. No se intentó
inyectar excepciones, matar hilos con herramientas de depuración ni intervenir otros
servicios. Antes se guardó un snapshot SQLite consistente y copia de referencias y
originales; los backups completos D069 se conservaron.

## Estado real tras la recuperación

Comprobación del **11 nov 09:39 CET**: API healthy, cero trabajos activos, Qwen sin cargar.
Tres ventanas de5 s:

| Medida | Resultado |
|---|---|
| CPU del proceso Voicebox | 0–0,002 núcleos, prácticamente reposo |
| CPU del cgroup completo | 0,0055–0,014 núcleos, incluye exporters y tareas del CT |
| RSS de Voicebox | 394.296 KiB, aproximadamente385 MiB |
| Memoria cgroup | 2.048.360.448 bytes, aproximadamente1,91 GiB; incluye caché y otros procesos |
| Swap cgroup | 80.887.808 bytes, aproximadamente77,14 MiB, estable en las tres ventanas |
| VmSwap de Voicebox | 32.000 KiB,31,25 MiB |
| OOM / OOM kill | 0 / 0 |
| UptimeCT | 65.030,28 s; continúa el arranque anterior, no un reinicio del LXC |

La swap no es cero. La medición de la mañana refleja páginas inactivas tras la
noche; no se atribuye todo su cambio respecto a la tarde al acto de cancelar.
Los eventos `memory.max` acumulados113728 son reclamación/límites anteriores,
noOOM; permanecen sin nuevos OOM. No se amplió RAM, CPU, disco ni swap.

Un único perfil y una referencia siguen presentes. Referencia y grabación original
se verificaron idénticas por SHA256 contra D069, sin publicar sus hashes ni contenido.
Imagen `sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b`,
mismo contenedor `68ecf2b01961696f7db2f452a7450ae0a74abe27fd0658de8a4e170df03da8b4`.
La identidad y configuración PVE de627 y las26 configuraciones ajenas mantienen
los hashes de la auditoría D069: ningún otro LXC modificado.

## Kokoro y Piper conservados y comprobados

Pruebas **breves de presets**, usando la imagen y pesos existentes, en helpers
secuenciales, sin red, sin escribir el volumen de datos y con límite de 1.400 MiB y 2 CPU.
No usaron ni imitaron el perfil personal y no crearon perfiles. Los WAV de diagnóstico
son privados y no se presentan como voz del propietario.

| Motor | Audio real | Generación observada | HWM RSS del helper |
|---|---:|---:|---:|
| Kokoro / em_alex | 2,58 s,24kHz | 8,09 s | 1.377.083.392 bytes,1,28 GiB |
| Piper / es_ES-sharvard F | 2,11 s,22,05kHz | 2,16 s | 417.050.624 bytes,0,39 GiB |

Los helpers terminaron y fueron retirados automáticamente. Los intentos iniciales
fallaron en preparación del helper por entrypoint que exigía volumen escribible,
PYTHONPATH y cacheHF del usuario; se corrigió el entorno del helper, **sin cambiar
permisos de producción ni descargar pesos**. Los resultados de la tabla pertenecen
únicamente a los dos ensayos completos. No se mide con ellos la velocidad de un
minuto ni clonación. Kokoro y Piper por sí solos no reproducen la voz personal.

Monitorización:59 targets con los mismos labels/URLs y UP, sin FIRING/PENDING. No se
cambiaron targets, reglas, Grafana ni otro LXC. No se ha modificado el pipeline.

## Comparación de alternativas: datos frente a presupuesto

Se revisaron documentación y código primarios y metadatos de archivos. **No se
instalaron dependencias ni se descargaron checkpoints alternativos.** MB/GB de
la tabla son bytes decimales de archivos; GiB son presupuestos de memoria. Pesos
en disco no equivalen a RAM: framework, copias durante carga, buffers y caché cuentan.

Los techos de worker siguientes son **propuestas de prueba**, no requisitos oficiales
ni consumos medidos. Ninguna alternativa tiene aún un benchmark de 1 min en CT627.
No se promete una velocidad concreta extrapolando GPU, otrosCPU o muestras breves.

| Opción | Voz personal/español y CPU | Archivos principales verificados | RAM y límite de 7 GiB | Tiempo para1min / valoración |
|---|---|---:|---|---|
| **OpenVoiceV2 + MeloTTS español** | Conversión de timbre desde referencia real; ejemplo oficial español y CPU. Ritmo y pronunciación nacen del TTS fuente: parecido y acento deben escucharse | Converter131,32 MB + Melo ES207,86 MB =339,18 MB; más watermark/tokenizadores/runtime | Proponer worker≤3 GiB, etapas secuenciales y fragmentos cortos. Es la ruta con mejor margen por pesos; RAM real pendiente | Melo anuncia tiempo real enCPU, sin benchmark de nuestra cadena completa. **Primera candidata**, no rendimiento garantizado |
| **Piper/Kokoro → OpenVoiceV2** | Conversión a timbre personal reutilizando síntesis existente; integración distinta del ejemplo oficialMelo | Añade converter131,32 MB más auxiliares; pesos TTS ya presentes | Mismo techo inicial≤3 GiB y liberar etapaTTS antes de convertir | Menos descargas, pero se debe extraer embedding del hablante fuente correspondiente; no reutilizar sin más el embeddingMelo. Segunda variante si el acento del fuente resulta adecuado |
| **XTTS-v2** | Clonación directa multilingüe, español y rutaCPU; referencia real existente válida como entrada candidata | model.pth1.867,93 MB; vocab/config y auxiliares aparte | Proponer techo inicial4,5 GiB con auditoría de carga; copias y activaciones podrían impedirlo. Viabilidad7 GiB no demostrada | Autorregresivo: no hay evidencia de minuto rápido con 3 vCPU. Priorizar si la conversión pierde identidad/acento; requiere probar consumo y latencia |
| **Chatterbox MultilingualV3** | Español y cargaCPU explícita; condicionamiento de hablante, no confundir con Turbo/Nano ingleses | T3 v3+S3Gen + VE aproximadamente3.206,85 MB, sin duplicar formatos ni versiones | La carga ingenua mantiene state_dict y parámetros; margen7 GiB incierto y riesgo de picos. No es la primera opción | Sin benchmarkCPU aplicable. Además suREADME actual declara proyecto retirado/sin mantenimiento; coste de integración y soporte mayor |
| **Qwen Base 0.6B actual** | Parecido aceptado para muestra corta, no para narración larga | Ya descargado, snapshot fijadoD069 | D069: cgroup observado5,18 GiB. Este trabajo largo no causóOOM, pero consumíaCPU sin terminar | Muestra6,4 s/106,86 s y trabajo largo cancelado tras~20min. **No repetir largos por ahora** |

OpenVoice/Melo y Chatterbox publican MIT; XTTS tiene Coqui Public Model License,
distinta de la licencia de la librería. Revisar sus condiciones antes de elegirlo;
no se da por equivalente a MIT. No se propone cuantización no integrada como si
estuviera validada en nuestro fork. LuxTTS y ChatterboxTurbo/Nano rápidos no se
promueven como solución española validada: sus tarjetas/modelos consultados se
identifican como ingleses. Entrenar una voz Piper propia requiere otro conjunto de
datos/proceso; la grabación actual no demuestra que ese entrenamiento sea viable.

### Datos concretos que cambian el presupuesto

Melo ES tiene `disable_bert:true` en su configuración: no debe presupuestarse un
modelo BERT en inferencia sin comprobar el camino real. Su fonemizador sí utiliza
un tokenizador español. Los imports multilingües y dependencias antiguas deben
revisarse para impedir descargas implícitas de idiomas/modelos no usados.

OpenVoice ofrece `ToneColorConverter.extract_se` directamente sobre referencias;
para este perfil con audio ya validado puede investigarse ese camino sin añadir
ASR indiscriminadamente. Su demo usa otra ruta con VAD; se debe medir y documentar
la extracción elegida. Los auxiliares de watermark y resample44,1→22,05kHz también
cuentan:339 MB son un mínimo de checkpoints principales, no el paquete completo.

El runtime actual es Python 3.12 / PyTorch 2.8. Las requirements de OpenVoice fijan, entre
otros, NumPy 1.22 y dependencias antiguas. **No ejecutar pip install sobre Voicebox
estable**: una candidata aislada debe resolver versiones y fijarlas. No se afirma
compatibilidad automática con nuestrofork por compartir PyTorch.

## Recomendación y propuesta, no despliegue autorizado

**Priorizar un piloto aislado de OpenVoiceV2 + Melo ES**, sin cambiar recursos ni
perfil de producción, conservando Kokoro y Piper. La variante con fuentePiper puede
reducir descargas, pero necesita validar el embedding fuente y el acento. Si el
parecido no es aceptable, revisar XTTS-v2 con presupuesto de carga antes de ensayarlo.
No recomendar aumentar RAM ni insistir en Qwen largo con los datos actuales.

Propuesta para revisión antes de descargar/desplegar:

1. Fijar repositorios, revisiones, licencias, dependencias y lista mínima de pesos;
   comprobar disco y margen del host. Runtime separado y rollback de imagen/datos.
2. Worker por trabajo, con PID/cgroup y plazo; cancelación que termine ese worker,
   sin reiniciarAPI ni CT. `asyncio.cancel()` por sí solo no satisface esta condición.
3. Techo inicial3 GiB porworker, CT≤7 GiB y mismas protecciones de cgroup6,5 GiB,
   swap+64 MiB,OOM y presión del host. No forzar carga si el preflight contradice
   ese presupuesto; no subir límites automáticamente.
4. Extraer la identidad de la grabación real, sin perfiles ficticios ni terceros.
   Generar una frase corta; revisión del propietario de parecido, acento y texto.
5. Solo después,15–20 s y~60 s. Objetivo propuesto: minuto en≤120 s en caliente y
  ≤180 s desde frío, midiendo por separado carga, extracción, síntesis/conversión,
   RSS/cgroup/swap/OOM y cancelación real. Son criterios deseados, **no resultados**.
6. Aprobación de la candidata antes de incorporarla a Voicebox. Pipeline permanece
   fuera de alcance. No migrar automáticamente el perfil ni sustituirlo por un preset.

## Backups, evidencias y siguiente paso

Snapshot privado `/opt/voicebox/backups/d070-cancel`: SQLite y referencia/original/
transcripción, verificado antes de reiniciar el servicio; copia fueraPVE y
restauración aislada de4 archivos con integridadSQLite. Los backups completos D069,
modelos y volúmenes permanecen. Logs y referencias personales no se publican.

[Recuperación/CPU/memoria](evidence/2026-11-11-d070-recovery.json) ·
[Backup](evidence/2026-11-11-d070-backup.json) ·
[Kokoro](evidence/2026-11-11-d070-kokoro.json) ·
[Piper](evidence/2026-11-11-d070-piper.json) ·
[Monitorización](evidence/2026-11-11-d070-monitoring.json) ·
[Metadatos, sin descarga](evidence/2026-11-11-d070-model-metadata.json).

**Fase 7.4 IN PROGRESS para narración personal de un minuto; Qwen largo BLOCKED.**
D070 termina diagnóstico, recuperación y comparación; D069 conserva la aceptación
limitada de su muestra corta. Siguiente: revisar la candidata propuesta antes de
cualquier nuevo despliegue. Sin commit ni push.

## Fuentes primarias consultadas

- [OpenVoice API/CPU y extractor](https://github.com/myshell-ai/OpenVoice/blob/main/openvoice/api.py),
  [demo V2 con Melo español](https://github.com/myshell-ai/OpenVoice/blob/main/demo_part3.ipynb),
  [requirements](https://github.com/myshell-ai/OpenVoice/blob/main/requirements.txt).
- [Melo CPU y español](https://github.com/myshell-ai/MeloTTS),
  [configES](https://huggingface.co/myshell-ai/MeloTTS-Spanish/blob/dbb5496df39d11a66c1d5f5a9ca357c3c9fb95fb/config.json),
  [selecciónBERT](https://github.com/myshell-ai/MeloTTS/blob/main/melo/utils.py).
- [PesosOpenVoiceV2](https://huggingface.co/myshell-ai/OpenVoiceV2/tree/f36e7edfe1684461a8343844af60babc2efbb727),
  [pesosMelo ES](https://huggingface.co/myshell-ai/MeloTTS-Spanish/tree/dbb5496df39d11a66c1d5f5a9ca357c3c9fb95fb).
- [XTTS oficial mantenido por Idiap](https://coqui-tts.readthedocs.io/en/latest/models/xtts.html),
  [archivosXTTS](https://huggingface.co/coqui/XTTS-v2/tree/6c2b0d75eae4b7047358e3b6bd9325f857d43f77).
- [Chatterbox modeloCPU multilingüe](https://github.com/resemble-ai/chatterbox/blob/master/src/chatterbox/mtl_tts.py),
  [README y variantes](https://github.com/resemble-ai/chatterbox),
  [archivos](https://huggingface.co/ResembleAI/chatterbox/tree/5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18).

## Cierre de verificación

Auditoría posterior a los helpers: 2026-11-11T08:50:51.819525+00:00 (UTC). CPU Voicebox máximo 0.0020 núcleos en las ventanas; RSS 234.43 MiB, cgroup 1.60 GiB y swap 228.09 MiB. Sin OOM, sin trabajos activos, perfil y referencias intactos.
La tabla anterior describe la medición inicial de recuperación; la caché del cgroup
puede variar tras leer modelos en los helpers. Las cifras no son RAM de un motor nuevo.
[Auditoría inicial](evidence/2026-11-11-d070-initial-recovery.json) ·
[Auditoría final](evidence/2026-11-11-d070-recovery.json).

Compilación de los scripts de diagnóstico, enlaces locales, JSON y
`git diff --check`: PASS. No se añadieron tests de una inferencia alternativa no
ejecutada ni se presentaron metadatos como un benchmark.

La swap del cgroup aumentó entre las lecturas inicial y final, de77,14 a228,09MiB,
mientras bajaba RSS del proceso. No se atribuye ese cambio a una causa única sin
perfilado. En los15s finales de CPU y otra ventana de10s se mantuvo en239.165.440bytes,
con PSI full del CT0,00. El host mostró actividad global (PSI fullavg10 final1,13%,
unos8,48GiB disponibles); no se modificó ningún servicio ajeno ni se agotó memoria.
No se describe la swap como cero ni estable durante toda la intervención, únicamente
en las ventanas observadas. [Control final](evidence/2026-11-11-d070-swap-check.json).
