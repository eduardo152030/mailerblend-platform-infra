# Fase 7.4 — D075: segunda opinión Qwen, Fase A de diagnóstico

Seguimiento posterior: [Fase B, intento único con error de preparación antes de
cargarQwen](PHASE7-D075-QWEN-FP32-PHASE-B.md). No se obtuvo benchmarkFP32 niWAV.
El informeFaseA inferior se conserva como evidencia histórica.


Estado: **DONE — diagnóstico y microbenchmark; Fase B TODO / no ejecutada**.
11nov2026, Europe/Madrid. Incluye cierre de la limpieza D074 expresamente aprobada.
Sin carga de Qwen, nueva generación, cambios de recursos, reinicios, modificación de
CT618/cAdvisor u otros LXC. Sin commit/push. La frase «ejecutar generación Qwen todavía»
se interpreta como «no ejecutar todavía», coherente con «Solo diagnóstico» y la parada
solicitada antes de Fase B. D075 es identificador de seguimiento de esta Fase A.

## Conclusión

**BF16 es funcional, pero muy lento en este PyTorch/i5 sin instrucciones BF16 nativas.**
El microbenchmark confirma el coste para estas operaciones: 10,48–146,33× frente aFP32
en matrices y44,19× en conv1d. Es evidencia fuerte para la lentitud del backend
oficial, **no un factor de aceleración garantizado de todo Qwen**. Tampoco explica
por sí solo D072: ese motor es C, cuantiza matrices aINT8 y usa rutas AVX2/FMA propias.

Además, Voicebox no pasa un límite de tokens a generate_voice_clone y el snapshot
real contiene **max_new_tokens8192**, mucho más permisivo de lo apropiado para una
prueba corta CPU. Es una configuración operativa mejorable, no prueba de ausencia deEOS.
El intento C deD072 sí tenía312frames como máximo y se cortó por el supervisor con
último progreso50frames; no demostró fuga de tokens ni fallo del decoder.

La explicación más probable del historial oficial es **alto coste de cómputo BF16
sin aceleración, combinado con límites de trabajo demasiado amplios y cancelación
API ineficaz del hilo nativo**. ParaC siguen pendientes los costes por etapa de
referencia/Talker/CP/decoder y su solapamiento. No hay una causa única demostrada para
ambos motores ni una prueba de falta deRAM. Ninguna optimización se aplica hoy.

## Hipótesis de Claude

| Hipótesis | Evidencia real | Estado |
|---|---|---|
| 1. BF16 sin aceleración adecuada | i5AVX2/FMA sinAVX512_BF16/AMX; PyTorch capabilityAVX2/nativeBF16false; microbenchmark BF16 mucho más lento | **CONFIRMADA para operaciones PyTorch probadas**; contribución exacta al modelo pendiente |
| 2. Exceso de tokens/sin finalizar | Backend no pasa max_new_tokens; generation_config real8192. C D072: límite312frames, último50; no conteo final D070 ni EOS medido | **CONFIRMADO límite oficial excesivamente permisivo; PENDIENTE generación sinEOS** |
| 3. Sobreconcurrencia de hilos | PyTorchOMP/MKL2; C -j2 yBLASserial en ejecución; Docker cpu.stat0throttled. Interop4 disponible no implica cuatro tareas activas; C solapa decoder | **No confirmada; DESCARTADA configuración obvia de muchos hilos BLAS en D072**, perfil dinámico pendiente |
| 4. Confundir cgroup con pagecache | Tras limpieza: anon0.225GiB,file3.192GiB,kernel0.365GiB. memory.current incluye todos; RSS no equivale a ellos | **CONFIRMADA la distinción necesaria**; no toda cache se libera inmediatamente |
| 5. Referencia demasiado larga | Referencia24,883s válida, mono24kHzPCM16,425caracteres exactos; C usa303frames de referencia y467posiciones de prefill | **PENDIENTE como cuello de rendimiento; DESCARTADA incompatibilidad de formato/duración** |
| 6. Backend o decoder defectuoso | D069 completaWAV ycronometra codec33,37s; D070 cancelaciónAPI no para hilo. C tiene decoder concurrente yguarda WAV alfinal; D072 no finalizó | **CONFIRMADO defecto operativo de cancelación oficial; PENDIENTE bug de decoder/calidad/backend C** |

## 1. Hardware y límites efectivos

Intel Core i5-6500, Skylake,4núcleos físicos/4hilos,1socket, sinSMT. AVX2 yFMA sí;
AVX512_BF16,AVX512_VNNI,AMX no. DMI:2módulosDDR4 de8GB, DIMM1/ChannelB y
DIMM3/ChannelA,2133MT/s configurados. Hay módulos en ambos canales; DMI no mide el
modo de interleaving activo ni el ancho de banda real. No se ha ejecutado prueba de
memoria ni se presume una cifra deGB/s.

CT627: cpuset efectivo **0–2**, memory.max7GiB yswap.max512MiB. CPUmax delLXC:
`max 100000` — sin cuotaCFS adicional, limitado por ese cpuset. DockerVoicebox:
`cpu.max=300000 100000`, acceso0–2, cuota3CPU. Estos cores no son exclusivos delCT;
otros huéspedes comparten el host. Se precisa el diagnósticoD073 que describía
CT3vCPU genéricamente como cuota: aquí se separan cpusetLXC y cuotaDocker reales.
Docker memoria6200MiB yMemorySwap6600MiB, valores conservados. No ampliar nada.

Driver intel_pstate, gobernador performance, rango800–3600MHz. Muestra final:

| CPU | MHz instantáneos | Gobernador |
|---|---:|---|
| cpu0 | 3583.9 | performance |
| cpu1 | 1029.5 | performance |
| cpu2 | 1198.8 | performance |
| cpu3 | 3454.4 | performance |

Los contadores core/package thermal_throttle son0 antes ydespués de la ventana.
CPUstatDocker nr_throttled0/throttled_usec0. No evidencia de throttling térmico/CFS;
frecuencia baja puntual en reposo no lo prueba. No se midieron MSR/power-limit durante
cada operador, por loque no se excluyen todas las limitaciones eléctricas/transitorias.

## 2. PyTorch real y microbenchmark sin Qwen

Ejecutado mediante dockerexec de proceso diagnóstico en **la misma imagen y entorno
VoiceboxD069**, sin importar Qwen ni instanciar modelos. PyTorch **2.8.0+cpu**, qwen-tts
**0.1.1**, CPUcapabilityAVX2, MKL2024.2/oneDNN3.7.1/OpenMP4.5 disponibles.
Entorno realOMP_NUM_THREADS=2/MKL_NUM_THREADS=2; OPENBLAS_NUM_THREADS no definido.
Torch inicial intraop2/interop4. Solo el proceso debenchmark ajusta interop1/intraop2;
no cambia los valores del procesoAPI ni sus variables/configuración.

Datos sintéticos, semilla42, torch.inference_mode, conversiones deentrada fuera de
la región cronometrada,2warmups y5mediciones por dtype. Ordenalternado enmatmul.
Mediana milisegundos,5muestras pequeñas, no benchmark de modelo completo:

| Operador / dimensiones M,K,N o entrada | FP32 ms | BF16 ms | BF16/FP32 |
|---|---:|---:|---:|
| mm [1, 1024, 1024] | 0.1872 | 1.9616 | 10.48× |
| mm [64, 1024, 1024] | 0.9723 | 117.2909 | 120.63× |
| mm [512, 512, 512] | 1.6586 | 242.7004 | 146.33× |
| conv1d [1, 64, 256] | 0.0673 | 2.9721 | 44.19× |

Todos los resultados finitos; erroresL2 registrados para mm. PicoRSS del proceso
**224.73MiB**. Límites del proceso CPU45/50s yalarma60s, envoltorio
65s; acabó normalmente, sin hilos/modelos residentes nuevos. No descarga, cambios de
imagen ni archivos deaudio. El coste relativo varía con forma ybackend: el ratio de
146× no se extrapola a un minuto deQwen.

La documentación primaria dePyTorch explica las rutas aceleradas BF16 con
AVX512_BF16/AMX y conversiones aFP32 para otras operaciones. La funcionalidadCPU
BF16 no implica aceleración enAVX2. [Documentación PyTorch](https://pytorch.org/blog/empowering-pytorch-on-intel-xeon-scalable-processors-with-bfloat16/).
Cambiar todoQwen aFP32 duplicaría ciertos pesos y puede exceder el margen con
activaciones/códec: **el microbenchmark no autoriza ni demuestra esa carga en7GiB**.

## 3. Motor C utilizado en D072

Commit **ef339be58a778b062e1c14382347964552eae007**, imagen
`sha256:03dadc9a464031613f05080d0d860749fe4a696bd5d0583da41d93edf226a305`, binario
SHA256 `04f4bce57f28449bb485e5ec9d6acf80d846851b1e08ffa9f885878241318de6`.
Fuente fijada fueraCT preservada; se retiró solo el contexto público decompilación
aprobado. ConsultaAPI deupstream actual devuelve el **mismo commit**,25sep2026UTC.
No se ha actualizado imagen/código. [Repositorio](https://github.com/gabriele-mastrapasqua/qwen3-tts).

Inspección de qwen_tts_talker.c/qwen_tts_code_predictor.c/main.c/qwen_tts.c y
caps/dispatch/logsD072, no nueva carga:

- **Talker INT8 real:** proyecciones Q/K/V/O,gate_up/down de28capas, cuantización
  per-rowabsmax desdeBF16; head/embeddings yauxiliares no todosINT8.
- **CodePredictor INT8 real:**5capas,15lm_heads ymtp_proj según rutaINT8. El códec
  safetensors permaneceFP32; speakerencoder ybuffers tienen otrosformatos.
- **INT4:** existen ramas Q4_0 para Talker yCP, con dimensiones dinámicas compatibles
  con múltiplos32 deBase0.6B. El help aún dice Talker1.7B-only. No se ha validado
  con carga/audioBase0.6B: soporte por código plausible, no éxito demostrado. En
  ciertos auxiliares la rutaINT4 conservaINT8/BF16/FP32, no cuantiza todoelmodelo.
- **AVX2 efectivo:** compilaciónportable `-mavx2 -mfma`, caps ydispatchD072 en eli5:
  dotINT8 widen/dequant+FMA, sinVNNI; prefillBF16→FP32+SGEMM/OpenBLAS. No es el
  mismo matmulPyTorchBF16 que mide el microbenchmark.
- **Hilos:** D072 CLI-j2, entornoOpenBLAS/OMP2; presupuestoCLI resuelveBLASserial
  ypoolengine particionado. Hay un hilo dedecoder solapado desde elinicio, incluso
  sin flagstream. El número dehilos existentes no equivale a coresactivos; falta
  perfil porhilo durante una futura inferencia para valorar competencia real.
- **Clonación:** `--ref-audio` y`--ref-text` activan ICLcompleto; xvector-only por
  defecto cuando no se da reftext, **no es loque se usó**. NoCustomVoice/graft.
- **Límites:** defaultCLI8192frames, pero D072`--max-duration25` lo sustituye por
  int(25×12,5)=312frames; outerdeadline240s, cortehostPSI~123s. EOSv1ramp desde
  frame258 para los43tokens detexto. Último progreso50/312, sin prueba de runaway.

El decoder consume códigos en un hilo concurrente yacumula audio internamente;
CLIoffline escribe elWAV alfinal de qwen_tts_generate, después de finalizar/join.
Por tanto, **noWAV parcial no demuestra que decoder no se haya ejecutado o esté roto**.
El log final de tiempos tampoco existe si el supervisor mata antes. Una variante
QWEN_NO_OVERLAP desactiva solapamiento por presencia devariable; comparar fases
sería útil pero aún no se ejecuta. No activar una palancaexperimental en producción.

Palancas memoria localizadas: QWEN_PREFILL_QUANT/QWEN_FREE_BF16 para reducir
representacionesduplicadas; el upstream marcaFREE_BF16 experimental/fuera delregistro,
no una configuración desplegable automáticamente. MADV_DONTNEED no garantiza
liberar inmediatamente toda cachecgroup. INT4, recorteKV o códec reducido requieren
compatibilidad ymedición específica; no son soluciones validadas por estos datos.

## 4. Memoria y cache, antes/después del trabajo

Tras limpieza ybenchmark, snapshot15:43:37UTC:

| Contador CT627 | Valor |
|---|---:|
| memory.current | 3.785GiB |
| memory.stat anon | 0.225GiB |
| memory.stat file | 3.192GiB |
| memory.stat kernel | 0.365GiB |
| memory.swap.current | 413.02MiB |
| memory.pressure fullavg10 | 0,00% |
| PSIhost fullavg10 | 0,03% |
| OOM nuevos | 0 |

La relectura de variosGiB debackups para revalidar integridad cargó cache yprovocó
reclamación local: swapCT aumentó desde~60MiB históricos hasta~413MiB. También
crecieron eventosmemory.max, sinOOM. **Es un coste deesta auditoría, no una inferencia
Qwen ni una fuga demostrada delAPI**. No se ha ocultado como memoria gratis ni se ha
forzado swapoff/drop_caches/reinicio para restaurar cifras. No modificar archivos
comprimidos retenidos para expulsar cache fuera del alcance105. Comprobar margen y
swap dinámico antes deFaseB; página swappeada puede permanecer ahí aun conRAM libre.

filecache no es todo inmediatamente recuperable: páginas activas/mapeadas/sucias,
slab, charge decgroup yIO condicionan su recuperación. No restar file entero de
memory.current para fabricar un presupuesto seguro. A la inversa, current no es RSS
ni memoria anónima deQwen. La limpieza de disco no prueba caída proporcional deRAM.
No se modifica ni investiga de nuevoCT618; se conservan límites6273CPU/7GiB/512MiB.

## 5. Referencia personal preservada

Original SHA2560d068f05…920fe,PCM16estéreo48kHz27,861s; normalizada
SHA2567b388a91…7dd4,PCM16mono24kHz24,883s. Permisos0600,uid999; archivos persistentes
intactos. Transcripción425caracteres idéntica entre API yarchivo privado confirmado
por el propietario; no se publica texto ni grabación. Esto comprueba integridad y
consistencia, no repite ASR ni altera la aceptación previa. Original no recortado.

C admite24kHz yusa por defecto hasta30s; toda la referencia normalizada cabe. Se
recortan internamente~0,59s de cola segúnD072, sin cambiar el archivo en disco.
Ref303frames yprefill467posiciones: su coste adicional es plausible ymedible, no un
error de formato. PyTorch usa ref_audio+ref_text yx_vector_only_mode=False; C también
ICLcompleto. No vocesficticias/terceros niCustomVoice para clonar identidad.

## Configuración mejorable y prueba mínima de Fase B — solo propuesta

1. **Oficial:** no heredar8192tokens para frases cortas. Pasar un límite explícito
   proporcional al texto ywalltimeout con cancelación deproceso efectiva, conservando
   la distinción EOS/limite/timeout. No se ha demostrado defectoEOS.
2. **CPU:** BF16 dePyTorch es una mala elección de rendimiento en estas operaciones
   aunque reduzca almacenamiento. Preferir evaluar CINT8/CPU o precisión mixta
   justificada; no cargarFP32 completo a ciegas ni aumentarRAM.
3. **Medir por fases ypor hilos:** tiempo de referencia, prefill,Talker/CodePredictor,cola/join y
   chunks decoder, tokens/frames reales,motivo deparada,RSS/cgroupanon/file/kernel,
   swap/PSI/CPU; nunca contenido devoz ni tokensdetexto privados en logs públicos.
4. **Prueba mínima futura:** una frase de~3s con la misma referencia/transcripción,
   Base0.6BCINT8,j2,semilla42,cap~100frames/8s,deadlinefinito/cancelación externa,
   untrabajo ysinmotorproductivo residente. Registrar resultadoaunque corte y no
   confundir cap con lectura completa. Antes, preflight de margen/swap trasestaauditoría.
5. Solo si esa prueba funciona, comparar una variable por vez: decoder sin solape,
   memoriaexperimental o cacheICL real verificada. Para evaluar longitud de referencia,
   una **copia derivada privada** con segmento/transcripción exactos requiere un plan
   deFaseB; nunca sobrescribir/recortar eloriginal ni cambiar variascosas a la vez.

No FaseB, generación ni nueva carga ejecutada. No se da ganador defidelidad ni se
promete recuperar Qwen por solo esta tabla. Se detiene para revisión de resultados.

## Cierre D074 aprobado y verificación final

Se retiraron **105/105** elementos:61rutas y44cacheIDs exactos del manifiesto
SHA256d2396813…fc8b00. Espacio disponible **7.056→18.997GiB**,
incremento **11.941GiB**. Byteexactos yIDs en evidencia.
No imágenes/contenedores/modelos/volúmenes/comprimidos ni datosvivos borrados.

Incidentes de preflight, sin borrar antes de resolver: la verificación SQLiteD074
había creado0B-WAL/32KiB-SHM enexpansiones; DB yarchivosretendidos intactos yhashes
idénticos. Se comprobó que eran las únicas2diferencias yse corrigió lectura con
immutable=1. Unhelperunattended-shutdown inactivo se distinguió de una tareaAPT real
porlocks/procesos. El primer filtrobooleano decache seleccionó0registros; selector
exclusivo de44IDs convalidaciónShared/InUse retiró los44. No limpiezaDocker global.
No ampliar la aprobación original ni reutilizar la lista para una segunda limpieza.

Voiceboxhealthy, mismoID/imagen/StartedAt/restarts, perfilEduardo ygrabacioneshash
conservados; logs275líneas desde15:00UTC:0ERROR/Traceback/HTTP5xx. K/P ymodelos
conservados, disponibilidad porAPI; no nuevas inferencias.59targetsUP con18Node y
18cAdvisor; alerta de disco resuelta,0alertas actuales. Grafana/databaseok, dashboards
Fleet/Details disponibles yconsulta por proxy aPrometheus para627 correcta.
27configuracionesPVE idénticas albaseline,0OOM nuevosglobal/cgroups. Ningún cambio
CT618/cAdvisor,otrosLXC,pipeline,recursos oservicios. Fase7.4 permanece INPROGRESS;
D074limpiezaDONE,FaseADONE yFaseBno iniciada. Sin commit/push.

## Evidencias

- [Limpieza D074 ejecutada](evidence/2026-11-11-d074-execution.json).
- [Hardware ymemoria](evidence/2026-11-11-d075-hardware-memory.json).
- [MicrobenchmarkPyTorch](evidence/2026-11-11-d075-torch-microbenchmark.json).
- [Referencia yruntime](evidence/2026-11-11-d075-reference-runtime.json).
- [ValidaciónPrometheus/Grafana/servicio](evidence/2026-11-11-d075-final-validation.json).

Scripts en `services/infra-voicebox/diagnostic-d075/`; ninguna función cargaQwen.
Archivosfuente instalados se inspeccionaron enprivado, no se publican grabaciones ni
transcripción. SintaxisPython/JSON/enlaceslocales/diffcheck comprobados; no test de
inferencia inventado. FuentesC contrastadas conupstream actual ycommitD072 exacto.
