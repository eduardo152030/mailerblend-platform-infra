# Fase 7.4 — D078: pico de referencia, caché y recuperación de Qwen

Seguimiento: **12 de noviembre de 2026, Europe/Madrid**. Incidentes del11nov2026;
marcas UTC conservadas. **Diagnóstico DONE; corrección propuesta, NO desplegada**.
Fase7.4 IN PROGRESS; narración completa desde Voicebox BLOCKED. No inferencias,
liberación de caché, cambios productivos, recursos, guardas, borrados, commit o push.

## Conclusión prioritaria

**La guarda se alcanza antes de generar narración, mientras se prepara la referencia
real. El cambio demostrado es1,38–1,54GiB más de caché inicial del CT, no un Talker
que crece con los573caracteres.** La memoria anónima inicial y el código ML son
prácticamente iguales a D077. El modelo se carga y después su memoria residente más
los buffers de preparación se suman a esa caché; el total cruza9,5GiB y el supervisor
cancela correctamente. No fue OOM, timeout, decoder ni acumulación de tokens.

La caché adicional coincide temporalmente con el archivado de la imagen D077:
el piloto bueno precedió al archivado; la observación posterior ya mostró el nuevo
baseline alto que después reaparece en los fallos. La auditoría mincore actual
identifica1,41GiB residentes bajo containerd, **de los que1,05GiB son cinco blobs de
imagen concretos** propuestos para reclamación selectiva. No equiparar todo ese1,41
con blobs prescindibles ni declarar que cualquier página file puede liberarse ya.

La causa inmediata está demostrada por contadores y orden de llamadas. La identidad
de las páginas de cada fichero en el instante histórico no se registró: atribuir
cada byte al exportador sería más preciso de lo que permite la evidencia. Los
ficheros residentes actuales y la evolución durante el archivado respaldan fuertemente
ese origen de la diferencia. No se ha hecho la intervención causal de liberar y
repetir porque el propietario la prohíbe en este diagnóstico.

## Trabajos identificados y cronología

Texto con el prefijo solicitado,573caracteres/584bytes UTF8; ambos intentos tienen
SHA256 `c09d243905eac563e8379e6bc496a32347f3c1dc445ed577e8240baacfc47972`.
La narración completa queda privada; no se publica la transcripción de referencia.

| Intento | Historial / job privado | Inicio agente UTC | Resultado |
| --- | --- | --- | --- |
| Primero | `86dde73b-fe39-498c-ba26-658bd7849f1c` / `86dde73bfe39498cba26658bd7849f1c` |11nov21:19:04,895 |failed/talker/CT_MEMORY_9_5_GIB |
| Segundo, visible ahora | `73a3755f-5b19-4d33-aba3-79e43bf6d72b` / `73a3755f5b194d33aba379e43bf6d72b` |11nov21:20:20,369 |failed/talker/CT_MEMORY_9_5_GIB |

Son22:19 y22:20 del11nov en Madrid. Los logs API muestran POST/generate para cada
uno, retry del primero21:19:57UTC, DELETE de su historial21:20:14UTC, y retry del
segundo21:21:26UTC. El DELETE precede a D078; la auditoría no borró nada. La carpeta
privada del primer intento sigue intacta aunque su fila ya no esté en el historial.
No hay evidencia de repetición automática del modelo: son dos Generar separados;
los retries reutilizaron el ID y quedaron bloqueados antes de cargar otro worker.

En ambos jobs solo están request/text/state, events, talker-supervisor y cancel.flag.
**No hay directorio checkpoint, COMMITTED, manifest, codes.npy, parcial, release,
resultado B ni WAV.** state.json dice checkpoint_preserved=false. Decoder B no arrancó.
Ambos procesos acabaron PID0/cgroup vacío, Exit137, OOMKilled=false, contenedor propio
retirado. La señal de cancelación de la app se escribió después del fallo; no causó
la parada original, que está registrada por el supervisor de memoria.

Eventos ML únicos: `load_talker_start` y `load_talker_end`. La carga tardó2,254s en
el primero y2,406s en el segundo. No existe `reference_ready`, `talker_end` ni commit.
El código hace create_voice_clone_prompt antes de emitir reference_ready, y llama
al generador después: **tokens nuevos0, EOS de narración no alcanzado, velocidad de
generación no aplicable**. El encoder pudo haber calculado alguna representación
interna de la referencia en RAM; no está persistida y no puede recuperarse de un
proceso muerto. No confundirla con códigos de la nueva narración.

El journal del agente no tiene entradas de trabajo en esa ventana. El código guarda
estado y stdout del supervisor en archivos y descarta stderr del hijo. Los JSON
persistidos sí demuestran el motivo; faltan trazas finas encoder/speaker y debe
corregirse esa observabilidad, sin registrar voz ni transcripciones.

## Memoria comparada — misma referencia y mismo worker ML

GiB=2^30bytes. Se compara memoria muestreada con memoria muestreada; el HWM no
registrado de los procesos terminados por SIGKILL no se inventa.

| Métrica | D077 correcto | Primer fallo86… | Segundo fallo73… |
| --- | ---: | ---: | ---: |
| CT inicial total |3,896 |5,445 |5,299 |
| CT inicial anon |0,346 |0,350 |0,361 |
| CT inicial file |3,311 |4,847 |4,692 |
| CT inicial kernel |0,238 |0,248 |0,245 |
| CT máximo observado |8,141 |9,697 |9,778 |
| CT anon al máximo |4,503 |4,674 |4,794 |
| CT file al máximo |3,313 |4,690 |4,651 |
| CT kernel al máximo |0,326 |0,333 |0,333 |
| Worker cgroup al máximo CT |4,158 |4,323 |4,442 |
| Worker RSS al máximo CT |4,566 |4,523 |4,637 |
| Anon del resto del CT al máximo |≈0,36 |≈0,36 |≈0,37 |
| Swap CT/worker |0/0 |0/0 |0/0 |
| PSI local full avg10 muestreado |0 |0 |0 |
| OOM nuevos |0 |0 |0 |
| CPU media/máxima muestreada, cores |2,10/2,69 |1,15/1,94 |1,14/2,10 |
| Supervisor, segundos |130,105 |26,179 |27,217 |
| Agente, segundos |— |27,382 |28,448 |

Ejemplo segundo fallo:4,794anon+4,651file+0,333kernel≈9,778GiB. En el segundo fallo, file incluye≈3,393GiB active_file y1,256GiB inactive_file;
la separación no acredita liberación inmediata. El worker no se
aproximó a su guarda8,2GiB ni a hard9GiB; se activó la guarda del **padre CT**.
El host conservaba más de17GiB disponibles, por lo que no era agotamiento físico
del PVE. El incremento de anon ajeno al worker es pequeño: no aparece otro Qwen
residente en Voicebox ni una segunda inferencia concurrente.

**No es caché ficticia ni toda inmediatamente recuperable.** Hubo193 eventos high
en el primero y58 adicionales en el segundo, junto con escaneo/reclamación directa.
El memory.high actual, con recursos intactos, es9,921875GiB, sobre la guarda9,5;
los muestreos pueden perder picos entre lecturas. PSI avg10 redondeado0 no demuestra
presión absolutamente nula. La guarda es una comprobación periódica, no un hardlimit
instantáneo: de ahí los9,70–9,78 observados. El hardlimit CT10GiB se conserva y no
hubo OOM. Reducir anon+file en el arranque es la corrección; no ignorar file ni elevar
el umbral para dejar actuar al reclaim cerca del máximo.

El kernel documenta la contabilidad jerárquica y los controles de memoria en
[cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html); no sumar RSS y page
cache ni sumar padre e hijo como memorias independientes.

### Qué se encontró residente, sin cargar datos

`fincore/mincore`, archivos regulares≥1MiB, inode deduplicado; no lee pesos a tensores
ni trae sus páginas a RAM. Medida actual, no mapa histórico de cargos cgroup:

| Categoría | Páginas residentes |
| --- | ---: |
| HF, principalmente pesos BF16 en disco y tokenizerFP32 |2,343GiB |
| Docker, bibliotecas desempaquetadas |0,326GiB |
| containerd, contenido y snapshots |1,409GiB |
| Backups |0,119GiB |

No sumar esta tabla para sustituir memory.stat: son residencias globales por fichero,
solo archivos grandes y con reglas de cargo distintas. El modelo se ejecutaFP32;
que el archivo fuente seaBF16 es normal al convertirlo durante la carga.

La imagen se terminó de archivar a20:59:36UTC. En la observación D077, file pasó
4,319GiB a20:58:48→4,846GiB a21:01:48. El primer fallo empezó con4,847GiB. Es una
coincidencia cuantitativa particularmente fuerte con el baseline posterior al export,
frente a3,311GiB del piloto bueno antes de ese trabajo de mantenimiento.

Procesos actuales, no una fotografía retroactiva: uvicorn≈233MiB anon, dockerd≈35,
containerd≈24 y cAdvisor≈15. El resto pequeño; total consistente con el baseline.
Agente PVE≈8MiB, activo/NRestarts0. No se tocó cAdvisor ni otro LXC.

## Dónde está el pico y qué no depende del texto

Se contrastaron hashes: worker.py, runtime.py, checkpoint.py y demás código ML son
idénticos a D077. El supervisor solo cambia ROOT y una label de propiedad. Modelo,
referencia, FP32/SDPA, hilos3, checkpoint y límites son los mismos. CT3CPU por cpuset
0–2, memory.max10GiB, swap.max2GiB; workerCPU3/hard9GiB/sin swap. La app conserva
6200m/memswap6600m y la misma imagen/StartedAt desde el despliegue corregido.
Los límites del CT se leyeron en vivo; los del worker histórico se derivan del
comando de creación fijado en el supervisor, pues ya se retiró ese contenedor.

En worker.py se lee text.txt al principio, pero su variable **no se pasa a ninguna
operación del modelo hasta después de preparar la referencia**. Los573caracteres
ocupan unos pocosKiB como máximo y no se tokenizan en esa etapa. create_voice_clone_prompt
recibe únicamente audio/transcripción de referencia, que no cambiaron. Por tanto,
el tamaño de este texto no causa el pico observado. Reducirlo o segmentarlo ahora
repetiría la misma preparación y no resuelve la causa.

La función instalada codifica audio con speech_tokenizer.encode y luego extrae
speaker embedding. El loader también mantiene cargados Talker y decoder aunque no
se necesiten para esas operaciones. Desde cabeceras safetensors, sin leer pesos:

| Estado de pesos, equivalenteFP32 | Tamaño |
| --- | ---: |
| Talker y Code Predictor, proyecciones/embeddings incluidos |3,374GiB |
| Speaker encoder |33,78MiB |
| Encoder de referencia |214,52MiB |
| Decoder de audio, innecesario en esta etapa |436,11MiB |
| Total |4,043GiB |

La referencia normalizada es la misma, mono24kHz y24,8827s. Su waveformfloat32
ocupa≈2,28MiB, no variosGiB; se procesa un solo sample y no es el original estéreo
48kHz. El código conserva listas/aliases del audio y calcula códigos/embedding en
cada intento. Inference_mode y eval están activos: no hay evidencia de grafos de
autograd acumulados. Sí se retienen simultáneamente pesos de componentes que no se
necesitan al preparar referencia, incluido el decoder de436MiB.

Son bytes teóricos de tensores, no RSS medido ni workspace. El pico suma también
buffers, activaciones, librerías y asignaciones temporales. **No puede atribuirse
el último buffer a encode frente a speaker_encoder sin nueva instrumentación**:
la traza actual no delimita esas dos llamadas. Sí queda demostrado que ocurre entre
load_end y reference_ready, antes de prefill/KV de la narración. No hay prueba de
fuga ni de crecimiento proporcional a tokens porque aquí no se generó ninguno.

## Corrección concreta para volver a intentar60s continuos

### 1. Restaurar margen eliminando solo retención de caché de exportación

Propuesta local [cache-reclaim-plan.json](../../services/infra-voicebox/proposals/d078/cache-reclaim-plan.json):
cinco blobs de imágenes concretos con1,051GiB residentes. Solicitar reclamación de
sus páginas mediante POSIX_FADV_DONTNEED tras verificar que no hay export/build/pull/
inferencia activo; no borrar imágenes/archivos, no tocar modelos HF, referencia,
checkpoints o bibliotecas del runtime, y no drop_caches global.

El consejo es no vinculante: páginas ocupadas/sucias pueden permanecer. Está documentado
en [posix_fadvise](https://man7.org/linux/man-pages/man2/posix_fadvise.2.html).
No se ejecutó. Solo una medición posterior puede acreditar recuperación real.

Si se recuperasen esos1,05GiB, la aritmética del caso observado daría baseline
4,25–4,39GiB y pico8,65–8,73GiB; **previsión, no garantía**. Es el cambio mínimo
preferido para aislar el factor que difiere del piloto bueno, sin tocar el modelo,
precisión, referencia, bloques ni guardas. No repetir archivados durante el ensayo.

Añadir admisión predictiva: baselineCT+incremento de arranque observado+margen debe
caber bajo la misma guarda9,5GiB. Hoy se comprueba host/memoria instantánea, no el
coste previsto del modelo. Con baseline5,44 e incremento conocido≈4,25 ya se puede
prever9,69 antes de cargar y bloquear con mensaje útil. No modificar la guarda.

### 2. Reducir estructuralmente el pico de referencia, en cambio posterior aislado

Preparar caché privada validada del prompt completo: ref_code, ref_spk_embedding,
flags ICL y hashes de audio/texto/backend/modelo/dtype. No recortar el original ni
pasar a x-vector-only. Qwen permite reutilizar voice_clone_prompt; lo confirma el
[código/documentación oficial](https://github.com/QwenLM/Qwen3-TTS#voice-clone), y la
firma instalada acepta los mismos objetos. Guardarlo en disco y verificar identidad
es trabajo propio; no existe un flag que haga por sí solo esta optimización.

Un proceso R debe cargar solo encoder214,52MiB y speaker33,78MiB, preparar y persistir,
y terminar antes de A. A cargaría solo Talker3,374GiB y reutilizaría ese prompt,
sin encoder, speaker o decoder. B se conserva300/context25. **Mover la misma fábrica
completa a R repetiría el problema**: hacen falta loaders selectivos y validación
contra el cálculo oficial. Ahorro de pesos en A≈684MiB, más activaciones de referencia
que dejarían de coincidir; su reducción real no está medida.

El checkpoint aceptado D077 conserva los312pasos de referencia con hashes y podría
aportar ref_code, pero **no conserva ref_spk_embedding**. No permite construir el
prompt completo por sí solo; una extracción auxiliar nueva requeriría autorización.
No reutilizar los135pasos de su narración como si fueran el texto pre-market.

Instrumentar límites de carga/encode/speaker/prefill/generación y sus picos, sin logs
de audio/transcripción. Es preferible a cambiar varias cosas a la vez y atribuir
erróneamente la mejora. No se implementaron loaders ni caché reales en D078.

## Recuperación y mensajes de Voicebox

La UI envía retry con el mismo generation_id; el backend lo convierte al mismo UUIDhex
y rechaza cualquier path existente. El error es incondicional: **no comprueba ni la
existencia ni la integridad del checkpoint**. El agente sí guardó false correctamente.
El retry sobrescribe en el historial el error original de memoria por ese mensaje,
aunque state/supervisor conservan la causa. Ese ID queda bloqueado por diseño;
Generar nuevo produce otro ID, pero sin arreglar el margen vuelve a fallar.

Los dos trabajos analizados **no pueden recuperarse desde B**. Hace falta una nueva
inferencia tras corregir condiciones y acción explícita, con nuevo attempt_id ligado
al historial original. Nunca borrar la carpeta ni resetear cancel.flag para reutilizarla.
Una fila de historial no debe ser también el identificador único de cada intento.

La [política local preparada](../../services/infra-voicebox/proposals/d078/recovery_policy.py)
no inicia nada: seis tests sintéticos PASS. Propone:

- Checkpoint íntegro, EOS, modelo/referencia/texto coincidentes y procesos parados:
  ofrecer «Reanudar audio», solo B con otra salida/log y referencia al checkpointRO.
- Sin checkpoint: «No se guardaron códigos; reintentar requiere nueva inferencia».
  Acción explícita crea otro UUID de intento tras preflight; conservar intento previo.
- Parcial/dañado/incompatible: conservar y revisar, sin reanudar ni regenerar.
- Activo o sin PID0: esperar/cancelar, no lanzar otro modelo.

Conservar error original y error de última acción por separado; exponer fase,
checkpoint_status y acción posible. No repetir Talker automáticamente al refrescar
la UI, reiniciar agente o pulsar retry sin una decisión informada. Todo seguirá
siendo **texto completo→Generar→un único WAV final**, no una colección de fragmentos.

## Viabilidad continua y plan de validación posterior

No está demostrado que60s continuos sean inviables: **D076 ya emitió EOS con812pasos
acústicos, equivalentes nominalmente a64,96s**, antes de fallar en el antiguo decoder
conjunto. D077 confirmó decoder separado y voz aceptada10,8s. Falta el WAV continuo
largo completo a través de la integración corregida. No usar esta evidencia como
UAT de60s ni declarar una limitación de duración por los fallos de referencia.

Primera validación futura propuesta, solo tras autorización:

1. Aplicar únicamente corrección de caché acotada y medir margen real; si no se
   recupera, detenerse. No elevar recursos/guardas. Añadir telemetría y admisión.
2. Verificar hashes y recuperación de intentos sin lanzar modelo. Para los actuales
   informar ausencia de checkpoint y conservarlos, no aparentar Decoder resumible.
3. Un ensayo desde Voicebox con texto completo de duración objetivo55–60s, misma
   voz/modelo/parámetros y900s, sin fragmentar. El texto573caracteres no tiene una
   duración de60s garantizada: medir WAV real, no estimar éxito por caracteres.
4. Confirmar referencia_ready, prefill, tokens/códigos diferenciados, EOS, checkpoint
   íntegro, A terminado, B300 y WAV único, cancelación efectiva y límites. Detener
   en cualquier guarda, sin retry automático. Escucha de voz/texto/continuidad.
5. Si hiciera falta más margen, implementar R/cache y Talker selectivo en otra
   comparación, manteniendo FP32; no segmentar sin evidencia de inviabilidad continua.

KV-cache y hidden states son secundarios aquí: ni siquiera comenzaron. Para evaluar
más adelante, config real28capas/8KVheads/head128/FP32 da≈224KiB por posición de
cache K/V y batch1, aparte de prefill y buffers. Unos750pasos acústicos para60s
sugieren≈164MiB de KV nuevo; no una medida de esta ejecución. El core conserva
hidden states porque los usa para extraer códigos: desactivarlos ciegamente rompe
el contrato. Mantener use_cache evita recalcular todo el prefijo. No se ha aplicado
ninguna de estas modificaciones.

A velocidad observada D076/D077≈1,28–1,42tokens de secuencia/s,60s de audio es una
carga de varios minutos y900s resulta plausible, no garantizado. Para5–10min, el
límite1024 y900s actuales no bastan con esas velocidades: requeriría otro diseño y
validación. Antes de segmentar, evaluar crecimiento real de estados y retención de
capas no necesarias. Si el rendimiento CPU no sirve, considerar workerGPU con el
mismo Base/voz/FP32 y referencia privada, sin despliegue ni compra ahora. Segmentar
internamente podría acotar estados, pero no hace desaparecer el pico de referencia
ni acelera mágicamente los pasos; solo se justificaría después. De adoptarse, sería
automático con checkpoints internos y un WAV final atómico, sin trabajo manual del
usuario y con UAT específica de prosodia/pausas/continuidad.

## Estado final y evidencias

Voicebox y agente se mantienen como estaban; servicio vivo no equivale a generación
larga funcional. No se cambió producción, ningún LXC, guardas, recursos o pipeline.
Los trabajos fallidos y el checkpoint aceptado D077 permanecen conservados. No se
hicieron inferencias ni se emitió consejo de reclamación. Corrección y siguiente
ensayo pendientes de autorización; sin commit/push.

- [Jobs y estado](evidence/2026-11-12-d078-jobs.json).
- [Comparación D077/fallos](evidence/2026-11-12-d078-comparison.json).
- [Métricas originales](evidence/2026-11-12-d078-measurements.json).
- [Cronología API](evidence/2026-11-12-d078-api-events.json).
- [Caché/mincore](evidence/2026-11-12-d078-cache.json).
- [Runtime, procesos y límites](evidence/2026-11-12-d078-runtime.json).
- [Cabeceras de pesos/configuración](evidence/2026-11-12-d078-model-headers.json).
- [Conservación final](evidence/2026-11-12-d078-final.json).

Los logs completos y fuentes inspeccionadas quedan privados fuera de Git. Solo se
ha preparado código local de análisis/política y un plan de cinco candidatos, no
una operación ejecutable de limpieza o modificación del servicio.
