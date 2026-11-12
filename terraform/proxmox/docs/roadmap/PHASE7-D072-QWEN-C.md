# Fase 7.4 — D-072: Qwen Base 0.6B C/BLAS aislado

Estado: **diagnóstico y piloto acotado DONE; motor/narración BLOCKED, sin aceptación**. 11nov2026, Europe/Madrid.
Autorización: D072 del propietario, sin sustitución productiva ni aceptación implícita.

## Compatibilidad verificada

Motor [gabriele-mastrapasqua/qwen3-tts](https://github.com/gabriele-mastrapasqua/qwen3-tts),
commit `ef339be58a778b062e1c14382347964552eae007` (25sep2026UTC), fuente fijada
por SHA256 en `services/infra-voicebox/pilot-d072/source-lock.json`. MIT; motor
comunitario independiente, actividad observada1105commits, sin garantía de soporte.
Base0.6B oficial Apache2.0; no se utiliza CustomVoice ni graft ni otras identidades.
[Modelo y licencia](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base).

Linuxx86_64, i5-6500 Skylake, AVX2/FMA reales; no AVX512/VNNI/BF16 nativo/AMX.
Compilación `make blas SIMD=portable -j2`, GCC12/OpenBLAS0.3.21; self-test PASS.
INT8 en Talker y CodePredictor; BF16 original convertido a INT8 en carga. Códec
originalFP32 y operaciones auxiliares no se convierten enteramente aINT8. AVX2
resuelve widen/dequant+FMA; prefill convierteBF16→FP32+SGEMM. No se atribuye
rendimiento VNNI/AMX ni benchmarksM1 a estei5. INT4 existe en código, pero exige
validación real de precisión/ruta y calidad; el help todavía dice1.7B-only.

Pesos ya persistentes reutilizados solo lectura, snapshotBase
`5d83992436eae1d760afd27aff78a71d676296fc`:
modelo1.829.344.272B,478tensoresBF16; códec682.293.092B,496tensoresFP32.
Descargar/mmap/cargar/generar son etapas distintas. No descarga nueva de modelos.
Carga mmap no equivale a RSS y se contabiliza además cgroup/cache/transitorios.

## Referencia y aislamiento

Perfil `1fd00418-2a79-4178-883f-af6c3f5e07ee`, Eduardo — Mi Voz, sin cambios.
Referencia `8840f5e1-990b-463e-b94e-e72beef61917`, SHA256
`7b388a917fb98bdf6b251454e04e7adc511faec42d21797f103ce539fc167dd4`.
PCM16 mono24kHz24,882667s, transcripción425caracteres confirmada por el dueño y
contrastada con SQLite en solo lectura. Copia privada persistente0700/0600 fueraGit;
no texto de referencia ni grabación en este informe/repositorio.
Ruta ICL completa `--ref-audio`+`--ref-text`, no xvector-only predeterminado. El motor
recorta internamente0,59s de cola; archivo de entrada y transcripción invariables.

Producción permanece D069, sin reinicios/modificación de imagen/perfil/volúmenes.
OpenVoice parado; health informa ningún modelo residente ni trabajos activos antes
de iniciar. CT627 conserva3vCPU/7168MiB/512MiBswap/50GiB. Piloto oneshot sin red,
usuario999, referencia/cacheRO, rootFSRO, cap-dropALL, no-new-privileges. Worker
techo5GiB sin swap y3CPU, hilos2. No inferencias simultáneas.

Supervisor externoPVE: timeout corto240s, parada soloDockerpiloto,2s de gracia y
kill/recolección Docker. Cortes: CT6,25GiB,worker4,75GiB,swapCT+64MiB, OOMnuevo,
host disponible<1,5GiB oPSIfullavg10≥2% sostenido10s. Preflight exige6GiB disponibles
yPSI<2%; la tolerancia sostenida se fija antes de probar, no tras un veto. Observa
RSS agregado, eventos/cpu/memoria/swap del worker yCT, disponibilidad/PSI del host.
No cambia otrosLXC ni pipeline. Esto es piloto CLI, no cualificación de servidor.

## Comparación histórica

| Motor | Resultado medido anterior | Fidelidad |
|---|---|---|
| Qwen oficial, PyTorch BF16/SDPA, Base0.6B | D069:6,40s audio/106,86s; HWM4,68GiB,CT5,18GiB; D070~20min sin WAV largo | Muestra corta aceptada por propietario |
| OpenVoiceV2+MeloES | D071:7,37s/34,26s y15,39s/74,20s; hijoRSS~2,38GiB; minuto detenidoPSI | Propietario rechaza muestra369ebd31 |
| Qwen C/BLAS INT8 | Ensayo aislado en curso | Pendiente escucha; no ganador declarado |

Textos/rutas/versiones diferentes: estas filas no prueban una aceleración normalizada.
OpenVoice se conserva parado; no se sigue optimizando como solución principal.

## Integración futura, sin implementar

Preferencia propuesta: worker independiente con API interna y proceso cancelable
por trabajo, cola limitada y un motor residente máximo. Adaptador Voicebox conserva
perfilUUID, API, historial, descargaWAV y persistencia; almacena únicamente resultados
completos, con estados failed/cancelled distinguibles. Referencias privadasRO y lock
de modelo/motor, métricas CPU/RSS/cgroup/swap/OOM/tiempos, backup/rollback coordinado.
DockerCompose versionado, sin puertos públicos del motor y límites explícitos.
Alternativa integrada exige bindings C/gestión de memoria y puede volver a mezclar
cancelación e inferencia con API; mayor acoplamiento al fork. El servidor C ofrece
rutas OpenAI y streaming, pero no se presupone compatibilidad con contratoVoicebox
ni aislamiento de cancelación: requieren pruebas separadas antes de integración.
Ninguna de estas opciones se despliega con esta preparación.

## Resultado real INT8 y decisión

**Sin WAV; no se continúa.** Una sola prueba con el texto exacto solicitado,
semilla42 y referencia completa ICL. Carga interna5,738s; referencia303frames,
prefill467posiciones/6,357s; último progreso50frames (~4s de códigos, no audio
decodificado). Corte de seguridad a122,953s; supervisor127,662s incluyendo
parada. No se alcanzó timeout240s. No audio reproducible, duración final/RTF/
tiempo de generación completa no disponibles. No pruebaINT4/BF16 ni15/30/60s.
No enlaces nuevos a muestras porque no existe WAV; no presentar códigos como audio.

| Medición observada | Resultado |
|---|---:|
| RSS agregado máximo muestreado | 3.969.597.440B /3,697GiB |
| Cgroup worker máximo muestreado | 3.985.432.576B /3,712GiB |
| Cgroup CT627 máximo muestreado | 5.469.765.632B /5,094GiB |
| Swap worker | 0 |
| SwapCT inicial→máximo | 54.067.200→64.667.648B, +10,11MiB |
| CPU worker pico por intervalo | 1,846núcleos |
| Host disponible mínimo | 7.219.187.712B /6,72GiB |
| PSIfullavg10 host máximo | 9,10% |
| OOM/oom_kill nuevos | 0/0 |
| Parada Docker piloto, tiempo supervisor | 3,406s |

RSS incluye wrapper+procesoC; muestreo no sustituyeHWM del proceso abortado.
No hay medida separada concluyente de RAM de carga frente a incremento exclusivo
de inferencia; la evidencia registra serie temporal privada y máximos observados.
El límiteDocker5GiB y umbralworker4,75GiB no se alcanzaron. Veto por presión global
sostenida del host, pese aMemAvailable alto; no demuestra que Qwen exceda7GiB.
Tampoco acredita ausencia de impacto transitorio sobre otros servicios:59targetsUP
prueban disponibilidad, no sus latencias. No atribuir la causaPSI a otroLXC sin
medición causal. PSI posteriorCT0,00% yhost0,03%avg10 en comprobación posterior.

Cancelación efectiva: contenedor únicamente del piloto, PID0,Runningfalse,
ExitCode137 por kill controlado,OOMKilledfalse; no hilo residual ni reinicioCT
oVoicebox. Imagen candidata `sha256:03dadc9a464031613f05080d0d860749fe4a696bd5d0583da41d93edf226a305`,
binarioSHA256 `04f4bce57f28449bb485e5ec9d6acf80d846851b1e08ffa9f885878241318de6`.
`--caps` muestra build/source unknown porque la fuente se obtuvo como archivo;
la procedencia se fija externamente por commit+SHA de archivo ybinario, sin afirmar
una identificación embebida inexistente. Despacho de arranque registrado, ejecución
real confirma Talker/CPINT8 y presupuesto2hilos/BLASserial+partitioned. No campaña
SOAK ni servidor productivo; no convertir este CLI en cualificación de streaming.

## Producción y riesgos pendientes

Voicebox healthy, imagenD069exacta,0jobsactivos/model_loadedfalse, perfil único
conservado. Hashes de referencia y original verificados, configuracionesPVE
idénticas al baseline. En ventana5s posterior CPUCT0,00247núcleos,
cgroup3.370.291.200B yswap64.520.192B: memoria incluye caché de archivos retenida;
no inferenciaC residente. No afirmar que toda la caché sea fuga de memoria.
Kokoro/Alex helperoffline:2,58s/8,745s; Piper2,113s/2,029s, ambosPASS después
del corte y secuencialmente, sin crear perfiles ni modificarAPI/historial.

59targetsUP. Aparece **HostDiskFilling CT627, warning/PENDING**,14,43% disponible
en consulta; `df`7,1GiB libres/49GiB. La compilación deja imagen/caché/contexto
adicionales; el disco ya tenía8,4GiB antes. No ocultar esta regresión ni declararlo
sin alertas. No borrados de imágenes/backups/modelos/datos ni limpieza global.
Antes de otro build, preparar limpieza acotada autorizada de artefactos prescindibles
con imagen candidata exportada/verificada fueraCT; revisar espacio recuperable real
porque capasBuildKit compartidas no equivalen a bytes recuperables.

**Recomendación: optimizar y diagnosticar más, sin integrar ni descartar Qwen por
RAM.** El C/INT8 carga y comienza ICL dentro del límite observado, pero no demuestra
WAV ni rendimiento útil. Priorizar atribuciónPSI con series host+CT/IO/swap, espacio
de disco y contabilidad por etapas. Propuesta posterior: ventana de host estable,
cache privada del prompt ICL si conserva fidelidad y soporteBase0.6B verificados,
y revisión de buffers/códec/prefill; sin cambiar referencia ni usar xvector-only
para prometer el mismo parecido. No ejecutar nueva carga por este cierre.
El motor principal sigue pendiente de validación: OpenVoice rechazado; muestra
QwenD069 aceptada solo para aquel audio corto. La elección de calidad requiere
WAV nuevo y escucha del propietario, nunca se decide por RSS o documentación.

Muestras históricas, sin nueva aceptación implícita:
[Qwen D069 aceptada](http://192.168.1.127:17493/audio/925f8b71-6ad7-46f0-a48a-ffa3881004ef),
[OpenVoice D071 rechazada](http://192.168.1.127:17493/audio/369ebd31-937b-4fe4-b21d-13ce48b972d6).
Comparación técnica oficial: [QwenLM](https://github.com/QwenLM/Qwen3-TTS);
PyTorch CPU real del fork y resultados medidos se documentan en D069/D070.

## Evidencias y reproducción

Código aislado: `services/infra-voicebox/pilot-d072/` (Dockerfile, lock, preparación
privada verificada, wrapper y supervisor). No aplicación al Compose productivo.
Para repetir se exige revisar capacidad/PSI/espacio, preparar un label nuevo y
request privado, y mantener los mismos checks; no repetir este ensayo detenido
automáticamente. Contenedor fallido conservado parado para auditoría, sin red.
Fuentes originales y mediciones detalladas privadas fueraGit. Se compiló Python
de los scripts, self-testC PASS, diff--check y enlaces locales comprobados.

- [Manifiesto de ejecución CLI](evidence/2026-11-11-d072-run-manifest.json).
- [Resumen del piloto](evidence/2026-11-11-d072-pilot-summary.json).
- [Auditoría posterior](evidence/2026-11-11-d072-final-audit.json).
- [Preservación y monitorización](evidence/2026-11-11-d072-preservation.json).
- [Kokoro/Piper posteriores](evidence/2026-11-11-d072-stable-engines.json).
- [Capacidades y self-test](evidence/2026-11-11-d072-caps-tests.txt).
- [Despacho de kernels](evidence/2026-11-11-d072-dispatch.txt).

Fase7.4 IN PROGRESS. D072 prueba acotada concluida por seguridad; clonación y
narración optimizadas BLOCKED, aceptación pendiente. No commit/push, otrosLXC,
pipeline ni ampliación. Siguiente: revisión del diagnóstico y preparación de
remediación del host/disco antes de otra prueba; integración solo tras WAV aceptado.
