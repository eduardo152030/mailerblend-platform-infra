# Fase 7.4 — D076: nuevos recursos y ensayo de narración de trading

Estado: **recursos DONE; intento02 terminado E por guarda de memoria del CT en decoder; WAV55–60s BLOCKED**.
11nov2026, Europe/Madrid. Se ejecutó un único nuevo intento tras la autorización
«Sí, máximo15minutos». El Talker finalizó con EOS; no se obtuvo WAV. No se han
repetido pruebas ni elevado recursos/guardas después del resultado.

## Intento02 — resultado vigente (máximo900s)

Mismos Base0.6B/FP32/SDPA, referencia/transcripción/texto193palabras, semilla42,
max_new_tokens1024, tres hilos einterop1. Directorio job02 yworkerlong02 independientes;
job01 y evidencias conservados. Imports NumBa/librosa ycachetmpfsPASS antes decargar.

Preflight60s: hostmín21,63GiB disponibles, CTswap0 estable/PSI0, sin inferencias
activas, Voiceboxhealthy/exporters localesHTTP200, disco19GiB. HostPSIglobalmáx14,14%
yactividadswap de fondo285323páginas entrada/157230salida, registrados antes del
worker. CTnointercambia; no se atribuye actividad global almodelo sin evidencia.

| Medición | Resultado02 |
| --- | --- |
| Carga, con caché ya presente | 2,615s |
| Preparación referencia (incluye encode3,295s) | 13,093s |
| Prefill (incluido en generación) | 3,096s |
| Talker, secuencia813tokens incluyendo EOS | 634,226s;1,282tokens/s |
| Finalización Talker | EOS; no llegó al límite1024 |
| Códigos acústicos | 812×16; no persistidos antes deldecoder |
| Decoder | Inició a656,404s delworker; no terminó; unos42s hasta parada |
| Total supervisado | 701,542s; no timeout |
| Guarda que detuvo | CTmemory.current9,533GiB >9,5GiB |
| Pico worker cgroup / RSS muestreado | 5,984GiB /6,406GiB; no es RSSHWM |
| CTalparar: anon /file /kernel | 5,906 /3,298 /0,328GiB |
| Worker alparar: anon /file /kernel | 5,564 /0,403 /0,017GiB |
| Swap CT/worker; PSIlocalfullavg10 | 0 /0;0% |
| Hostdisponible mínimo duranteensayo | 16,09GiB |
| CPUmedia/máxima muestreada | 2,248 /2,893cores;CPUtotal≈1570s |
| OOMnuevo host/CT/worker | 0 /0 /0 |
| Parada | cgroup.kill delworker;Exit137,OOMKilledfalse,PID0 |
| WAV/duración real | No existe; no medida |

No se alcanzó la guarda8,2GiB delworker ni sulímite duro9GiB. Se activó la guarda
adicional delCT9,5GiB, que conserva margen frente asulímite10GiB. No es una muerte
OOM delkernel ni un timeout. La señal137 procede de lacancelación delsupervisor.
Las medidas cgroup son jerárquicas: no sumar worker yCT ni equipararRSS conanon.
Los3,298GiB file no son todos liberables inmediatamente:3,034GiB estaban active_file;
no se han purgado cachés ni modificado otros procesos para forzar elresultado.

### Diagnóstico deldecoder y propuesta, sin ejecutar

La implementación instalada concatena códigos dereferencia ysalida antes dedecodificar
yrecorta lareferencia después (`qwen3_tts/inference/qwen3_tts_model.py`,líneas612–629).
Por ello procesa también aproximadamente25s dereferencia, además delanarración.
La configuración real output_sample_rate24000/decode_upsample_rate1920 equivale a
12,5pasos/s;812pasos implican **64,96s nominales**, no duración WAV verificada ni
prueba de pronunciación completa. Nunca usar elnombre12Hz como factor exacto12.

El tokenizer12Hz ya llama a `decoder.chunked_decode` por defecto: bloques300pasos
(24s) yleft_context25pasos(2s), líneas886–896/1015 delmodeling instalado. No recomendar
«activar chunking» como si estuviera desactivado. Elwrapper público decode no expone
chunk_size; reducirlo requiere adaptación interna delworker aislado, no un flag ya
soportado por Voicebox.

**Siguiente paso propuesto, pendiente de autorización:** guardar códigos acústicos,
metadatos de referencia/recorte y métricas antes deldecoder; desacoplar Talker ycodec
para liberar elmodelo autoregresivo antes dedecodificar; evaluar chunk300→120
(9,6s) concontext25 conservado. Mantener FP32, recursos yguardas actuales. Verificar
continuidad/calidad por escucha; no afirmar equivalencia aún. Así un fallo deldecoder
no exigiría repetir10,6min de generación. No se implementó ni lanzó esta alternativa.

No procede ampliarRAM ni elevar otra vez lasguardas coneste únicoresultado. Ya se
ha demostrado finalizaciónEOS delTalker enFP32 ysu coste, pero resta elWAV yUAT.

### Conservación y validación final02

Todos loshashes deconfigPVE,imagen/ID/inicio/restarts/health deVoicebox, referencia,
original ytranscripción coinciden conbaseline02. Ningún cambio enotrosLXC/CT618/
pipeline. CTqueda3CPU/10GiB/2GiBswap. Trasparada: CPU≈0,009cores, RAMcurrent3,89GiB
(deellosanon0,35GiB,file3,30GiB),swap0,PSI0. Kokoro yPiper figuran descargados ysin
carga; no se hizo nueva síntesis ni se afirma UAT nueva. PerfilEduardo intacto.
Voiceboxhealthy, sinERROR/Traceback/HTTP5xx enelintervalo de logs comprobado.
Exporters35/36 alprimerbarrido: cAdvisorgestoría agotó8s; segunda lectura acotada
HTTP200, sin modificarlo. Prometheus9090 sigue inaccesible comoantes; GrafanaDBok.
No se acredita saludcentral/ausencia dealertas viaPrometheus. CeroOOM nuevos en
host ytodosloscgroups observados. Sin commit/push. Fase7.4 INPROGRESS.

Evidencias02: [Manifiesto](evidence/2026-11-11-d076-02-manifest.json),
[preflight](evidence/2026-11-11-d076-02-preflight.json),
[resultado](evidence/2026-11-11-d076-02-result.json),
[mediciones](evidence/2026-11-11-d076-02-measurements.json),
[etapas](evidence/2026-11-11-d076-02-worker.json) y
[validación final](evidence/2026-11-11-d076-02-final.json).

## Registro histórico del intento01 y aplicación de recursos

## Autorización y cambios reales

Propietario autoriza CT6273vCPU/10GiBRAM/2GiBswap, worker duro9GiB yguarda8,2GiB,
crecimientoSwap128MiB, PSICT5% sostenido10s, OMP/MKL/TORCH3; objetivo55–60s para
vídeos de trading. Sin cambiar Voicebox productivo, otrosLXC, CT618 o pipeline;
sin commit/push. Se conserva Base0.6B/CPU/FP32/SDPA yreferenciaEduardo exacta.

Host verificado: MemTotal33.533.042.688B≈31,23GiB, unos21,9GiB disponibles alinicio.
El aumento físico es real; no se asumió por la instrucción. El host había reiniciado
antes de la intervención; contadoresOOM eidentidades se comparan conbaseline actual,
no conelboot anterior. PSIglobal alto antes del ensayo, pese a abundanteMemAvailable.
Se mide separado dePSICT; no se modifica otro contenedor para corregirlo.

IaC:

- Inventario Voicebox resources.memory10240 yswap2048; main.tf máximo autorizado
  10240,CPU3/disco50 conservados, swap2048 exclusiva deVoicebox; otrosservicios512.
- PlanTerraform guardado yrevisado: solo svc[infra-voicebox], memory/description,
  actualización, sin recreación. No se aplicó mediante elupdate del proveedor.
- BPG0.94.0 marca rebootRequired al modificar memory. Para evitar reiniciarCT se
  aplicó **pctset627 --memory10240 --swap2048** mediante receta versionada
  [resize-live.py](../../services/infra-voicebox/pilot-d076/resize-live.py), con backup
  privado deconfig, invariantes deimagen/ID/inicio/health yhashes deotrosCT.
  [Fuente del proveedor](https://github.com/bpg/terraform-provider-proxmox/blob/v0.94.0/proxmoxtf/resource/container/container.go).
- Cgroup live memory.max10737418240B yswap.max2147483648B verificados. Notes627
  sincronizadas con observación real yuptime; registro7168 previo conservadohistórico.
- Terraform refresh-only revisado sin mutacionesremotas y aplicado para reconciliar
  estado, después plan normal dirigido627 **0cambios**. TerraformvalidatePASS y
  16tests inventarioPASS. No make deploy-all ni apply aotrosCT.

Voicebox conserva imagenD069,mismaID/StartedAt/restarts durante esta intervención,
CPU3/memDocker6200MiB/memswap6600MiB; **no se aumentó la aplicación productiva**.
El nuevo worker es un proceso independiente en la misma imagen con paquete oficial,
no la API ni backendVoicebox. CT627 no se reinició/recreó.

## Preflight y configuración

60s/31muestras, hostdisponiblemín23.447.146.496B≈21,84GiB, PSICT0%,swapCTsin
crecimiento. APIhealthy/model_loadedfalse, referencia privada verificada, ningún
motor inferente residente. Exporters localesNode/cAdvisor responden200 con métricas.
Disco≈19GiB disponibles. Numba/librosa/cachetmpfs yFP32 pasan dentrodelworker.

**Incidencia preexistente de monitorización:** Prometheus192.168.1.110:9090 rechazaba
conexiones antes de lanzar elworker, desde el cliente ydesdePVE. GrafanaAPI/database
responde, pero la salud deldatasourceProm falla. No se reinició ni modificóCT610 ni
ningún otroLXC. La supervisión externaPVE registró recursos yOOM directamente.
36endpointsNode/cAdvisor de18LXC respondenHTTP200 alfinal; eso no acredita scrapes
centrales, alertas, históricos o cadena completa. No declarar59targetsUP sin API.

Worker: hard9GiB/RAM+swap9GiB (sin swapworker),CPU3,rootFSRO,usuario999,rednone,
cacheNumba=/tmp/numba en tmpfs128MiB, modelos/referenciaRO,jobprivadoRW.
OMP_NUM_THREADS=3,MKL_NUM_THREADS=3,TORCH_NUM_THREADS=3 y **torch.set_num_threads(3)**
explícito, interop1. FP32 validado:478tensores main y400codec; SDPA registrado.
Paquetes oficiales qwen-tts0.1.1,torch2.8.0+cpu,transformers4.57.3,accelerate1.12.0.
SnapshotBase0.6B5d83992436eae1d760afd27aff78a71d676296fc; ningún modelo nuevo.

Guardas: workercurrent/RSS8,2GiB,CTcurrent9,5GiB, swapcrecimiento128MiB ytecho1920MiB,
PSICT5%10s, hostdisponible<4GiB,OOMnuevo. PSIglobal se registra; solo es veto adicional
si≥20%10s yMemAvailable<6GiB, para no equiparar PSI deotroscgroups a falta deRAM física.
No se alcanza ningunaguarda en elensayo. Límite duro9GiB yCT10GiB conservados.

Texto de193palabras preparado en [trading-text.txt](../../services/infra-voicebox/pilot-d076/trading-text.txt).
Es una narración genérica sobre contexto, registro y revisión detrading, no una señal
decompra/venta. Se dirige a55–60s por extensión; **duración real no medida porque
no hayaudio**. No se hizo ajuste de tempo, recorte, relleno ni procesamiento ficticio.

max_new_tokens=1024 explícitos, semilla42, lenguaSpanish, ICLaudio+transcripción.
Límite aplicado por mergekwargs→model.generate→talker.generate, registrado enevento.
No son BPE detexto ni todos los codebooks; no convertir llamadasforward a frames.
ReferenciaEduardo24,883s/425caracteres, hashes deloriginal ynormalizada intactos.

## Plazo de cinco minutos y resultado real

La FaseB anterior tenía un máximoexpreso300s. Se solicitó alpropietario ampliar a900s
para la narración larga; no llegó confirmación durante esta intervención. Por tanto
el ensayo se ejecutó con **300s**, sin ampliar silenciosamente elplazo. El control
privado quedó enseconds300; la posibilidad preparada de aceptar900 solo podía
activarse tras respuesta expresa y no se activó. No se lanzó otro intento.

Resultado: **timeout con progreso**, no bloqueo demostrado ni guardaderesursos.
WorkerTimeoutError a295,001s; supervisor final299,907s, PID0/Runningfalse/OOMKilledfalse.
Se mantuvo generación hasta el corte, sinEOS ni secuencia final disponible.

| Medición | Resultado |
|---|---:|
| Carga | 8,576s |
| Preparaciónreferencia, incluidoencode | 15,029s |
| Encode dereferencia | 4,127s |
| Primerforward/prefill | 3,599s |
| InicioTalkergenerate | t=34,083s |
| Último progreso | 368llamadasforward a293,568s |
| Avance aproximado | ~1,42llamadas/s desde inicioTalker, **noTPS definitivo** |
| Tokens finales / EOS | No disponibles/noobservado |
| Decode / escritura | No alcanzados |
| DuraciónWAV /archivo | No existe |
| RSSHWM | 6.001.713.152B≈5,59GiB |
| RSSmáximo muestreado | 5.905.367.040B≈5,50GiB |
| Workercurrent máximo | 6.977.933.312B≈6,50GiB |
| CTcurrent máximo | 8.358.232.064B≈7,78GiB |
| SwapCT /worker | 0/0 |
| PSICTfullavg10 máximo | 0,00% |
| Hostdisponible mínimo | ~17,02GiB |
| CPUworker pico | 2,84cores |
| OOM nuevos | 0 |

368es un contador de llamadas alforward, no la longitud final desequences ni de
acousticcodes. No afirmar368tokens ni29s deaudio. Elavance360→368 en6,17s antes del
corte descarta inactividad total en ese intervalo, no todos los posibles problemas
posteriores. La clasificación cruda del supervisor esF/EXTERNAL_DEADLINE; se
interpreta como timeout con generación activa, no error deimportación ni falloFP32.

Los nuevos recursos yumbrales permiten sostener esta generación parcial sin swap ni
PSI local, pero **no validan el pico deldecoder de60s**, que no se alcanzó. No hay
base para reducir guardas de memoria ni declarar aceptado el audio final.

## Estado y siguiente paso históricos del intento01

CT627 queda3CPU/10GiB/2GiBswap autorizado; worker parado, sin hilosresiduales.
Voiceboxhealthy, mismoID/imagen/inicio, Eduardo/referencia/original conservados,
modelos yvolúmenes intactos. ConfiguracionesPVE ajenas sin cambios; no otrosLXC,
CT618,pipeline ni commits/push. No restaurar automáticamente7GiB trasun timeout deCPU.

**Objetivo55–60s todavía no logrado.** Siguiente paso concreto: confirmar autorización
para **otra ejecución con máximo15minutos**, misma configuración de recursos/texto/
modelo/referencia yguardas; sin ampliarRAMotra vez. Sigue pendiente el plazo, no
se pide de nuevo permiso para losrecursos ya aprobados. No reiniciar Prometheus sin
alcance separado. Mantener su incidencia diferenciada delensayo.

## Evidencias

- [Recursos en caliente](evidence/2026-11-11-d076-resize.json).
- [Preflight](evidence/2026-11-11-d076-preflight.json).
- [Resultado](evidence/2026-11-11-d076-result.json).
- [Mediciones](evidence/2026-11-11-d076-measurements.json).
- [Etapas delworker](evidence/2026-11-11-d076-worker.json).
- [Validaciónfinal yendpoints](evidence/2026-11-11-d076-final.json).

Recetas: `services/infra-voicebox/pilot-d076/`. Planes/estado/backupconfig ylogs
completos privados fueradelrepositorio; sin secretos ni audios personales enGit.
SintaxisPython/JSON, enlaces ydiffcheck validados. Fase7.4 INPROGRESS;
recursosDONE, narraciónBLOCKED por guarda deCT en decoder delintento02; ver resultado vigente arriba.
