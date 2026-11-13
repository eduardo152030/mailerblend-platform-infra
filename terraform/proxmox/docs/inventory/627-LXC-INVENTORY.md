# CT 627 — infra-voicebox

Estado: **DONE técnico del alta D063**, con600s/21muestras deestabilidadPASS.
Fecha: 2026-11-10 (Europe/Madrid). [Informe y estado vigente](../roadmap/PHASE7-D063-VOICEBOX.md).

## Chatterbox: entrada1200 desplegada; narración larga pendiente

13nov2026 Europe/Madrid, Fase7.4. Despliegue autorizado después de3987cab:
UI/API/controlador/worker coherentes1200; imagen218dc413… basada en21270364
conservada para rollback. CompilaciónUI y salud/configuración operativa verificadas;
sin suite ni inferencias. Backup180archivos verificado en HDD,12generaciones y
perfil/referencia/historial intactos,11audios verificados. Primer intento revertido
por criterio UI no válido; observador corregido y segundo intentoPASS. Idempotencia
sin escrituras/reiniciosPASS. Voicebox/Qwen/CBes/en saludables; Qwen/efectos,
400tokens/EOS/20sWAV/300s/guardas y recursos sin cambios. Sin CTrestart/otrosLXC/pipeline.
Despliegue DONE; generación completa1200sin validar, la probará el propietario.
[Informe y rollback](../roadmap/VOICEBOX-CHATTERBOX-INPUT-1200.md).
Siguiente: prueba manual del propietario; no ejecutar narraciones automáticamente.

## D089 — DONE / ACCEPTED; cierre del alcance validado Voicebox F7.4

13nov2026 Europe/Madrid. Aceptación acústica explícita del propietario: Chatterbox
español5,48s/inglés5,00s y Qwen inglés45,04s. Qwen español D081 preservado.
Auditoría efectiva solo lectura: Chatterbox240caracteres (UI/API/controlador/worker),
400tokens/EOS obligatorio,300s y WAV≤20s; Qwen1200caracteres. No se amplían límites;
Chatterbox1200caracteres o narraciones largas no demostrados ni incluidos en cierre.
Robotic/Radio/Echo Chamber/Deep Voice disponibles para ambos motores; Eduardo
sin efectos por defecto, perfil sin cadena. Disponibilidad comprobada sin DSP/audio.
Voicebox/Qwen/Chatterbox es/en saludables; configuración productiva intacta.
Publicación normal main autorizada solo para Voicebox/CT627/documentación asociada;
cambios ajenos y datos privados excluidos. F7 global/7.2/7.3 no se cierran.
[Informe D089](../roadmap/PHASE7-D089-CHATTERBOX-PRODUCTION-VALIDATION.md),
[auditoría](../roadmap/evidence/2026-11-13-d089-acceptance-audit.json).
Siguiente: operación/vigilancia; ampliaciones o ensayos nuevos fuera de este alcance.

## D087b — Qwen bilingüe DONE / ACCEPTED; Chatterbox BLOCKED

13nov2026 Europe/Madrid. Despliegue corregido21270364… healthy, USER999:999,
entrypoint real y capacidadescero. Copia soloarchivos delrelease; readinesscompleto
incluye guardas/supervisores. Backupnuevo117archivos restaurado externamente;
39tests sininferenciaPASS. Cancelaciónsintética/sharedlockPASS sin modelos ni audio.
A QwenEnglish: EOS33tokens,checkpoint344×16íntegro,WAV2,56s/124,38s; propietario
escuchó y aceptóvoz/texto. Español conserva contrato y audioD081, sin otra inferencia.
B ChatterboxSpanish: parada worker7GiB; pico cgroup7,70GiB (RSS6,52), CT12,04GiB;
61,73s,sinWAV/OOM. C NOejecutado; sin reintentos. Chatterboxdeshabilitado sin
reiniciarapp; Qwenes/en sigue listo. No elevarmásRAMCT ni guardas automáticamente.
Cuatroefectos disponibles, sinvozreal. Perfil/ref/6históricos intactos; historial8,
105archivos ycheckpoints verificados, nuevosjobs archivados privadamente fueraPVE.
20GiB/3CPU/2GiBswap/100GiB/guarda19 yworkers originales conservados. Notes/TF
refresh-only627, planfinal0cambios; otras26configsPVE idénticas. Prom/Blackbox627up1,
Grafanahealth200, ceroalertasFIRING Voicebox, sinresiduales/otrosLXC/pipeline/commit/push.
[InformeD087](../roadmap/PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).
Siguiente: optimizar/instrumentar memoria delworkerChatterbox antes deotroensayo
explícitamente autorizado. Ingléslargo/Chatterbox/efectos reales no aceptados.
Esta entrada sustituye estados inferiores deD087; D081 conservado comobaseline/rollback.

## D087 — recursos20GiB DONE; despliegue ROLLED BACK / BLOCKED

12nov2026 Europe/Madrid, Fase7.4. Propietario autorizó20GiB y guardaCT19GiB;
aplicados en caliente y reconciliados con Terraform refresh-only exclusivo627,
planfinal0cambios. CPU3/swap2GiB/disco100GiB y workers Qwen9/8,2 y CB8/7 intactos.
Backupnuevo117archivos extraído/verificado fueraPVE; D081/82/84/85 revalidados.
Intento coordinado falló copiando controller/__pycache__, creado por la importación
del preflight. RollbackPASS: D081healthy, mismoID/inicio, agenteactivo, CBdeshabilitado;
ninguna app candidata recreada ni inferenciaA/B/C. Perfil/ref/6WAV/SQLite/checkpoints
intactos; otros26configsPVE idénticos, OOM0. Guarda19GiB permanece aprobada.
Corrección de copia solo local: archivos del release verificados por hash;37tests
sininferenciaPASS. No reintento, efectos, narraciones largas, otrosLXC/pipeline,
commit/push. [InformeD087](../roadmap/PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).
Siguiente: revisión y autorización de nuevo intento coordinado, conservando este
fallido y sus backups; preflight/backup actualizado antes de ejecutarA→B→C.
Aceptación acústica nueva pendiente. Esta entrada sustituye el bloqueo15GiB inferior.

## D087 — BLOCKED antes del despliegue: margen Chatterbox insuficiente

Fase7.4, 12nov2026 Europe/Madrid. Imagen corregida21270364… verificada con
USER999:999/entrypoint corregido/CMD Uvicorn; receta y lockD087 preparados localmente.
PreflightQwen PASS, pero Chatterbox proyecta15,245GiB frente a guarda14GiB:
CTinicial7,745GiB (anon0,366/file6,893/kernel0,485), falta1,245GiB de margen.
HostMemAvailable≈20,6GiB y pool31,03%libre; swapglobal activo, PSIlocal0,
swapCTestable/OOM0. No se presupone caché liberada ni se modifican guardas.
D081healthy, mismoID/inicio, perfil/referencia/6WAV/SQLite intactos,27configsPVE
idénticas.30tests sininferencias PASS. No despliegue, backupnuevo, rollback necesario,
A/B/C, efectos, recursos/otrosLXC/pipeline, commit ni push. Aceptación acústica pendiente.
[InformeD087](../roadmap/PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).
Siguiente: aclarar consumo file/swap con diagnóstico y resolver margen; revalidar
preflight y backups antes de reanudar. No ejecutar ensayos automáticamente.

## D086 — arranque UID999 corregido y validado en aislamiento

Corrección candidata DONE técnica, sin despliegue: imagen21270364… mantiene
USER999:999, entrypoint sin gosu/cambio deusuario yCMDUvicorn original. Caché
interna preparada conpropietario999 enbuild; permisos debinds reales intactos.
Prueba completa conentrypoint/CMD reales healthy, PID1UID/GID999 yCapEff/Prm0;
mismaENV/límites/mounts internos con copias privadas, sinred nipuertos.
30testsPython/UI y14API+8efectos+4DSP sintéticosPASS. D081healthy con mismoID/inicio,
agente/fuentes intactos,111archivos/BD/WAV y27configsPVE sin cambios.
NoinferenciasA/B/C, nodeploy productivo, nirecursos/guardas/otrosLXC/commit/push.
[Informe de corrección](../roadmap/PHASE7-D086-UID999-STARTUP-FIX.md). Siguiente: revisión del resultado antes de
continuar despliegue coordinado yensayos; propuesta anterior deUSERroot descartada.

## D086 — fallo de arranque; ROLLED BACK / BLOCKED

Despliegue candidato19af4754… falló antes deAPI porUSER999 incompatible con
entrypoint heredado que usa gosu. Rollback coordinado completado: D08109774c5b…
healthy, agente/src originales restaurados yChatterbox deshabilitado. Cero
inferencias: A/B/C yefectos NOejecutados por parada crítica. Backupnuevo118archivos
restaurado externamente; D081/82/84/85 revalidados. Perfil/ref/6WAV/111archivos y
27configsPVE intactos; otros17LXC sin cambios,OOM0,swap0,PSIlocal0. Disco100GiB,
59,852GiB libres; pool124,152GiB/31,03%. Reconciliaciónrollback no-op.
[Informe D086](../roadmap/PHASE7-D086-QWEN-CHATTERBOX-VALIDATION.md). Siguiente: autorización nueva para corregir contrato de
startup yvalidarlo aislado conentrypoint real antes de repetir despliegue/ensayos.
No se corrigió ni redesplegó traselfallo. Sincommit/push; D081 ACCEPTED intacto.

## D085 — preparación bilingüe, Chatterbox y efectos DONE; despliegue TODO

Candidato D083 preservado por16hashes. Qwen es/en preparado,1200caracteres,
FP32/0.6B/42 yA/B intactos. Chatterbox MultilingualV3 aislado,240caracteres,
5archivos/2,989GiB verificados y113paquetes fijados; sinVCSflotante. Efectos
Robotic,Radio,EchoChamber yDeepVoice preparados por generación conDSP nativo.
UI completa compila;11Python+5UI D085,14API,8envíos deefectos y4DSP sintéticos PASS;
regresiónD08310Python+4UI PASS. Backupnuevo117archivos restaurado externamente;
D084 completo SHA revalidado. Entorno4,796GiB; quedan60,025GiB enCT y124,155GiB
físicos enpool/31,03%, reserva20%respetada. D081healthy/mismoID/inicio/fuentes,
perfil/ref/6WAV/checkpoints intactos,27configsPVE idénticas yotros17sin cambios.
Sin inferencia real, despliegue, recursos/guardas modificados, commit/push.
[Informe D085](../roadmap/PHASE7-D085-QWEN-BILINGUAL-CHATTERBOX.md). Siguiente: revisión yautorización separada de despliegue
coordinado yensayos cortos A→B→C; calidad/RAM/latenciaCB aún pendientes.

## D084 — ampliación SSD CT627 DONE técnico

Rootfs local-lvm50→100GiB yext4 verificados en caliente, mismoUUID/PID/appsinreinicio.
Disponibles65,494GiB; poollibre124,605GiB/31,14%, reserva20%respetada. Backupcompleto
HDD17,651GiB verificado conextracciónaislada,SQLite/modelos/111archivos/permisos.
Terraformrefresh-only exclusivo627 aplicado; planfinaldirigido0cambios. Otros17LXC
sin cambios,OOM0,perfil/referencia/historial/WAV/checkpoints intactos. D081 sigue
ACCEPTED / PRODUCTION; candidatoD08316archivos conservado. Sin inferencias,descargas,
Chatterbox,reinicios,commit/push. [Informe D084](../roadmap/PHASE7-D084-CT627-SSD-RESIZE.md).
Siguiente: Qweninglés yChatterbox enintervención separada; D084cerrada.

## Antecedente D083 Voicebox — auditoría SSD previa a D084

Prioridad: rootfs62750→100GiB enlocal-lvm/SSD, no mp0HDD. Pool400,086GiB,
usados275,051/libres125,035; metadatos2,794%; VGsinextents, sobreasignación
808→858GiB lógicos. Viable para Docker/Chatterbox previsto, condicionado areserva
global ysnapshots; no es reserva física exclusiva de50GiB. Hotgrowth ext4 soportado,
no ejecutado. [Cifras, procedimientoIaC yrollback](../roadmap/PHASE7-D083-CT627-SSD-CAPACITY-AUDIT.md).
En D083, D081 seguía ACCEPTED / PRODUCTION conrootfs50GiB; imágenes,recursos,guardas,
perfiles ydatos intactos. CandidatoQwenbilingüe ytests conservados; Chatterbox
pausado. No resize,descargas,movimientos,reinicios,inferencias,commit/push.
Propuesta autorizada y ejecutada posteriormente en D084; no aplicar losplanes deauditoría.
Estaentrada es F7.4; elD083 de monitorización inferior esunaintervención separada.


## D082 — D081 ACCEPTED / PRODUCTION; Fase7.4 DONE / ACCEPTED

El propietario escuchó yaceptó voz ycontenido el12nov2026. Referencia final:
1059caracteres,57,36s continuos,total676,18s,EOS ycheckpoint íntegros,picoCT9,625GiB,
sin nuevosOOM. No narraciones5–10min validadas. Mismos recursos/modelo/arquitectura.
Cierre de implementación7.4 DONE / ACCEPTED; publicaciónGitD082 confirmada en
main/origin medianteSHA remoto yverificación productiva sin reinicios. No se cierran otrasfases. [Informefinal](../roadmap/PHASE7-D082-VOICEBOX-FINAL-ACCEPTANCE.md).
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
[Sistema,backups,resultado ylimitaciones](../roadmap/PHASE7-D081-QWEN-CONSOLIDATION.md). Siguiente: escuchar; no másensayos.

### Antecedentes D080

## D080 — recursos DONE técnicos; WAV continuo28,56s generado

12nov2026 Europe/Madrid, Fase7.4 IN PROGRESS. CT62715360MiB RAM ampliada en caliente
mediante recetaIaC yreconciliaciónTerraform; plan exclusivo627, final0cambios.
CPU3/swap2048/disco50 intactos. GuardaCT14GiB, workerhard9GiB/stop8,2GiB.
Preflight predictivoPASS; único job7f348e97… completado, sin segmentación/retries.
EOS358tokens ycheckpoint669×16; WAV28,56s en362,18s. PicoCT8,612GiB,
swap4KiB, sinOOM. Objetivo55–60s aún pendiente; calidad pendiente deescucha.
Perfil y77archivos protegidos preservados; Voicebox/exporters saludables.
[Informe D080](../roadmap/PHASE7-D080-QWEN-15G.md). Siguiente: escuchar elWAV ypreparar una validación60s separada.

### Antecedentes D079

## D079 — corrección desplegada; ensayo BLOCKED por preflight

Seguimiento12nov2026, Europe/Madrid. Fase7.4 **IN PROGRESS**.
Reclamación selectiva de cinco blobs: file reducido1,051445GiB, sin borrados.
Voicebox D079 healthy; admisión predictiva y mensaje de checkpoint corregidos.
36pruebas PASS, segunda aplicación sin recreación. Inicial4,533GiB +4,5 +0,5
proyecta9,533GiB >guarda9,5: **no se cargó Qwen ni se lanzó generación**.
Perfiles, referencia, grabaciones, historial y jobs anteriores conservados.
Recursos/guardas intactos. Siguiente: revisar margen adicional en una intervención
separada; no continuar ensayos automáticamente. [Informe D079](../roadmap/PHASE7-D079-QWEN-CONTINUOUS.md).

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

[Informe D078 yplan seguro](../roadmap/PHASE7-D078-QWEN-DIAGNOSIS.md). Voicebox/agente siguen vivos, pero liveness no
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

[Informe y uso productivo](../roadmap/PHASE7-D077-PRODUCTION.md). Próximo paso: uso de usuario y posterior validación
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

Siguiente paso: revisar [D077](../roadmap/PHASE7-D077-CHECKPOINT-DECODER.md) y autorizar separadamente un único ensayo
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
LXC, CT618 o pipeline; sin commit/push. [Informe D076](../roadmap/PHASE7-D076-LONG-NARRATION.md).
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
**Detenido para revisión.** [InformeFaseB](../roadmap/PHASE7-D075-QWEN-FP32-PHASE-B.md).

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
del diagnóstico antes de inferencia. [Informe FaseA](../roadmap/PHASE7-D075-QWEN-HYPOTHESES-PHASE-A.md),
[limpiezaejecutada](../roadmap/evidence/2026-11-11-d074-execution.json).

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

Detenido para aprobación de **[lista exacta105](../roadmap/PHASE7-D074-CLEANUP-LIST.md)** antes de eliminación;
CT618 requiere permiso separado si se decide aplicar propuesta. [InformeD074](../roadmap/PHASE7-D074-CONTROLLED-MAINTENANCE.md).

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
[Informe D073](../roadmap/PHASE7-D073-CAPACITY-AUDIT.md).

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
WAV y escucha necesarios antes de promover. [Informe D072](../roadmap/PHASE7-D072-QWEN-C.md).

## Histórico D070 — Qwen largo bloqueado, recuperación verificada

11nov2026 (Europe/Madrid). Trabajo largo cancelado: la API dejó un hilo nativo
consumiendoCPU; autorización adicional del propietario permitió reiniciar solo
DockerVoicebox. CT627 no reiniciado, imagen yrecursos sin cambios, perfil y referencia
originales intactos. APIhealthy ysin trabajos activos; CPU enreposo ysinOOM.
Kokoro/Piper comprobados con WAV breves aislados, sin crear perfiles. La aceptación
D069 se limita a su muestra corta; un minuto conQwen no está validado yno se repite.

Solo comparación de alternativasCPU dentro7GiB, sin descarga/despliegue de motores.
Primera candidata propuesta OpenVoiceV2+MeloES, con identidad/acento/tiempo yRAM
pendientes de piloto aprobado. [Informe y mediciones](../roadmap/PHASE7-D070-CPU-ALTERNATIVES.md).
Los apartados inferiores son históricos; fuentes yresultados D069 se conservan.

## Histórico D069 — voz personal exclusivamente

Recursos sin cambios:3vCPU,7168MiB,swap512MiB,50GiB. Único perfil de usuario
Eduardo — Mi Voz, UUID`1fd00418-2a79-4178-883f-af6c3f5e07ee`. Referencia real
ytranscripción confirmada; original privado fueraGit ypersistente enCT627.
Ocho perfiles anteriores retirados con backup recuperable verificado; motores y
catálogos integrados conservados. Futuras voces adicionales fuera del alcance actual.

Base0.6B CPU BF16/SDPA ycodecFP32 genera6,40s en106,86s; cgroup observado5,18GiB,
HWM4,68GiB,swap+5,32MiB,OOM0. Guard corregido porUUID sin quitar comprobaciones
de referencia;1.7B yCustomVoiceCPU bloqueados. Parecido/contenido/acento aceptados
por el propietario para esta primera muestra; no narración60s validada.
[Informe D069 y muestra](../roadmap/PHASE7-D069-PERSONAL.md) ·
[Guía personal](../../services/infra-voicebox/VOICE-PROFILES.md).
Los apartados D068 e inferiores son históricos.

## Histórico D068

**3 vCPU,7168 MiB RAM (7 GiB),512 MiB swap,50 GiB.** Solo memoria627 ampliada por
Terraform, un reinicio ysin recrear el LXC. Imagen PiperR2 fijada porimage-lock;
originalD063 conservada. DockerCPU3,RAM6200MiB yRAM+swap6600MiB (swap400comoantes).

Kokoro/Alex yperfil femeninoPiper es_ES-sharvard F generanWAV reales. Ocho perfiles,
con modeloTTS único, trabajos serializados y409 durante mutaciones de modelo.
Todos los perfiles rechazados ySerena siguen conservados. Personal aún sinperfil
ficticio: incorporaciónWAV privada, Base0.6B guardado yAPI preparados; prueba real
pendiente de grabaciones delpropietario. Acéptese voz/edad/acento solo tras escucha.

Qwen produjo códigos yentró alcodec; protecciones detuvieron probes finitos porPSI
yswap. Pico de cgroup4,97GiB,OOM0. No PruebaA completa,15–30s ni60s; noRTF ni causa
completa de600s demostrada. CustomVoiceCPU bloqueado enoperación, sin forzar másRAM.
La antigua muestra D0635385d04b ausente se recuperó desdebackup conUUID+SHAoriginales,
sinrevertir audiosnuevos; causa no determinada. No se solicitó ningún borrado.

[Informe y evidencias](../roadmap/PHASE7-D068-VOICEBOX.md) ·
[Catálogo con IDs reales](../../services/infra-voicebox/voice-identities.yml) ·
[Grabaciones, clonación y contratoAPI](../../services/infra-voicebox/VOICE-PROFILES.md).
Los cierres inferiores son históricos; prevalece D068.

## Cierre histórico D067

**3 vCPU,3072 MiB RAM,512 MiB swap,50 GiB.** Se ensayaron6144 MiB y se restauró
la configuración anterior al fallar Qwen por timeout600s en la frase corta, sinWAV.
Pico cgroup4,22 GiB incluida parada, RSS3,03 GiB, swap4 KiB, ceroOOM. No hubo
pruebas de30/60s ni aceptación de Qwen. Candidata parada, imagen original/Kokoro
activa. Los perfiles y referencias persisten tras recrear Docker; Alex y candidato
masculino generan audio. Siete perfiles, sin borrados; candidata femeninaSerena
sinmuestra, bloqueada. Personal sinperfil ficticio, procedimiento preparado y
Base0.6B aún sinvalidar. Otros17CT intactos;59targetsUP yGrafana comprobado.
[Informe y mediciones](../roadmap/PHASE7-D067-QWEN-6G.md),
[catálogo deidentidades](../../services/infra-voicebox/voice-identities.yml),
[grabación, clonación y contratoAPI](../../services/infra-voicebox/VOICE-PROFILES.md).
Los apartados D066/D063 inferiores son históricos; prevalece este estado.

## Cierre histórico D066

Recursos actuales: **3 vCPU, 3072 MiB RAM, 512 MiB swap, 50 GiB**. El piloto
CustomVoice 0.6B usó temporalmente 4096 MiB, con backup y rollback automático.
Carga BF16/SDPA PASS; generación corta detenida por umbral preventivo a 3,54 GiB
de cgroup, sin OOM. No se completó audio Qwen ni se ensayaron 60 s.
La imagen original continúa en producción, con Kokoro y Alex verificados mediante
nueva generación. Candidata parada, imagen y caché Qwen conservadas solo en el
área aislada del piloto; no se instalaron modelos Qwen en la caché de producción.
Observación posterior 180 s/7 muestras PASS; otros 17 CT sin cambios.

Alex aceptado por el propietario. Dora/Santa/Emma D064 están rechazados, pero sus
perfiles y muestras siguen conservados; tampoco se elimina el perfil original
D063. [Informe, mediciones e identificadores exactos](../roadmap/PHASE7-D066-QWEN-PILOT.md).
Los apartados D063 inferiores describen el cierre original; prevalece este estado.

## Arquitectura y recursos

Proxmox pve → LXC627 privilegiado, plantilla106 → Docker Compose → Voicebox 0.6.0
web/API → PyTorch CPU → Kokoro 82M. Servicio permanente AI / Voice Generation.
Ubuntu 22.04.5 LTS amd64; Docker 29.0.2 y Compose 2.40.3 observados.
3 vCPU, **7168 MiB RAM**, 512 MiB swap, 50 GiB local-lvm; sin GPU/passthrough.
Se comenzó con 1080 MiB de la plantilla. La carga inicial saturó RAM/swap y provocó
timeout de monitorización; 1536 MiB permitió TTS pero dejó solo un 13,7% disponible.
El siguiente escalón de 2048 MiB dejó alrededor del 30% disponible, sin cambiar F5.
El provider 0.94 reinicia el CT al cambiar memoria: ambos reinicios fueron solo627.
La Intel HD530 del nodo no acredita compatibilidad de aceleración con Voicebox.

Contenedor test-nginx heredado de plantilla conservado en8080 IPv4/IPv6; no se
utiliza como healthcheck ni como prueba de Voicebox.

## Red, puertos y acceso

192.168.1.127/24, vmbr0, gateway/DNS 192.168.1.254.
Web y API: http://192.168.1.127:17493. Exporters: 9100 Node y 8085 cAdvisor.
CT627 no existía antes del alta. La IP no coincidía con inventario ni configuración
PVE y no respondió a ping/ARP; esto no prueba una exclusión de rango DHCP.
No se creó dominio, NAT WAN ni configuración de reverse proxy.

LAN autorizada inicial 192.168.1.0/24. Regla DOCKER-USER específica para el destino
original 192.168.1.127:17493, aplicada solo en dirección ORIGINAL y persistida por
voicebox-lan-only.service. El primer candidato sin dirección bloqueó respuestas;
se sustituyó exclusivamente esa regla y se validó el acceso real desde administración.
No autenticación entrante acreditada en Voicebox; CORS y ClientId no la sustituyen.
Una futura exposición exige autenticación, autorización, TLS y límites de peticiones.

## SSH y plantilla

Bootstrap D062 por consola pct exec confiable. Clave pública del propietario añadida
sin eliminar otras claves, sshd -t/-T y acceso por clave antes/después de endurecer.
PasswordAuthentication=no, KbdInteractiveAuthentication=no y root prohibit-password.
Known_hosts propio del bundle obtenido mediante PVE estricto; nunca keyscan como
verificación ni cambios en la configuración SSH del propietario.
Incidencia: la plantilla incluye una clave DSA obsoleta. El selector ahora la excluye,
conservando sus archivos y las identidades admitidas. Se recuperó el bootstrap y se
retiró el taint solo627 tras PASS, sin reemplazarlo. Consola y rollback conservados.

## Código, Docker y variables

Fork https://github.com/eduardo152030/voicebox, revisión
8af7efe62fab8d33e2a5dfbedabaa45f68a5184f. Fork y upstream anunciaban el mismo HEAD al
consultar; no se presupone igualdad futura. Checkout /opt/voicebox/source sin parches
backend/frontend. IaC en [services/infra-voicebox](../../services/infra-voicebox/README.md).

Imagen local/voicebox:8af7efe62fab-cpu-d063, ID exacto y archivo exportado fijados en
image-lock.json. Bases por digest, torch/torchaudio CPU 2.8.0 y espeak-ng. Los rangos
pip upstream no garantizan builds futuros idénticos: la reproducción exacta usa la
imagen archivada y validada, no un nuevo build con dependencias flotantes.
Compose: restart unless-stopped, 3 CPU, 1600 MiB RAM, 2000 MiB RAM+swap y logs 10 MiB×3.
Variables centralizadas: cloud desactivado, OMP/MKL dos hilos, caché Numba persistente,
telemetría HF desactivada y HF_HUB_OFFLINE=1. No se requieren secretos nuevos;
ninguna clave privada ni token se incorpora a Git o al contenedor de aplicación.

## Persistencia y modelos

/srv/voicebox/data → /app/data: SQLite, perfiles, muestras, configuración y audios.
/srv/voicebox/huggingface → caché Hugging Face: pesos, voces y referencias fijadas.
Perfil preset español «Prueba IaC español D063», voz Dora ef_dora. También se precargan
em_alex y em_santa. Modelo hexgrad/Kokoro-82M,
revisión f3ff3571791e39611d31c381e3a41a3af07b4987, pesos 327212226 bytes y tres voces
aproximadamente 0,5 MB cada una. model-lock.json registra tamaños y hashes LFS.
Pesos Apache2.0 según la ficha oficial; conservar atribuciones y condiciones del origen.
Otros motores visibles en UI no se consideran descargados, probados ni aceptados.

## API y futura integración con Pipeline_videos_modulares

No se modificó elpipeline. El contrato vigente ylos comandos están en
[VOICE-PROFILES](../../services/infra-voicebox/VOICE-PROFILES.md). Selección por
`personal`/`male_es`/`female_es`, UUID real, engine apropiado ytexto enespañol.
`POST /generate` devuelveID; consultar `GET /history/{id}` hasta completed/failed
 yrecuperar `GET /audio/{id}`. No repetirPOST después detimeout sin reconciliarID.
Piper emitePCM16mono22050Hz, Kokoro24000Hz; leer lacabecera. Gestionar409 de motor
ocupado ylos erroresdeltrabajo. Un modelo cargado oHTTP200 no demuestraTTS.
Personal conIDnull se bloquea, nunca se sustituye por unapreset. La clonaciónBase
requiere las grabaciones reales; el catálogo no inventa unaidentidad delpropietario.

## Salud, observabilidad y aceptación funcional

GET /health: JSON status=healthy y backend_variant=cpu. Acredita API, no inferencia.
model_loaded de ese endpoint se refiere al backend predeterminado Qwen: no usarlo
como prueba de Kokoro. La inferencia tiene evidencia independiente de audio real.
Node1.10.2 nativo, CPU cgroup textfile cada5s y collector.cpu desactivado; RAM LXCFS.
cAdvisor0.60.6 por digest, namespaces verificados y socket containerd read-only solo627.
Uptime real desde exporter PVE; no node_boot_time_seconds del host físico.

Alta aditiva de targets y regla627 en Prom610 y módulo JSON en Blackbox616, con backup
coordinado, promtool/parser y recargas sin reinicios. 18 Node/18 cAdvisor/19 Blackbox UP;
56 targets anteriores idénticos y 17 configuraciones PVE conservadas por hash.
Fleet y Details seleccionan627 en navegador sin modificar sus dashboards.
Los catálogos locales se alinearon con los catálogos vivos antes de añadir627: el diff
Git incluye etiquetas CPU ya desplegadas, sin modificar esas etiquetas en producción.

Primer intento1080 MiB conservado como failed en historial, no presentado como éxito.
Tres generaciones completadas: 26,98s a1536 MiB; 15,40s y 12,94s a2048 MiB, todas con
el texto solicitado y WAV de6,46s. Audio final recuperable mediante el enlace del informe.
Perfil/audio previos conservaron identificadores y hash tras reinicio controlado.
No se afirma escucha/UAT humana, prueba de otros motores ni nuevo ensayo Telegram.

## Backup, restauración, actualización y rollback

Capturas privadas en /opt/voicebox/backups/ y copia fuera del CT en el equipo de
administración, directorio privado mailerblend-recovery/new-lxc/voicebox-d063.
Backup coherente con SQLite backup y sin generaciones activas, datos, configuración y
modelos. Restauración aislada comprobada: hashes de25 archivos, cinco enlaces internos,
integridad SQLite y tres audios completados. Se preservó también el intento fallido.
Imagen exportada aparte: 1206316979 bytes; manifiesto y 22 blobs OCI verificados.
No se ha cargado esa exportación sobre el runtime activo ni realizado restore completo
sobre otro LXC. Un primer ensayo del filtro tarfile3.10 rechazó enlaces HF legítimos;
el verificador confina cada destino, rechaza devices/hardlinks y valida hashes.

Despliegue: /opt/voicebox/deploy.sh, solo627; exige imagen/Dockerfile aprobados.
Si falta imagen, indicar VOICEBOX_IMAGE_ARCHIVE; comprueba hash antes de docker load.
Estado/logs y pasos detallados en [runbook del servicio](../../services/infra-voicebox/README.md).
Actualizar: nuevo candidato/commit/tag/lock, backup, conservar imagen anterior y recrear
solo Voicebox. Rollback con imagen previa y datos compatibles; migraciones SQLite
requieren restauración coordinada. Nunca down -v, prune ni destroy automático.
Recuperación Terraform tainted según [runbook de altas](../runbooks/NEW-LXC-PROVISIONING.md),
sin reaplicación que reemplace el CT. RPO/RTO/retención global siguen pendientes F7.3.

## D-088 Voicebox y autorización condicional D-089

13nov2026 Europe/Madrid. Dos cargas autorizadas consumidas; candidata FP32 carga
en38,88s, RSS máximo4,557GiB frente a6,556GiB original. Reducción por assign=True
verificada sin cambiar pesos. Producción Qwen es/en intacta y Chatterbox deshabilitado.
D089 BLOCKED: no hay mediciones de activaciones/generación/decoder que acrediten
margen. No despliegue ni audio. Propuesta pendiente de autorización: ensayo aislado
instrumentado bajo guardas originales. Informe: [D088](../roadmap/PHASE7-D088-CHATTERBOX-MEMORY-OPTIMIZATION.md). Sin commit/push.
