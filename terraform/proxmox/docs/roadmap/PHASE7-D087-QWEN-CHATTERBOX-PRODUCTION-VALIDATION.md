# Fase 7.4 — D-087: Qwen bilingüe aceptado; Chatterbox bloqueado

Seguimiento: **13 de noviembre de2026, Europe/Madrid**. Las evidencias técnicas
conservan su UTC original del12nov2026, después de medianoche enMadrid.
**Qwen English: DONE / ACCEPTED para la frase corta. Chatterbox: BLOCKED y deshabilitado.**
Despliegue corregido: DONE técnico. No se ejecutóC ni hubo reintentos.

## Resultado

La imagen corregida está desplegada yhealthy con USER999:999, entrypointreal,
CMDUvicorn y capacidades efectivas/permitidas cero. Qwen funciona con Eduardo en
español/inglés; el propietario escuchóA y confirmó: «Sí, voz y texto correctos».
La aceptación inglesa se limita al ensayo2,56s: no valida narración larga eninglés.

**[Escuchar Qwen English](http://192.168.1.127:17493/audio/d7f2f5da-9dfd-49ea-b7df-678ff1e25b82).**
WAV24kHz/mono/PCM16,61.440muestras,122.924bytes; SHA
`0196b8a5645a0a15f63f44f8142942e57385e74680b7f957b721e7fdcf791c7e`. Coincide con elWAV brutoDecoder: no normalización ni efectos.
El archivo también se conserva fueraPVE en un directorio privado, fueraGit.

ChatterboxSpanish alcanzó la guarda preventiva7GiB de suworker; no produjoWAV.
No huboOOM. CT627 tenía margen: su pico fue12.039GiB frente a19GiB.
Se detuvo la secuencia y se deshabilitó su release sin reiniciar la app ni alterar
Qwen. Los modelosChatterbox y las evidencias se conservan. No existe comparación
acústica entre motores porqueB no llegó a generar audio.

## Autorización y preparación corregida

El propietario autorizó «solucionalo y continua» tras el rollbackD087 y mantuvo
20GiB/guarda19GiB. Se creó intento **d087b**, con nombres nuevos para backup,
staging, contexto ysrc; no se sobrescribió el intento fallido.
Antecedentes: [D087 previo](PHASE7-D087-ROLLED-BACK-HISTORY.md) y
[entrypointUID999](PHASE7-D086-UID999-STARTUP-FIX.md).

La corrección `copy_locked` valida nombres, archivos regulares sin symlinks ySHA,
y copia exclusivamente el release. No recorre indiscriminadamente `__pycache__`;
la copia de contexto también lo excluye y se desactiva bytecode en la transacción.
Se corrigió además el contrato estricto de readiness para incluir los siete
archivos de controller y siete deworker, incorporando guards/supervise de20GiB.
Sin esa corrección, el release completo de recursos se habría rechazado.
Una prueba del heartbeat real con metadata sintética valida ambos idiomas yCBready,
sin cargar pesos. No se eliminó ninguna validación de identidad, idioma o hash.

## Preflight, backup y rollback

- D081healthy antes del cambio, guardas20GiB/19GiB coherentes, CPU3/swap2GiB/root100GiB.
- Sin inferencias ni workers activos; perfil/referencia/checkpoints históricos íntegros.
- Preflight predictivo de ambos motores PASS, hostMemAvailable≥12GiB, PSIlocal0,
  thinpool libre>20%. No se descontó caché como si estuviera recuperada.
- D081imagen, D082datos y D085datos externos releídos y comprobados porSHA.
- D084backup completoHDD18.952.506.863bytes releído: SHA3fa4107c…afcb coincidente.
  Se conserva su extracción verificada histórica; no se afirma un nuevo arranqueDR.
- Backupnuevo `/opt/voicebox/backups/d087b-before-deploy.tar.gz`, **117archivos**,
  SQLiteok/1perfil/1referencia/6WAV, extraído y verificado fueraPVE. SHA:
  `a090fdab2af2ad0932a73bc4d3815a460f0bfb0873bf74ccf509904ae86d536c`.
- CopiaHDD `/mnt/storage/d087b-before-deploy/application.tar.gz`; controller/config/src
  originales enPVE `backups/d087b-before` yHDD `.../controller`.
- Imágenes anteriores ysource originales conservados. No borrados ni limpiezasDocker.

Rollback coordinado preparado:
`python3 /mnt/storage/d087b-staging/transaction.py --attempt d087b --execute --rollback`.
Restaura app/Compose/locks/controller/srcD081, con recursos20GiB/guarda19GiB yaaprobados,
sin restaurarSQLite sobre producción. No fue necesario rollbackD087b: el despliegue
pasó todas las validaciones. Tras fallarB se deshabilitó soloCB, conservandoQwen.

## Configuración desplegada y versiones

| Componente | Versión/configuración |
| --- | --- |
| App/UI/API |sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386|
| App arranque |USER999:999; /usr/local/bin/entrypoint-uid999.sh; CMDUvicornoriginal; CapEff/Prm0|
| WorkerML |sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b|
| Qwen |Qwen3-TTS-12Hz-0.6B-Base; snapshot5d83992436eae1d760afd27aff78a71d676296fc; FP32/CPU/SDPA|
| Qwen parámetros |es→Spanish/en→English; semilla42; referencia/transcripciónoriginal;3hilos; A/B;300/contexto25;1200chars/900s|
| RecursosCT |3CPU/20480MiBRAM/2048MiBswap/rootfs100GiB local-lvmSSD; guarda19GiB|
| Qwenworker |hard9GiB/sinswap; parada8,2GiB; demás controles existentes intactos|
| Chatterbox |MultilingualV3, sourceab55923c27757c90cfcc407baa57dc25a7d25217; modelo5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18|
| Chatterboxworker |FP32/CPU; es/en; semilla42;240chars;400tokens;hard8GiB/sinswap;stop7GiB;300s; ahora deshabilitado|
| Efectos |Robotic,Radio,EchoChamber,DeepVoice disponibles enAPI/UI; no aplicados avoz real|

Dependencias y hashes: [lock](../../services/infra-voicebox/candidate-d085/requirements.lock),
[sources](../../services/infra-voicebox/candidate-d085/sources.lock.json),
[modelos](../../services/infra-voicebox/candidate-d085/models.lock.json) y
[release de recursos](../../services/infra-voicebox/maintenance-d087/release.proposed.json).
No descargas, instalaciones ni reconstrucción deimagen duranteD087b; sinmaster flotante.
D081 permanece conservado como baseline/rollback; la app que corre es21270364…,
no laimagenD08109774c5b…. Español conserva su contratoML y elWAV aceptadoD081.

## Despliegue y validación sin inferencia

Receta: [transaction.py](../../services/infra-voicebox/deploy-d087/transaction.py),
con `--attempt d087b --execute --bundle /mnt/storage/d087b-staging/bundle
--release /mnt/storage/d087b-staging/release.json`.
Prepara archivos/hashes yrollback antes de pausar elagente; activa controller/src
coordinados, esperaheartbeat listo y recrea soloDockerVoicebox. No reinicioCT627.
Compose normalizado solo cambia imagen/build; recursos, mounts, entorno yprivilegios
se conservan. Imagen defectuosa19af4754… no se usa como destino.

Healthreal, UID/GID999, capacidadcero, readinesses/en, perfil, referencias, historial,
los siete audios originales ydescargaD081 PASS. Appno carga modelos; un soloworker.

La prueba `verify-control.py` creó únicamente un proceso sintético `hold` y suhijo,
sin pesos, referencia ni audio. El lock compartido bloqueó un segundo contendiente;
la cancelación dejó PID0/cgroupvacío, eliminó solo sucontenedor efímero y liberó elslot.
Eljob sintético noesUUID yno tiene request/state: elagente no lo trata comogeneración.
RutaAPIcancelar unID inexistente devolvió404 sin modificar historial. No se canceló
ninguna narración delpropietario.

**39tests locales sin inferencia PASS:** D08310Python+4UI, D08511Python+5UI,
D0877recursos/copia+2readiness. Sintaxis, enlaces, inventario, diff yTerraform revisados.
Estos tests no equivalen aaceptaciónacústica; esa aceptación llegó después paraA.

## Ensayos reales: una ejecución por ensayo

| Métrica | A — Qwen English | B — Chatterbox Spanish | C — Chatterbox English |
| --- | --- | --- | --- |
| Estado |DONE / ACCEPTED|FAILED / guarda preventiva|NO EJECUTADO trasB|
| Job |d7f2f5da-9dfd-49ea-b7df-678ff1e25b82|9eca224b-2312-4b1a-9cc0-756c3251e5a4|No existe|
| Texto |This is a test to see if I can speak in English.|Hola, soy Eduardo. Esta es una prueba de mi voz utilizando Chatterbox en español.|Preparado, no enviado|
| CargaTalker |8.829s|No instrumentada porfase antes deparada|No aplica|
| Preparaciónreferencia |17.063s|Subetapa no demostrada|No aplica|
| GeneraciónTalker |27.224s;33tokenssecuencia;1.212tokens/s|Sin resultado de tokens/EOS|No aplica|
| EOS/checkpoint |EOSsí;344×16int64,312ref+32nuevos,checksumvalidado|SincheckpointQwen; motoresincompatibles|No aplica|
| DecoderB |36,370s proceso; sinTalker/encoder;300/25|SinWAV|No aplica|
| Tiempoagente total |124.383s|61.726s|No aplica|
| WAV |**2,56s**, mono24kHzPCM16|No generado|No generado|
| PicoCT muestreado |8.378GiB|12.039GiB|No aplica|
| PicoWorker cgroup muestreado |6.367GiB|7.696GiB|No aplica|
| RSSHWM /RSS observado |Talker5.589GiB HWM; decoder2.251GiB HWM|6.515GiB muestreado; sinHWM final|No aplica|
| CPUworker acumulada muestreada |Talker91.559s; decoder63.565s|35.469s|No aplica|
| SwapCT máximo/delta ensayo |13,465MiB /0|13,465MiB /0; workerswap0|No aplica|
| PSIlocal full avg10 máximo |0%|0%|No aplica|
| OOM nuevo CT/host/worker |0|0|No aplica|
| Procesos liberados |Sí, A antes deBdecoder|Sí, worker terminado|No se creó|

Los tiempos de carga/gen/decode son subetapas; el total incluyeimports, lanzamiento,
verificaciones, guardas ycleanup. El observadorHTTP empezó después delPOST y no se
usa comotiempo total. Los picos anon/file/RSS pueden ocurrir eninstantes diferentes;
no sumarlos como si fueran simultáneos. ParaA hayRSSHWM kernel; paraB solo muestras,
porque la parada preventiva impidió elresultadofinal delworker.

A se envió con `normalize:false`, `effects_chain:[]`, `personality:false`, seed42.
Sucheckpoint confirma **English/en**, referencia original y FP32/Base0.6B. Decoder
leyó elcheckpoint trasfin completoA; no cargóTalker ni encoder. Elcheckpoint yambos
jobs se exportaron privadamente fueraPVE y se verificaron de nuevo porSHA.
No originales devoz niWAV se incorporan aGit.

## Causa demostrada deB y límites del diagnóstico

La parada exacta es **CHATTERBOX_WORKER_7_GIB**. En la misma muestra delpico:

| MemoriaWorker | GiB |
| --- | --- |
| memory.current |7.696|
| anon |4.326|
| file |3.352|
| file_mapped (subconjunto de file) |2.171|
| kernel |0.018|
| RSS |6.515|

**La guarda mide cgroup, no soloRSS.** La suma deanon/file/kernel explica elcontador;
file_mapped no debe sumarse otra vez. No se asume recuperable toda esa memoria.
ElRSS quedó bajo7GiB, pero elcontador agregado delworker lo superó. La muestra
registró7,70GiB antes delkill: la guarda se muestrea y no es un límiteinstantáneo.
El hard8GiB permanece; worker.events max/oom/oom_kill0 y no huboOOM.
HostMemAvailable mínimoB17.493GiB: no se alcanzó la guardaCT19GiB
ni elpiso de memoriahost. **MásRAM delCT no corrige este umbral independiente.**

No se puede demostrar la subetapa exacta carga/referencia/inferencia con la
instrumentaciónCB actual: solo escribe load_seconds/tokens/result alfinal, que
no llegó aescribirse antes delkill. No se declaraEOSfalse ni tiempo decarga0.
Elcódigo fijado `from_local` conserva `t3_state` mientras carga otroscomponentes;
se recomienda investigar copias deweights/mapeos, pero no se atribuye causalidad
exclusiva sin eventos porfase. No se modificó el cargador ni se reintentóB.

Siguiente propuesta, **no implementada**: eventos durables antes/después de cada
componente, referencia, tokens ydecoder; evaluar liberación deestados temporales
ycarga que evite duplicación deparams yweights, manteniendo FP32, hashes yreferencia.
Validar enaislamiento antes de solicitar otroensayoSpanish. No recomendar otra
ampliación deRAMCT ni relajar lasguardas conesta evidencia.

## Estado final, persistencia eIaC

- Apphealthy, USER999/CapEff0, mismoID/inicio después deldespliegue; sinreiniciosextra.
- Qwen es/en listo; inglés corto aceptado por propietario. Español conserva contrato,
  perfil yWAV D081; no se ejecutó otra inferenciaespañolaQwen noautorizada.
- Chatterboxdeshabilitado mediante receipt atómico trasB; no precarga ni otroservicio.
- Robotic,Radio,EchoChamber yDeepVoice presentes; sin procesar vozreal conefectos.
- 105archivos protegidos idénticos;1perfil/1referencia/6históricos intactos.
  Historialfinal8:6previos+Acompleted+Bfailed. C no se envió; sin jobs bloqueados activos.
- Checkpoints históricosD080/D081 y nuevoA íntegros/EOS; evidenciaB preservada.
- Controlador/src/release verificados porhash; grabación/transcripción sincambios.
- 26configsPVE ajenas idénticas (incluidos losotros17LXC); solo Notes627 actualizadas.
- Notes/inventario yTerraform reconciliados porrefresh-only exclusivo627;
  planfinaldirigido **0cambios**, resto delestadoidéntico; sinapplygeneral/deploy-all.
- Prometheusready200, node/cAdvisor627up1, BlackboxVoiceboxprobe1; Grafana3010health200,
  databaseok; ceroalertasFIRING conserviceinfra-voicebox. No se afirma salud deapps ajenas.
- Alfinal CT usa7.618GiB (anon0.356,
  file6.861, kernel0.400); swap13,465MiB,
  PSIlocal0%, high251/max367heredados, OOM0. Pool31.021%libre.
- No otrosLXC/pipeline modificados, nuevosmodelos descargados, borrados, commit/push.

**Intervención detenida después deB.** Qwenbilingüe aceptado dentro delalcance corto;
Chatterbox pendiente deoptimización y nuevaautorización deensayo, sin comparación
acústica posible todavía. No ejecutarC, efectos, narraciones largas ni retries.

## Archivos operativos y evidencias

[Receta/locks](../../services/infra-voicebox/deploy-d087/README.md),
[readiness de recursos](../../services/infra-voicebox/maintenance-d087/readiness.py),
[pruebas completas de heartbeat](../../tests/voicebox/test_d087_readiness.py),
[evidencia final](evidence/2026-11-13-d087b-production-result.json),
[antecedentes D087](PHASE7-D087-ROLLED-BACK-HISTORY.md).
