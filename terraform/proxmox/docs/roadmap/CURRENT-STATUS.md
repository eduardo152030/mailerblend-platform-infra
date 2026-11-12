# Estado actual del proyecto

Actualizado: **2026-11-12 (Europe/Madrid)**. Seguimiento D-082.
[Roadmap](ROADMAP.md) · [Decisiones](DECISIONS.md) · [Informe F6](PHASE6-D060-CLOSURE.md).

## D082 — D081 ACCEPTED / PRODUCTION; Fase7.4 DONE / ACCEPTED

El propietario escuchó yaceptó voz ycontenido el12nov2026. Referencia final:
1059caracteres,57,36s continuos,total676,18s,EOS ycheckpoint íntegros,picoCT9,625GiB,
sin nuevosOOM. No narraciones5–10min validadas. Mismos recursos/modelo/arquitectura.
Cierre de implementación7.4 DONE / ACCEPTED; publicaciónGitD082 confirmada en
main/origin medianteSHA remoto yverificación productiva sin reinicios. No se cierran otrasfases. [Informefinal](PHASE7-D082-VOICEBOX-FINAL-ACCEPTANCE.md).
Siguiente: uso normal dentro delalcance aceptado. Intervención cerrada; sin nuevas
funcionalidades, inferencias de prueba ni optimizaciones.

### Antecedentes D081

## D081 — versión funcional consolidada; WAV continuo57,36s generado

12nov2026 Europe/Madrid, Fase7.4 IN PROGRESS. D080 aceptado como referencia técnica.
Mismo runtime/recursos/guardas, sinrestarts; backups externos verificados deambas
imágenes y103archivos/SQLite/checkpoints. ReconciliaciónD079 corregida,idempotente.
ÚnicoenvíoUI1059caracteres: EOS718,checkpoint1029×16, WAV57,36s,total676,18s.
PicoCT9,625GiB,swapmáx4KiB,PSIlocal0/OOM0; workersfinalizados,Voiceboxhealthy.
Duraciónligeramente superior a50–55; cuatrovariantesASR pendientesdeescucha, no
aceptación automática devoz olectura. Originales/perfil/checkpoints protegidos.
[Sistema,backups,resultado ylimitaciones](PHASE7-D081-QWEN-CONSOLIDATION.md). Siguiente: escuchar; no másensayos.

### Antecedentes D080

## D080 — recursos DONE técnicos; WAV continuo28,56s generado

12nov2026 Europe/Madrid, Fase7.4 IN PROGRESS. CT62715360MiB RAM ampliada en caliente
mediante recetaIaC yreconciliaciónTerraform; plan exclusivo627, final0cambios.
CPU3/swap2048/disco50 intactos. GuardaCT14GiB, workerhard9GiB/stop8,2GiB.
Preflight predictivoPASS; único job7f348e97… completado, sin segmentación/retries.
EOS358tokens ycheckpoint669×16; WAV28,56s en362,18s. PicoCT8,612GiB,
swap4KiB, sinOOM. Objetivo55–60s aún pendiente; calidad pendiente deescucha.
Perfil y77archivos protegidos preservados; Voicebox/exporters saludables.
[Informe D080](PHASE7-D080-QWEN-15G.md). Siguiente: escuchar elWAV ypreparar una validación60s separada.

### Antecedentes D079

## D079 — corrección desplegada; ensayo BLOCKED por preflight

Seguimiento12nov2026, Europe/Madrid. Fase7.4 **IN PROGRESS**.
Reclamación selectiva de cinco blobs: file reducido1,051445GiB, sin borrados.
Voicebox D079 healthy; admisión predictiva y mensaje de checkpoint corregidos.
36pruebas PASS, segunda aplicación sin recreación. Inicial4,533GiB +4,5 +0,5
proyecta9,533GiB >guarda9,5: **no se cargó Qwen ni se lanzó generación**.
Perfiles, referencia, grabaciones, historial y jobs anteriores conservados.
Recursos/guardas intactos. Siguiente: revisar margen adicional en una intervención
separada; no continuar ensayos automáticamente. [Informe D079](PHASE7-D079-QWEN-CONTINUOUS.md).

### Antecedentes D078

## D078 — diagnóstico DONE; narración desde Voicebox BLOCKED

Seguimiento12nov2026, Europe/Madrid. Fase7.4 **IN PROGRESS**. Alcance exclusivo:
lectura y preparación local; no nuevas inferencias ni cambios de producción.
Dos jobs del mismo texto573caracteres fallaron durante preparación de referencia,
antes de prefill/generación:86dde73b… y73a3755f… (actual historial). **0tokens nuevos,
sin EOS ni checkpoint**, B no iniciado. No se pueden recuperar desde Decoder.

Cambio principal respecto a D077: baselineCT3,896→5,30–5,44GiB, casi todo cachéfile;
anon inicial≈0,35GiB. Al cargar modelo ypreparar la misma referencia, CT9,70–9,78GiB
activó guarda9,5. Swap0/OOM0; high/reclaim sí ocurrió. Worker ML idéntico aD077,
no segundo modelo residente. El texto no llega al modelo hasta después de esa etapa.
La caché aumentó durante el archivadoD077;1,41GiB residentes actuales encontainerd,
con cinco blobs candidatos concretos que suman1,05GiB. No todos son liberables ya.

Propuesta mínima **no ejecutada**: consejo de reclamación acotado a esos cinco
blobs, sin borrar ni purga global, medir margen y conservar todas las guardas.
Después, ensayo continuo60s solo con autorización. No hay evidencia que obligue
asegmentar: D076 ya produjo812pasos≈64,96s nominales conEOS, aunque sinWAVfinal.
Robustez posterior: prompt reutilizable y carga selectiva de componentes FP32.

La UIretry reutiliza el ID; el backend bloquea cualquier carpeta y afirma checkpoint
sin comprobarlo. Política local preparada,6testsPASS: B solo con checkpoint íntegro;
sincheckpoint, nueva inferencia por acción explícita conotro attemptID y errororiginal
conservado. No borrar trabajos ni reiniciar modelos para sortear el bloqueo.

[Informe D078 yplan seguro](PHASE7-D078-QWEN-DIAGNOSIS.md). Voicebox/agente siguen vivos, pero liveness no
acredita generación larga. Perfil/grabaciones/checkpoints y recursos intactos;
no otrosLXC/CT618/pipeline, commit ni push. Detenido para revisión.

## D077 — Qwen personal aceptado y Voicebox productivo DONE técnico

11 de noviembre de2026, Europe/Madrid. **Fase7.4 IN PROGRESS**: duración55–60s
pendiente. El propietario autorizó ensayo único con texto nuevo e integración
productiva; confirmó «Sí, voz y texto correctos» después de escuchar la muestra.

A→B300/context25 PASS: Base0.6B FP32/SDPA, referencia real, semilla42 y3hilos.
EOS136tokens en95,547s; checkpoint447×16 persistido/verificado, A finalizado antes
de B. WAV10,8s/24kHz/mono/PCM16; total183,041s. PicoCT A8,141GiB/B5,660GiB,
RSSHWM A5,592/B2,276GiB;swap0/PSIlocal0/OOM0. No120 ni segundo ensayo.

Voicebox healthy con imagen qwen-isolated-d077 y cola privada, sin Qwen residente
ni Docker socket. AgentePVE voicebox-qwen-627 exclusivamente627, sin puertos nuevos;
A/checkpoint/PID0/B, guardas conservadas. CT3CPU/10GiB/2GiBswap; workerhard9GiB,
guardaCT9,5GiB. UI/API/historial/descargas conservados. Nuevo WAV aceptado publicado
en historial deEduardo, sin inferencia adicional. Perfil/samples idénticos al backup;
Kokoro/Piper conservados. No otrosLXC/CT618/pipeline, commit ni push.

23tests runtimePASS; backup68archivos y restore SQLite verificados fueraCT, imagen
original conservada y nueva archivada. Incidencia de permisos del candidato resuelta
con rollback real y gateUID999 previo; permiso del WAV nuevo corregido sin tocar
originales. Segundo deploy sin recrear app. Observación180s/7muestrasPASS, sin nuevos
errores/OOM/swap; Prometheus9090 sigue como incidencia previa fuera de este alcance.

[Informe y uso productivo](PHASE7-D077-PRODUCTION.md). Próximo paso: uso de usuario y posterior validación
específica55–60s. No se ejecutó otra inferencia real porAPI: se probaron componentes,
historial/descarga y rechazos. Los apartados siguientes son históricos.

## D077 — preparación del checkpoint y decoder independiente DONE

11 de noviembre de 2026 (Europe/Madrid). Fase 7.4 **IN PROGRESS**.
**Preparación/validación sin inferencia DONE; ensayo real TODO, sin autorizar.**
Dos procesos exclusivos: A persiste referencia+códigos y finaliza; B carga solo las
271 entradas del decoder, después de comprobar PID0 y cgroup vacío. Checkpoint
privado en disco del job, NPY int64 sin pickle, manifest/hashes y commit atómico;
recorte de referencia fiel al backend. Bloques300/context25 por defecto;120 es
experimental y no se selecciona automáticamente.

17 tests locales PASS. En CT627: imports y layout meta sin pesos reales PASS,
escritura sintética y recuperación desde otro contenedor PASS, prueba padre+hijo
cancelada con PID0/cgroup vacío y retirada solo del worker propio. Segunda preparación
idéntica no cambia revisión ni recrea servicios. D076 no contiene checkpoint real
recuperable. Job narracion01 preparado; **ningún peso cargado ni WAV generado**.

CT627 conserva3CPU/10GiB/2GiBswap, workerhard9GiB y guardaCT9,5GiB. Voicebox healthy,
Eduardo/originales/transcripción intactos, Kokoro/Piper descargados;27 configs PVE
sin cambios y0OOM nuevos. Exporters localesHTTP200; Prometheus9090 sigue inaccesible,
incidencia previa sin intervenir. No otrosLXC/CT618/pipeline ni commit/push.

Siguiente paso: revisar [D077](PHASE7-D077-CHECKPOINT-DECODER.md) y autorizar separadamente un único ensayo
A→B300 para medir el efecto de liberar Talker. RAM real del decoder, WAV y calidad
siguen pendientes; no se afirma equivalencia acústica300/120. D076 siguiente es histórico.

## D076 — EOS confirmado; decoder detenido por guarda de memoria

Estado vigente: 11 de noviembre de 2026 (Europe/Madrid). Fase 7.4 **IN PROGRESS**.
Recursos CT627 **DONE**: 3 vCPU, 10 GiB RAM y 2 GiB swap, aplicados en caliente y
reflejados en IaC. Voicebox y CT627 no se han reiniciado durante la intervención.

Tras la autorización explícita de máximo 15 minutos, se ejecutó un único intento02:
Base 0.6B, FP32/SDPA, tres hilos, referencia y transcripción reales de Eduardo.
**Talker emitió EOS: 813 tokens en 634,226 s (1,282 tokens/s)**. Llegó al decoder,
pero el supervisor lo detuvo por CTmemory.current **9,533 GiB > guarda9,5 GiB**.
Worker cgroup máximo5,984 GiB; RSS muestreado6,406 GiB. CT al parar: anon5,906 GiB,
file3,298 GiB. Swap0, PSI local0, nuevos OOM0. Total701,542 s; no fue timeout.
No hay WAV y no se repitió. Objetivo55–60 s **BLOCKED**, sin aceptación de voz.

Voicebox healthy, perfil Eduardo y originales intactos; todos los configs PVE
conservados. Kokoro/Piper siguen descargados; no nueva síntesis funcional. Tras la
parada CT≈3,89 GiB (anon0,35/file3,30), CPU≈0,009 cores, swap0. Los36 exporters
respondieron, uno tras repetir lectura por timeout. Prometheus9090 sigue inaccesible
como antes del ensayo; Grafana DBok. No se acredita cadena central ni alertas.

**Siguiente paso propuesto, sin ejecutar:** persistir códigos antes del decoder,
liberar Talker y evaluar bloques internos300→120 pasos conservando contexto25.
El código instalado ya usa chunking; no es un flag público del wrapper. Mantener
recursos y guardas actuales; no otro piloto sin autorización. Sin cambios en otros
LXC, CT618 o pipeline; sin commit/push. [Informe D076](PHASE7-D076-LONG-NARRATION.md).
Los resultados D075 siguientes son históricos.

## D075 Fase B — intento único FP32 concluido F, sin carga de Qwen

11nov2026,Europe/Madrid. Preflight60sPASS:host≥9,345GiB disponibles,CTPSI0,swap
estable412MiB,sinjobactivo/59UP/disco19GiB. Se lanzó una vez workeraislado CPUFP32
SDPA solicitado,max_new_tokens64,j2/interop1,deadline≤300s yguardas6GiBworker/7GiBCT.
**F: error de cachéNumba/librosa enimportación**, antes decargar pesos/prepararref/
generar. RootFSROsinNUMBA_CACHE_DIRtmpfs: omisión deconfiguración delpiloto.
Worker8,205s,total14,326s,RSSHWM483MiB;0tokens,0WAV,0cargas demodelo. No prueba
defalloFP32/SDPA ni benchmarkdemodelo. No segundo intento porlímiteexpreso.

Proceso paradoRunningfalse/PID0,ExitCode1,0OOM;Voiceboxmismaimagen/ID/iniciohealthy,
Eduardo/referencia/originalintactos.59UP/GrafanaPromPASS,0alertas/nuevosOOM,27configs
PVEconservadas. NoCT618/cAdvisor/otrosLXC/recursos/pipeline/commit/push.
Correcciónpropuesta `NUMBA_CACHE_DIR=/tmp/numba`, no aplicada ni repetida; requeriría
otro lanzamiento autorizado. Fase7.4INPROGRESS; intentoDONE,validaciónFP32BLOCKED.
**Detenido para revisión.** [InformeFaseB](PHASE7-D075-QWEN-FP32-PHASE-B.md).

## D074 ejecutado y D075 Fase A terminada — DONE

11nov2026, Europe/Madrid. Se ejecutó la aprobación exacta del manifiesto
d2396813…fc8b00: **105/105 elementos retirados**,61rutas y44cacheIDs; sin limpieza
globalDocker. Espacio libre7,056→18,997GiB, +11,941GiB reales. Imágenes, modelos,
contenedores,volúmenes,backupscomprimidos,voz/perfil/referencias/audios protegidos
conservados. Sin reinicios,recursos,CT618/cAdvisor,otrosLXC,pipeline,commit/push.

FaseA de segundaopinión: i5-6500/4cores4threads/AVX2FMA/sinBF16nativo; dosDIMM8GB
en canalesA/B. PyTorch2.8CPU real: BF16 frenteFP3210,48–146,33× máslento en matrices
y44,19× enconv1d pequeño, sin cargarQwen. Modelooficial hereda8192tokens; backendno
acota petición. NoEOSdefectuoso demostrado. CINT8D072 sí acotado312frames, último50;
codecconcurrente/WAValfinal, sobrehilos/decoder/ref larga aún pendientes de prueba.

Memoria finalCT: anon0,225/file3,192/kernel0,365GiB; swap413MiB tras releerbackups,
sinOOM. No cache/swapforzados, no interpretarcurrent comoRSS. Preflight detectó y
resolvió auxiliaresSQLite vacíos creados por chequeoD074 (DB/tars intactos), helperAPT
inactivo yselectorbooleanocache sincoincidencias, antes de ampliar ninguna eliminación.

Voiceboxhealthy/mismaimagen/ID/inicio, Eduardo/originales intactos; K/Pdisponibles.
59targetsUP/18Node/18cAdvisor, Grafanadb/dashboards/proxyPromPASS,0alertas actuales,
0OOM/erroresproductivos nuevos,27configuracionesPVE intactas. No nueva generación.
**Fase7.4 IN PROGRESS; FaseADONE,FaseB TODO yno iniciada.** Detenido para revisión
del diagnóstico antes de inferencia. [Informe FaseA](PHASE7-D075-QWEN-HYPOTHESES-PHASE-A.md),
[limpiezaejecutada](evidence/2026-11-11-d074-execution.json).

## Histórico D074 — preparación previa a la aprobación

11nov2026, Europe/Madrid. **Preparación DONE; Fase7.4 IN PROGRESS.** Lista cerrada
de105elementosCT627,11,946GiB potenciales:44cacheIDsBuildKit no usados/compartidos,
47rutasAPT/buildpúblico y14backups expandidos duplicados. SHA256manifiesto
`d2396813e51c98e171052f0bc8765c69476467db53b098d89727954474fc8b00`.
14/14expansiones↔tar idénticos, manifiestosválidos/SQLiteok,14copiasexternas con
SHA256idéntico. Conservar comprimidosCT+externos, modelos,perfil/originales/audio,
volúmenes eimágenesrollback. **0borrados y0cambios de recursos/reinicios.**

cAdvisor618healthy,0reinicios/0OOMnuevo,2880scrapes24hUP; límite128MiB tocado.
Propuesta opcionalIaC256MiB/384MiBRAM+swap/CPU0,50, solo local yno aprobada; no
condición previa impuesta aQwen. No Budibase/CRM/API/otroscontenedores modificados.
Voiceboxhealthy/Kokoro/Piperdisponibles,grabaciones/perfilintactos;18Node/18cAdvisor
y59targetsUP,0nuevasalertas/OOM. HostDiskFilling627FIRING previo sigue activo.
27configsPVE intactas,sinpipeline,commit/push. QwenC ymodelos preservados, sin nueva
inferencia enpreparación; voluntad decontinuarQwen registrada como siguiente objetivo.

Detenido para aprobación de **[lista exacta105](PHASE7-D074-CLEANUP-LIST.md)** antes de eliminación;
CT618 requiere permiso separado si se decide aplicar propuesta. [InformeD074](PHASE7-D074-CONTROLLED-MAINTENANCE.md).

## D073 — capacidad auditada; sin limpieza ni nueva inferencia — DONE

11nov2026, Europe/Madrid. Fase7.4 IN PROGRESS; vozQwen larga BLOCKED. Auditoría
de solo lectura: host15,50GiB físicos/9,07GiB disponibles en snapshot; límitesLXC
activos55,61GiB no son reservas. SinQwen,PSIfullhost alcanzó5,67% en60s; stall
host1,189s/cAdvisor6181,190s/CT6270,000029s, cAdvisor618 a128MiB y+4918eventosmax.
Fuente de presión actual independiente deQwen demostrada; causaexactaD072 no
reconstruida sinPSIcgroup histórico. No cambios enCT618 ni otrosLXC.

CT627 disco7,056GiB libres; Docker/containerd17,482GiB ybackups13,700GiB.
PropuestosA4,748GiB temporales/cache yB7,198GiB copiasbackup expandidas condicionadas
a integridad/restore/retención: hasta11,946GiB, **0bytes eliminados/archivados**.
Modelos,perfil,originales,historial eimágenesrollback protegidos. Voiceboxhealthy,
mismaimagen/ID/inicio,0jobs/modelosactivos; K/Pdisponibles yWAVsD072PASS legibles,
sin nueva generaciónD073.59targetsUP,HostDiskFilling627FIRING sinresolver;27configs
PVE intactas,otros17CTgestionados sin cambios; sinpipeline,recursos,commit/push.

Recomendación: revisar límitecAdvisor618 mediante permiso separado, decidir limpieza
acotada tras revisar informe, no ampliarRAM ni otroQwen ahora. **Detenido para
revisión del propietario; ninguna limpieza/corrección ni nuevo piloto autorizado.**
[Informe D073](PHASE7-D073-CAPACITY-AUDIT.md).

## D072 — Qwen C/BLAS: piloto detenido por seguridad

11nov2026, Europe/Madrid. **Fase7.4 IN PROGRESS; diagnóstico/piloto acotado DONE,
clonación optimizada y narración BLOCKED.** Base0.6B INT8 carga5,738s y comienza
ICL real; sin WAV. Corte~123s porPSIfull del host sostenido≥2%, pico9,10%.
PicoRSS3,697GiB,worker3,712GiB,CT5,094GiB,OOM0; no prueba de exceso del límite7GiB.
Parada exclusiva del piloto3,406s,PID0, sin reiniciarVoicebox/CT. NoINT4/BF16
ni15/30/60s tras fallo corto. No sustituir producción ni declarar voz aceptada.

ProducciónD069healthy, referencia/original/perfil intactos, sin trabajos activos.
Kokoro/Alex2,58s/8,745s yPiper2,113s/2,029s comprobados después;59targetsUP.
**Aviso de discoCT627:7,1GiB libres/14,43%,HostDiskFilling PENDING**; no limpieza
ni borrado de imágenes/backups. ConfiguracionesPVE ajenas conservadas; sin pipeline,
ampliación,commit/push. OpenVoiceD071 rechazado por propietario y parado.
Recomendación: optimizar/diagnosticar más, sin descartar porRAM ni integrar.
Siguiente: revisar presiónhost y remediación acotada de espacio antes de otro piloto;
WAV y escucha necesarios antes de promover. [Informe D072](PHASE7-D072-QWEN-C.md).

## D070 — cancelación recuperada; Qwen largo bloqueado

11nov2026, Europe/Madrid. **Fase7.4 IN PROGRESS para narración personal de un minuto.**
D070 diagnóstico/cancelación/comparación **DONE**; D069 conserva solo la aceptación
de su muestra corta. Trabajo d7ce3d31 de896caracteres: tras~20min seguía en fase
de tokens. La API marcó cancelado pero el hilo nativo seguía a~1,97núcleos. Con
autorización adicional expresa se reinició únicamente DockerVoicebox, sin reiniciar
CT627 ni cambiar imagen, perfil, referencia, recursos u otrosLXC.

Verificación real: healthy, sin trabajos activos ni inferenciaQwen residente; CPU
prácticamente en reposo, referencias/originales idénticos, sinOOM. Kokoro yPiper
generan audios breves en helpers offline sin perfiles nuevos.59targetsUP/sin alertas;
configuracionesPVE ajenas conservadas. Snapshot privado previo al reinicio y copia
restaurada fueraPVE; backupsD069 retenidos. No pruebasQwen largas, motores nuevos,
pipeline, commit ni push.

Comparación por código/documentación/metadata, no benchmarksCPU inventados:
OpenVoiceV2+MeloES es primera candidata propuesta; XTTSv2 alternativa si la identidad
no resulta aceptable; ChatterboxMTL tiene mayor presión de carga y riesgo de soporte.
Tiempos yRAM alternativos aún sin medir enCT627. Siguiente: revisar propuesta antes
de descargar/desplegar un nuevo motor. No autorización implícita de piloto.
[Informe, comparación y evidencias](PHASE7-D070-CPU-ALTERNATIVES.md).

## D069 — perfil personal único y primera muestra Base — DONE, aceptada

El propietario sustituye el objetivo de voces adicionales por su voz real. CT627
conserva3vCPU,7GiB,swap512MiB,50GiB. Perfil único **Eduardo — Mi Voz**,
`1fd00418-2a79-4178-883f-af6c3f5e07ee`, referencia real ytranscripción confirmada.
Grabación preservada yverificada fueraGit/enalmacenamiento privado persistente.
Ocho perfiles sobrantes retirados tras inventario, backup/restore yexports privados;
no motores desinstalados ni catálogos integrados borrados.

Guard0.6B corregido porUUID real (buscaba nombreantiguo);1.7B bloqueado por tamaño.
**Base0.6B generó WAV6,40s en106,86s**: prompt23,85s,tokens41,27s,codec33,37s.
Cgroup observado5,18GiB,HWM4,68GiB,swap+5,32MiB,OOM0; no cortes.
El propietario confirma parecido, contenido yacento: **ACCEPTED_BY_OWNER**. No60s
validado ni rendimiento de narración larga demostrado. Los cierres D068 inferiores
son históricos; ya no se exige perfil masculino/femenino ni otras grabaciones
para iniciar la clonación, puesto que la referencia real ya está incorporada.

Fase7.4/D069 **DONE — Accepted** para perfil único yprimera muestra.
[La muestra personal](http://192.168.1.127:17493/audio/925f8b71-6ad7-46f0-a48a-ffa3881004ef)
ya está aceptada. Siguiente: uso de la voz personal; narración larga requiere
validación separada. [Informe D069](PHASE7-D069-PERSONAL.md).
No otrosLXC,pipeline,recursos,commit nipush.

## Histórico D068 — 7 GiB y dos voces operativas; Qwen bloqueado

2026-11-10 (Europe/Madrid). **Fase 7.4 IN PROGRESS.** CT627: **3 vCPU,7168 MiB,
swap512 MiB,50 GiB**; plan inicial solo memoria627 y un reinicio, sin recrear LXC.
Kokoro/Alex conservados y Piper es_ES-sharvard F operativo por API, con muestras
reproducibles masculina/femenina. Edad/acento/calidad pendientes de escucha.
Ocho perfiles; personal no creado hasta grabaciones reales, originales privados
 yflujo Base0.6B implementado/guardado, sin descargar ni probar clonación real.

Qwen se instrumentó por etapas: códigos reales y entrada al codec, no deadlock
observado del generador. Probes finitos parados por PSIfull2,51% yswap+80,94MiB;
pico cgroup4,97GiB y ceroOOM. No PruebaA completa niB/C, sin tiempo por minuto.
Los600s anteriores eran el plazo del supervisor; causa completa sin determinar.
No forzar másRAM ni otra carga tras el veto. CustomVoiceCPU bloqueado enproducción.

Imagen operativa PiperR2 fijada y archivada (27blobs verificados); originalD063
retenida. Serialización real probada: dos trabajos completados, máximo1modeloTTS,
mutación concurrente409; doble deploy sin recrear/reiniciar. Otros17CT y59targets
conservados; observación final ybackup/restauración enel informe. Una muestra antigua
D063 ausente se recuperó con suUUID/WAV exactos sin revertir datos nuevos; origen
no determinado, no se emitieron borrados. No pipeline, commit ni push.

Siguiente: escucha/aceptación de muestras y grabaciones reales cuando elpropietario
quiera. Clonación noDONE sinprueba real; diagnóstico adicionalQwen solo propuesta.
[Informe y evidencias](PHASE7-D068-VOICEBOX.md).

## D067 — piloto 6 GiB terminado sin audio Qwen; recuperación PASS

2026-11-10 (Europe/Madrid). **Fase 7.4 IN PROGRESS**. Piloto ejecutado: Qwen
CustomVoice0.6B BF16/SDPA cargó (3,87 s interna/9,84 s API), pero la frase corta
agotó el plazo operativo600 s sin WAV. No se ejecutaron30/60 s. Pico cgroup
incluida parada4,22 GiB, RSS observado3,03 GiB, swap4 KiB, ceroOOM. Es un fallo
por timeout, no por superarRAM. No se demuestra velocidad ni viabilidad de60 s.

Configuración final restaurada: **3072 MiB,3 CPU,swap512,disco50**, imagen original,
Kokoro/Alex verificados. El retorno automático de imagen funcionó; el plan guardado
RAM falló por un manifiesto modificado durante el ensayo y se recuperó con un plan
nuevo revisado solo627. Automatización corregida localmente, no repetir piloto.
Recreación Docker conserva7 perfiles y25 hashes; segunda aplicación Compose sin
recrear/reiniciar. Otros17 CT intactos,59targetsUP,Grafana Fleet/DetailsPASS.
Observación180s/7PASS; TerraformNotes solo627 y segundaaplicación0/0/0;
clienteAPIKokoro realPASS. Backupfinal restaurado:39archivos/13audios.

Masculino basado enAlex con muestra real; femeninoSerena registrado pero
**BLOCKED: sin muestra y sin acento español validado**. Personal sinID ficticio;
procedimiento deWAV privado preparado, Base0.6B sin carga/inferencia probadas.
Los tres rechazados siguen conservados. No pipeline, commit ni push.
Siguiente: revisión auditiva masculina y decisión sobre diagnóstico de rendimiento
Qwen; no recomendar másRAM ni promover esta candidata. [Informe](PHASE7-D067-QWEN-6G.md).

## D066 — piloto ejecutado y restaurado; Qwen no aceptado

2026-11-10 (Europe/Madrid), **Fase 7.4 IN PROGRESS**. D066 **DONE como ensayo
controlado**, resultado Qwen **FAIL por parada preventiva**, recuperación **PASS**.
CustomVoice 0.6B cargó realmente en CPU BF16/SDPA (3,81 s de carga interna;
9,83 s por API). En la frase corta alcanzó 3,54 GiB de cgroup y 2,50 GiB RSS:
se detuvo al superar el umbral de 3,5 GiB. Sin OOM; no terminó audio Qwen ni se
probó la narración de 60 s. No se demuestra todavía viabilidad de narración.

Rollback automático: imagen original, Kokoro y Alex verificados; RAM actual
3072 MiB, máximo temporal 4096 MiB. Observación posterior 180 s/7 muestras PASS,
18 Node/18 cAdvisor/19 Blackbox UP; configuraciones de los otros 17 CT intactas.
Perfiles y muestras rechazados conservados, sin borrados. Sin cambios al pipeline,
sin commit/push. Recomendación propuesta: optimizar más antes de otro ensayo,
sin promover Qwen ni descartar el hardware solo por pesos teóricos. Autorización
D066 consumida por este piloto; siguiente paso: revisar resultados y una eventual
propuesta de optimización con nueva autorización, sin repetir la prueba tras HALT.
[Informe](PHASE7-D066-QWEN-PILOT.md).

## D065 — revisión Qwen optimizada, diagnóstico previo terminado

**Fase7 IN PROGRESS.** CT627 sigue operativo con3vCPU,3072MiB RAM,512MiBswap y50GiB.
D064 creó cuatro candidatas y amplió2→3GiB por18,4%RAMlibre/PENDING, con backup,
restore yplan solo627. Reboot/persistencia/Kokoro posteriorPASS;180s/7muestras,
18Node/18cAdvisor/19BlackboxUP, sinOOM; segundaaplicaciónTerraform ycatálogo sin cambios.
El propietario considera **Alex aceptable** y descarta Dora/Santa/Emma nuevos.
Sus perfiles siguen conservados hasta la revisión previa solicitada; originalD063
protegido. No se asignan edades ni certificación adicional deacento.

D065 reabre viabilidad: backendactualCPUFP32, peroBF16 puede reducir pesos0.6B a~2GiB.
Operadores pequeñosBF16/FP16CPU PASS; no son cargaQwen ni prueba denarración.
Transformers4.57.3 ignora low_cpu_mem_usage. Descarga alvolumen sin carga es posible;
Kokoro puede mantenerse endisco yliberarse deRAM. Cuantización no integrada enelfork.

[Diagnóstico/recomendación](PHASE7-D065-QWEN-OPTIMIZATION.md),
[catálogo/resultadosD064](PHASE7-D064-VOICES-QWEN.md).
**PruebaBF16, descargaQwen, ampliación4GiB ylimpieza: preparadas, NO ejecutadas**
después de laúltima instrucción. Antes de más cambios productivos elpropietario exige
presentar diagnóstico yrecomendación. Siguiente: revisar prueba0.6B secuencial,
piloto y~60s bajo4GiB, conmediciónRSS/cgroup/swap/OOM yrollback. No pipeline, otrosCT,
umbralesPrometheus, commit ni push. D063 conserva su cierre histórico deprovisioning.


## D064 — catálogo español y diagnóstico Qwen — IN PROGRESS

2026-11-10 (Europe/Madrid). Autorizado soloCT627: auditar perfiles/modelos, conservar
Kokoro y sus perfiles, generar muestras comparables y evaluar Qwen dentro del límite
máximo4GiB. Ampliaciones3/4GiB solo justificadas por medición/capacidad, con backup,
rollback y reinicios documentados; no crear/reemplazar CT, tocar otrosLXC, reglas
Prometheus, pipeline, exposiciónWAN ni commit/push. No aceptar acento/edad/calidad
sin revisión auditiva del propietario. D063 conserva su cierre técnico previo.
Primero distinguir error deperfil de disponibilidad/modelo y presupuestar tensores
CPU antes de descargas/cargas. [Informe](PHASE7-D064-VOICES-QWEN.md).


## D063 — primer provisioning real Voicebox — DONE técnico

CT627 **infra-voicebox** operativo en http://192.168.1.127:17493, solo LAN.
3vCPU, **2048MiB RAM**,512MiB swap,50GiB local-lvm. Se comenzó con1080MiB de
plantilla106 y se amplió1536→2048MiB por mediciones, según permiso del propietario.
SSH por clave y hardeningD062 realesPASS; incidenciaDSA recuperada sin reemplazo.
Kokoro CPU/español: WAV24kHzmono6,46s generado en12,94s y recuperado porcliente.
Persistencia trasreinicio, backup/restauraciónaislada eimagen exacta archivadaPASS.

Cobertura18Node/18cAdvisor/19BlackboxUP,18filas Fleet saludables ysinUNKNOWN;
627 seleccionable enFleet/Details sin modificar dashboards. UptimePVEdelta30s.
600s/21muestras sinanomalías niFIRING/PENDING.17configuracionesPVE y56targets
previos idénticos. Terraformfinal0/0/0; Compose0recreaciones/0reinicios;
monitorización0escrituras/0recargas.16testsprovisioning y15inventarioPASS.

[Informe y17criterios](PHASE7-D063-VOICEBOX.md),
[resultado](evidence/2026-11-10-d063-result.json),
[inventario627](../inventory/627-LXC-INVENTORY.md).
SinUAT/escucha humana ni nuevoensayoTelegram; no se amplían dispensas anteriores.
API sin autenticación integrada acreditada, restringida porreglaLAN; otrosmotores,
concurrencia, rangoDHCP/retención yDRglobal pendientes. Primer intento1080MiB fallido
conservado en historial, seguido de tres audios completados. Sin commit/push.
Fase7 globalINPROGRESS;7.2/7.3 OUTOFSCOPE. Siguiente: uso interno/revisión del
propietario; integración futura delpipeline requiere intervención separada.

## Antecedente D-062 — cierre local anterior a D063

**Implementación local DONE; despliegue/aceptación real PENDING VERIFICATION.**
7.4 sigue READY FOR FIRST REAL PROVISIONING TEST. Bootstrap aditivo por pct exec,
clave pública del propietario, openssh-server, acceso por clave antes de endurecer,
sshd -t/-T, rollback y consola conservados; provider admite inyección opt-in con
conjunto completo de claves heredadas revisado. 15 tests provisioning +14 inventario,
dos mocks de un solo CT y parser real OpenSSH PASS. Sin producción, nuevos CT,
contraseñas modificadas, SSH de los17, commits ni push. Riesgo tainted tras fallo
del provisioner: recuperar y revisar estado; nunca reaplicar con reemplazo automático.
[Informe y límites](PHASE7-D062-SSH.md), [runbook](../runbooks/NEW-LXC-PROVISIONING.md).
Siguiente: autorización específica del primer CT real; ejecución productiva detenida.

## D-061 — cierre del alcance solicitado

**7.1 Git Consolidation: DONE.** Cinco commits principales publicados por SSH
normal, sin force; main/origin sincronizados0/0. Cierre documental separado.
**7.4: READY FOR FIRST REAL PROVISIONING TEST.** Flujo sobre módulo/inventario
existentes, dos fixtures con/sinDocker, Notes/ficha, exporters/targets/candidatos
preparados y dos planes mock1alta/0cambios/0destrucciones. Ningún CT creado.
**7.2 Security Hardening y7.3 Disaster Recovery: OUT OF SCOPE**, no DONE.
Cambios ajenos y secretos/estado/backups locales conservados fuera del commit.
[Informe](PHASE7-D061-EXECUTION.md), [Git](evidence/2026-11-10-d061-git-published.json),
[runbook](../runbooks/NEW-LXC-PROVISIONING.md).

## Fase actual

**Fase 6. Grafana & Dashboards — DONE**, conforme a los once criterios autorizados
D-060. Fases1–5 conservan sus cierres y límites de aceptación. **Fase7 IN PROGRESS**
con7.1 publicada D061 y7.4 DONE técnico delprimeralta VoiceboxD063;7.2/7.3 OUT OF SCOPE, no DONE.

Fleet Overview y LXC Details están desplegados, enlazados en ambos sentidos y
verificados en navegador. Los nueve dashboards son IaC, incluidos siete anteriores
preservados con UID, modelo y carpeta. Providers duplicados resueltos; receta
Compose con tres mounts efectivos e imagen actual fijada por digest.
Environment y tabla Componentes Docker no reaparecen en Fleet; Docker sí está en Details.

## Producción comprobada al cerrar F6 — histórico D060

Lectura **10 nov08:08 CET**:17/17 Node,17/17cAdvisor,18/18 Blackbox y exporter PVE UP;
sondas success1, tres checks periódicos Odoo/PG con resultado1, sin FIRING/PENDING.
Reglas F5 y catálogo de targets idénticos a baseline D060. Grafana disponible y
nueve dashboards provisionados. Salud consolidada de17 CT sin UNKNOWN y uptime real.
[Resultado](evidence/2026-11-10-d060-result.json).

CT 613 sin app de negocio verificada; Application N/A, sin exención por DEMO.
CT 621 ping JSONFocalboard; CT 623 Odoo8069+PG y CT 625 pg_isready periódicos; CT 618 readiness CRM.
CT 611/616 N/A solo como negocio; Monitoring real. STOPPED solo desde PVE.

## Validación y persistencia

Implementación/navegador09 nov:34 escenarios,663 consultas instantáneas/28 históricas,
654 frames reales, filtros y navegación CT/rango, sin errores. Uptime comparado con PVE
para17 CT, máximo20 s. Revisión10 nov y reaplicación final sin escrituras/recargas/
reinicios; sin cambios en Grafana activo ni reglas/targets.

Persistencia probada por arranque aislado del candidato exacto y SQLite consistente,
misma imagen, red none/sin puertos; nueve modelos cargados y carpetas conservadas.
Ensayo detenido y preservado. No recreación de Grafana productivo ni nueva UAT de apps.
[Ensayo final](evidence/2026-11-10-d060-recreation-replay-final-20261110.json).
Backups CT/fuera PVE y originales conservados, sin commits/push.

## Pendientes externos a F6

| Estado | Pendiente | Límite / siguiente acción |
|---|---|---|
| TODO | F4-05: scrape propio Grafana | Job aún ausente; sonda HTTP no lo sustituye |
| IN PROGRESS | F4-06: observabilidad completa del host | Estado/uptime CT resueltos; host físico completo no aceptado |
| TODO | F7: secretos históricos/estado Terraform, SSH/TLS global, CI/herramientas y DR continuo | No resueltos por snapshots o cierre de dashboards |
| TODO | Digest EVA, prevenciónsGTM, UAT/GA4 y deriva inventario/discos | Requieren alcance específico; no certificados por HTTP/readiness |
| DONE | Consolidación Git curada D061 | Publicada; cambios funcionales ajenos conservados fuera del commit |

Límites representados:sin contador fiable de reinicios Docker; capacidad del filesystem
en vez decuota PVE/Terraform; descripción decontrato dealerta con evaluación enlazada
a Prometheus; inventarioslocales sin hospedaje web. No quedan componentes esenciales
pendientes dentro de los once criterios F6. Aceptación visual humana no se inventa;
D060 autoriza el cierre tras comprobaciones objetivas y de navegador.

## Autorización y siguiente paso

D063 sustituye la prohibición histórica de crearCT exclusivamente para el alta627,
su aplicación y su integración aditiva. Ejecución solicitada terminada; no habilita
otras altas, apps existentes, exposiciónWAN ni modificaciones delpipeline.
No commit/push ni borrado de backups/originales/evidencias.7.2/7.3 siguen fuera de
alcance, noDONE. Nuevas ampliaciones o integraciones requieren alcance específico.
No deploy-all ni aplicar planes generales sobre la deriva heredada.
Siguiente: uso interno deVoicebox; futuro contrato devoz enoff documentado, sin
implementación delpipeline. Los apartadosD061/D062 inferiores son antecedentes.

## Historial

[Revisión anterior D059](DOCUMENTATION-D059-REVIEW.md),
[historial previo](CURRENT-STATUS-HISTORY.md),
[decisiones](DECISIONS.md). Los informes originales conservan sus fechas/evidencias;
no reutilizar siguientes pasos históricos como permisos actuales.

## Preparado frente a desplegado en D061

Compatibilidad sinDocker en regla de ausencia y dashboards es código preparado,
no recargado en producción. Los17actuales mantienen el despliegueD060/F5 intacto.
El primer CTsinDocker exige autorización e integración coordinada de ese cambio.
Bootstrap/recibo son candidatos locales; estabilidad, segunda aplicación real y
cadena end-to-end no están probadas por mocks. Siguiente: autorización específica
del primer alta real. Sin hardening/DR global ni rotación histórica.

D063 completa elprimeralta Docker627; los límites sinDocker deD061 anteriores
permanecen históricos yno autorizan cambios globales en servicios existentes.
