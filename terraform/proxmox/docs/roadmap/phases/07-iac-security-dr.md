# Fase 7. IaC Reliability, Security & Disaster Recovery
## IA-CHAT-SWAP-631 — DONE técnico

Fase 7. Swap631 ampliada mediante YAML/script versionado de1024 a1741MiB (~1,7GiB),
autorización expresa del propietario, incluido commit/push. PVE/cgroup/Node/Prometheus
verificados; uso observado~58,8% tras ampliar cuota, RAM4096MiB conservada.
WebUI health200; contenedores intactos, sin reinicios, OOM0. Segunda aplicación
sin escrituras; plan Terraform acotado no-op conTLS,16tests inventario yvalidatePASS.
Notes631 sincronizadas, ficha/generados/README actualizados. Solo631 modificado;
sin627,otrosCT,swapoff ni apply general. Amplía cuota, no swap física delhost.
Siguiente: observar uso habitual; Fase7 global IN PROGRESS, pendientes heredados
conservados. [Informe](../IA-CHAT-SWAP-631.md).


## IA-CHAT — documentación y publicación autorizadas (13/11/2026)

Fase 7; documentación DONE y publicación principal DONE, verificada en origin/main. El propietario autoriza
commit y push del alcance IA-CHAT, sustituyendo la prohibición anterior solo para
esta publicación. Cambios ajenos permanecen fuera. Se documentan los 8192 tokens
de Gemma, el presupuesto compartido y el uso de chats cortos/temáticos, carpetas y
búsqueda; estas no amplían la memoria del modelo. Ampliación de contexto TODO, sin
despliegue: resumen, recuperación, slots u otro perfil requieren pruebas y alcance
autorizado. [Plan](../IA-CHAT-CONTEXT-PLAN.md). No cambios productivos ni CT627.
Publicación verificada: commit principal `2d945b0`, 37 pruebas PASS, Terraform validate,
inventario y revisión de secretos PASS. README operativo sincronizado.
Siguiente: caso largo del propietario y comparación del plan de contexto;
Fase 7 global IN PROGRESS. No despliegues ni cambios de configuración en este cierre.



## IA-CHAT-LATENCY — DONE técnico (13/11/2026 22:33 CET)

Fase 7. IaC Reliability, Security & Disaster Recovery continúa IN PROGRESS global.
Este resultado sustituye los pendientes de ejecución de latencia anteriores;
no acepta ni dispensa UAT, restauración o alertas heredadas.

Desplegado y comprobado exclusivamente630/631. Gemma, ruta UI real con stream:
344,401s antes →3,571/1,410/1,477s en tres turnos;2peticiones/mensaje →1.
Prompt5324tokens más título314 →60/96/134; cache0/77/112, mismo slot.
Qwen:4,193/4,039/2,634s, cache0/75/120, mismo slot. Objetivo<=10s PASS.
Idle3600:300,779s sin inferencias, mismoPID/RSS17,97GiB; saludo posterior1,609s.
Fecha correcta viernes13/11; búsqueda por botón PASS con3URLs yuna llamada LLM,
49,434s por recuperación/lectura785tokens. Consulta literal larga inicial sin
resultados preservada como fallo; con query-generationOFF usar términos breves.

Matriz r3 completa; Gemma b2048/ub512 yQwen b512/ub512. Prueba real3000tokens:
TTFT177,204/139,371s, picos18,095/19,219GiB (<19,8GiB). Qwen3000 empeora respecto
alos133,432s iniciales; no se oculta esa variación. Repack no repetido sin margen.
Gemma contexto16384total/8192por conversación conSWAcompleta; Qwen65536/32768.
6314096MiB aplicados, RAG/STT concurrentesPASS, sinOOM. max jerárquico delímite
cAdvisor256MiB; max local delCT=0. No certifica contexto lleno/multiusuario.

Fuentes canónicas INI/Jinja/selección, Compose/perfilAPI, YAML, Notes630/631,
fichas/índice yREADME operativo PVE actualizados. Segunda aplicación sin escrituras,
recargas, reinicios nirecreaciones; Terraform acotado no-op conTLS verificado.
37testsPASS, terraform validate, generador ydiff-checkPASS. CPUcgroup/RAM4GiB yhealth
verificados; integraciónGrafana previa conservada, sin cambios a610/611/616.
Usuario/Knowledge/token técnicos retirados, JWT401; propietario ydatos originales
preservados, SQLiteok. 27configuraciones protegidas intactas. CT627 no intervenido;
swap deotrosCT sololectura desdehost. Sin commit/push.

Siguiente: revisión del propietario del perfil/contexto yUAT móvil/voz; reservasDHCP,
restauración funcional yrecepción humana Telegram siguen sin verificar. No hay
autorización nueva para otrosCT ni rolloutF4. [Informe vigente](../IA-CHAT-LATENCY-2026-11-13.md).


## IA-CHAT-LATENCY — reanudación y selección validada (13/11/2026, Europe/Madrid)

IN PROGRESS. Matriz completa r3 de ambos modelos: 12 combinaciones y 24 comandos,
pp512/pp2048 a4h, tg128 a3h. Gemma b2048/ub512, Qwen b512/ub512; validación real
3000tokens PASS bajo guarda90%: picos18,095/19,219GiB. TTFT177,204/139,371s;
Qwen no mejora su prueba larga anterior133,432s pese a mejorar llama-bench.
Tres turnos UI Qwen4,193/4,039/2,634s, cache0/75/120tokens. Gemma final, fecha,
búsqueda y300s idle en ejecución. WebUI Compose reconciliado solo631, health200;
SearXNG/cAdvisor sin recreación. Perfil API ysegunda aplicación sin escrituras,
reaplicación llama/Compose/jobs sin reinicios,27configuraciones protegidas intactas.
Terraform630/631 no-op conTLS verificado; Notes actualizadas yverificadas.
Sigue pendiente retirar cuenta/token técnicos ycerrar informe con pruebas finales.
No627 ni otrosCT modificados; swapotrosCT sololecturahost. Sin commit/push.


## IA-CHAT-LATENCY — medición inicial y corrección de caché (13/11/2026)

Fase7 IN PROGRESS. Baseline UI real:5324tokens,344,401s hasta primer delta;
segunda petición de título314tokens (1reutilizado/313procesados). Herramientas
nativas por defecto desactivadas:43tokens y1,362s. Títulos/tareas y consultasOFF:
1petición/mensaje,0,444s con prefijo caliente. Idle3600 aplicado.

Gemma:template canónico preserva prefijo vacío de pensamiento desactivado ySWA
completa; contexto16384total/8192por slot para respetar RAM, frente a65536anterior.
Qwen mantiene65536total. Tres turnos UI:2,835/1,546/1,200s; caché0/60/243tokens,
mismo slot. Cambio de capacidad comunicado durante ejecución; no RAMextra630.
6314096MiB aplicados en vivo y declarados enYAML; no restartWebUI. RAG/STT PASS,
picoresidente2,510GiB. OOM0; delta jerárquicomax90 atribuido a cAdvisor256MiB,
contador local del límiteCT=0. Prueba3000tokens sin caché:Gemma185,868s/Qwen133,432s.

Matriz de benchmarks r3 en curso;630router detenido de forma acotada durante pruebas,
631 activo. Selección final, fecha/weekday,5minidle,idempotencia yretiradafixture
pendientes. Solo630/631 modificados; swapotrosCT sololecturahost. No627,commit/push.
[Informe](../IA-CHAT-LATENCY-2026-11-13.md).


## IA-CHAT — Notes e inventarios de 630/631 completados (2026-11-13)

Fase 7. IaC Reliability, Security & Disaster Recovery; tarea IA-CHAT-NOTES DONE.
Identificados en PVE activo y YAML:630 infra-llm y631 infra-webui. Los seis CT activos
fuera del inventario son servicios distintos, no candidatos de este despliegue.
Notes canónicas ampliadas siguiendo la estructura de627 y fichas individuales
completadas con observación real fechada, recursos/red/montajes/apps/persistencia/
healthchecks/monitorización/backups. Notes previas útiles conservadas.
Generador existente actualizado en sus salidas (JSON/manifiesto/índice); fuentes
individuales canónicas, sin cambiar el mecanismo de generación.

Aplicación exclusiva del campo description/Notes en630/631 mediante API PVE con
digest y backup privado; igualdad byte a byte verificada. Resto de configuración,
otros CT e identidades de servicios intactos; sin reinicios, redespliegue, apply
Terraform ni commit/push. CT627 solo referencia documental local, no intervenido.
SearXNG running sin healthcheck Docker: se distingue de healthy.

No verificados: reservasDHCP, dominio/TLS/ACL-WAN efectivas, UAT móvil/voz,
administrador actual del propietario, restauración funcional, ejecución del backup
semanal630 y recepción humana Telegram. Backup631 manual con integridad verificada
previamente y existencia/tamaño reconsultados; no nuevo ensayo de restauración.
Siguiente: propietario completa esos pendientes; Fase7 global sigue IN PROGRESS.
Evidencias: `evidence/ia-chat-2026-11-13/notes-live-audit.json` y
`notes-sync-applied.json`/`notes-sync-verified.json` en la misma carpeta.


## IA-CHAT — integración desplegada y estabilidad PASS (2026-11-13, Europe/Madrid)

Fase 7. IaC Reliability, Security & Disaster Recovery; complementos de Fases 4 y 6.
Implementación y pruebas técnicas DONE: CT 630/631 adoptados en Terraform sin
recreación, plan acotado no-op y 18 entradas anteriores del estado intactas.
YAML y configuración canónica por servicio, inventario individual/global y Notes
actualizados. CPU cgroup y RAM LXCFS verificadas; Node Exporter nativo en ambos,
cAdvisor solo en 631 y cinco targets nuevos. Prometheus/Blackbox integrados de
forma aditiva; Grafana Fleet/Details contempla cAdvisor N/A en 630.

PASS: 600 segundos / 21 muestras sin anomalías, 136 consultas reales de Grafana,
reinicio de ambos CT, autenticación, chat, visión, thinking, búsqueda, RAG e historial.
Segunda aplicación sin escrituras de configuración, recargas ni reinicios.
Backup final de 631 verificado por SHA256/zstd/tar; README operativo en PVE.
27 hashes de configuración PVE protegidos iguales; CT 627 no intervenido.
Sin commits ni push.

Voz funcional con calidad limitada: small/int8, 4 de 5 palabras correctas en el WAV
sintético (WER 20 %). Con RAG/STT y exporters, 631 alcanza 2,69 GiB residentes /
2,85 GiB de working set; propuesta de 4096 MiB sin aplicar, límite de 3072 MiB
conservado. Cuenta y Knowledge técnicos retirados; primer administrador disponible.

Aceptación completa IN PROGRESS: reservas DHCP, administrador y UAT móvil/voz del
propietario. Restauración funcional y recepción Telegram FIRING/RESOLVED de las
nuevas cadenas no realizadas. No declararlas aceptadas bajo el contrato F4 ni cerrar
la Fase 7 global. Siguiente paso: propietario reserva DHCP, crea su administrador,
prueba voz/móvil y valora el margen de RAM; coordinar después la aceptación de
alertas de 630/631. [Informe vigente](../IA-CHAT-EXECUTION-2026-11-13.md).



Estado: **IN PROGRESS**. Actualizado: 2026-11-13 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)


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
[Informe y rollback](../VOICEBOX-CHATTERBOX-INPUT-1200.md).
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
[Informe D089](../PHASE7-D089-CHATTERBOX-PRODUCTION-VALIDATION.md),
[auditoría](../evidence/2026-11-13-d089-acceptance-audit.json).
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
[InformeD087](../PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).
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
commit/push. [InformeD087](../PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).
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
[InformeD087](../PHASE7-D087-QWEN-CHATTERBOX-PRODUCTION-VALIDATION.md).
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
[Informe de corrección](../PHASE7-D086-UID999-STARTUP-FIX.md). Siguiente: revisión del resultado antes de
continuar despliegue coordinado yensayos; propuesta anterior deUSERroot descartada.

## D086 — fallo de arranque; ROLLED BACK / BLOCKED

Despliegue candidato19af4754… falló antes deAPI porUSER999 incompatible con
entrypoint heredado que usa gosu. Rollback coordinado completado: D08109774c5b…
healthy, agente/src originales restaurados yChatterbox deshabilitado. Cero
inferencias: A/B/C yefectos NOejecutados por parada crítica. Backupnuevo118archivos
restaurado externamente; D081/82/84/85 revalidados. Perfil/ref/6WAV/111archivos y
27configsPVE intactos; otros17LXC sin cambios,OOM0,swap0,PSIlocal0. Disco100GiB,
59,852GiB libres; pool124,152GiB/31,03%. Reconciliaciónrollback no-op.
[Informe D086](../PHASE7-D086-QWEN-CHATTERBOX-VALIDATION.md). Siguiente: autorización nueva para corregir contrato de
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
[Informe D085](../PHASE7-D085-QWEN-BILINGUAL-CHATTERBOX.md). Siguiente: revisión yautorización separada de despliegue
coordinado yensayos cortos A→B→C; calidad/RAM/latenciaCB aún pendientes.

## D084 — ampliación SSD CT627 DONE técnico

Rootfs local-lvm50→100GiB yext4 verificados en caliente, mismoUUID/PID/appsinreinicio.
Disponibles65,494GiB; poollibre124,605GiB/31,14%, reserva20%respetada. Backupcompleto
HDD17,651GiB verificado conextracciónaislada,SQLite/modelos/111archivos/permisos.
Terraformrefresh-only exclusivo627 aplicado; planfinaldirigido0cambios. Otros17LXC
sin cambios,OOM0,perfil/referencia/historial/WAV/checkpoints intactos. D081 sigue
ACCEPTED / PRODUCTION; candidatoD08316archivos conservado. Sin inferencias,descargas,
Chatterbox,reinicios,commit/push. [Informe D084](../PHASE7-D084-CT627-SSD-RESIZE.md).
Siguiente: Qweninglés yChatterbox enintervención separada; D084cerrada.

## Antecedente D083 Voicebox — auditoría SSD previa a D084

Prioridad: rootfs62750→100GiB enlocal-lvm/SSD, no mp0HDD. Pool400,086GiB,
usados275,051/libres125,035; metadatos2,794%; VGsinextents, sobreasignación
808→858GiB lógicos. Viable para Docker/Chatterbox previsto, condicionado areserva
global ysnapshots; no es reserva física exclusiva de50GiB. Hotgrowth ext4 soportado,
no ejecutado. [Cifras, procedimientoIaC yrollback](../PHASE7-D083-CT627-SSD-CAPACITY-AUDIT.md).
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
main/origin medianteSHA remoto yverificación productiva sin reinicios. No se cierran otrasfases. [Informefinal](../PHASE7-D082-VOICEBOX-FINAL-ACCEPTANCE.md).
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
[Sistema,backups,resultado ylimitaciones](../PHASE7-D081-QWEN-CONSOLIDATION.md). Siguiente: escuchar; no másensayos.

### Antecedentes D080

## D080 — recursos DONE técnicos; WAV continuo28,56s generado

12nov2026 Europe/Madrid, Fase7.4 IN PROGRESS. CT62715360MiB RAM ampliada en caliente
mediante recetaIaC yreconciliaciónTerraform; plan exclusivo627, final0cambios.
CPU3/swap2048/disco50 intactos. GuardaCT14GiB, workerhard9GiB/stop8,2GiB.
Preflight predictivoPASS; único job7f348e97… completado, sin segmentación/retries.
EOS358tokens ycheckpoint669×16; WAV28,56s en362,18s. PicoCT8,612GiB,
swap4KiB, sinOOM. Objetivo55–60s aún pendiente; calidad pendiente deescucha.
Perfil y77archivos protegidos preservados; Voicebox/exporters saludables.
[Informe D080](../PHASE7-D080-QWEN-15G.md). Siguiente: escuchar elWAV ypreparar una validación60s separada.

### Antecedentes D079

## D079 — corrección desplegada; ensayo BLOCKED por preflight

Seguimiento12nov2026, Europe/Madrid. Fase7.4 **IN PROGRESS**.
Reclamación selectiva de cinco blobs: file reducido1,051445GiB, sin borrados.
Voicebox D079 healthy; admisión predictiva y mensaje de checkpoint corregidos.
36pruebas PASS, segunda aplicación sin recreación. Inicial4,533GiB +4,5 +0,5
proyecta9,533GiB >guarda9,5: **no se cargó Qwen ni se lanzó generación**.
Perfiles, referencia, grabaciones, historial y jobs anteriores conservados.
Recursos/guardas intactos. Siguiente: revisar margen adicional en una intervención
separada; no continuar ensayos automáticamente. [Informe D079](../PHASE7-D079-QWEN-CONTINUOUS.md).

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

[Informe D078 yplan seguro](../PHASE7-D078-QWEN-DIAGNOSIS.md). Voicebox/agente siguen vivos, pero liveness no
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

[Informe y uso productivo](../PHASE7-D077-PRODUCTION.md). Próximo paso: uso de usuario y posterior validación
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

Siguiente paso: revisar [D077](../PHASE7-D077-CHECKPOINT-DECODER.md) y autorizar separadamente un único ensayo
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
LXC, CT618 o pipeline; sin commit/push. [Informe D076](../PHASE7-D076-LONG-NARRATION.md).
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
**Detenido para revisión.** [InformeFaseB](../PHASE7-D075-QWEN-FP32-PHASE-B.md).

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
del diagnóstico antes de inferencia. [Informe FaseA](../PHASE7-D075-QWEN-HYPOTHESES-PHASE-A.md),
[limpiezaejecutada](../evidence/2026-11-11-d074-execution.json).

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

Detenido para aprobación de **[lista exacta105](../PHASE7-D074-CLEANUP-LIST.md)** antes de eliminación;
CT618 requiere permiso separado si se decide aplicar propuesta. [InformeD074](../PHASE7-D074-CONTROLLED-MAINTENANCE.md).

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
[Informe D073](../PHASE7-D073-CAPACITY-AUDIT.md).

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
WAV y escucha necesarios antes de promover. [Informe D072](../PHASE7-D072-QWEN-C.md).

## D070 — narración personal larga: IN PROGRESS / Qwen BLOCKED

Cancelación y recuperación DONE con reinicio soloVoicebox autorizado; CT627 y
datos preservados. Kokoro/Piper ymonitorización verificados. ComparaciónCPU DONE,
OpenVoiceV2+MeloES solo propuesta; nuevo motor/piloto no autorizado. D069 mantiene
su aceptación de muestra corta. [Informe D070](../PHASE7-D070-CPU-ALTERNATIVES.md).

## D069 — alcance vigente: exclusivamente voz personal

7.4/D069 DONE — Accepted para primera muestra personal. Perfil real Eduardo — Mi Voz conservado; ocho perfiles adicionales
retirados con backup restaurado. Primera muestra Base0.6B real6,40s/106,86s,
aceptación auditiva expresa del propietario. Narración larga no probada. No ampliarRAM, otrosLXC ni pipeline;7.2/7.3 conservan
su estado fuera de alcance. [Informe D069](../PHASE7-D069-PERSONAL.md).

## D068 — 7 GiB y dos voces operativas; Qwen bloqueado

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
[Informe y evidencias](../PHASE7-D068-VOICEBOX.md).

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
Qwen; no recomendar másRAM ni promover esta candidata. [Informe](../PHASE7-D067-QWEN-6G.md).

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
[Informe](../PHASE7-D066-QWEN-PILOT.md).

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

[Diagnóstico/recomendación](../PHASE7-D065-QWEN-OPTIMIZATION.md),
[catálogo/resultadosD064](../PHASE7-D064-VOICES-QWEN.md).
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
CPU antes de descargas/cargas. [Informe](../PHASE7-D064-VOICES-QWEN.md).


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

[Informe y17criterios](../PHASE7-D063-VOICEBOX.md),
[resultado](../evidence/2026-11-10-d063-result.json),
[inventario627](../../inventory/627-LXC-INVENTORY.md).
SinUAT/escucha humana ni nuevoensayoTelegram; no se amplían dispensas anteriores.
API sin autenticación integrada acreditada, restringida porreglaLAN; otrosmotores,
concurrencia, rangoDHCP/retención yDRglobal pendientes. Primer intento1080MiB fallido
conservado en historial, seguido de tres audios completados. Sin commit/push.
Fase7 globalINPROGRESS;7.2/7.3 OUTOFSCOPE. Siguiente: uso interno/revisión del
propietario; integración futura delpipeline requiere intervención separada.

## Antecedente D062 — anterior a D063

Implementación local DONE, aceptación real PENDING VERIFICATION. Bootstrap integrado
con key gate antes del endurecimiento, conservación de claves, rollback/consola,
15 tests provisioning,14 inventario, dos mocks y parser OpenSSH PASS.
[Informe](../PHASE7-D062-SSH.md). No crearCT ni cambiar producción/17CT/passwords;
no commits/push. Próximo: permiso para primer ensayo real. 7.4 conserva READY.

## Estado vigente de subfases — numeración del propietario

| Subfase | Estado | Alcance |
|---|---|---|
| 7.1 Git Consolidation | DONE | D061: cinco commits principales publicados, origin/main sincronizado; cierre documental separado |
| 7.2 Security Hardening | OUT OF SCOPE | Decisión expresa; no DONE ni rotación de secretos históricos |
| 7.3 Disaster Recovery | OUT OF SCOPE | Decisión expresa; no DONE ni política global DR nueva |
| 7.4 Automated LXC Provisioning | DONE / ACCEPTED — D082 | Alta D063 yQwen personal continuo≈1min D081 aceptados por propietario; fuentes yrecuperación documentadas |

[Informe D061](../PHASE7-D061-EXECUTION.md),
[runbook de altas](../../runbooks/NEW-LXC-PROVISIONING.md).
7.4 no equivale al ID históricoF7-04, que trata secretos. Las tareas históricas
inferiores conservan sus antecedentes; no autorizan ejecutar7.2/7.3 en esta sesión.
El cierreD042 solo cubría aquella publicación, no estos cambios posteriores.

## Objetivo

Cerrar las diferencias entre reproducibilidad declarada y operación real, con seguridad y recuperación sostenidas.

## Alcance y dependencias

Herramientas fijadas, CI, inventario/estado, SSH/TLS, secretos, backups, retención y restauraciones periódicas. Trabajo de fiabilidad de aplicaciones heredado que requiera alcance específico.

Dependencias: Inventario real, resultados F3/F4 y decisiones del propietario sobre seguridad, retención, RPO/RTO y ventanas.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F7-01 | Consolidar commits curados y documentación de cambios previos | DONE | D042: monitorización curada publicada; apps ajenas preservadas fuera de alcance; [evidencia](../evidence/2026-11-06-git-consolidation.json) |
| F7-02 | Eliminar dependencia de promtool/amtool en /tmp | TODO | Versiones y checksums reproducibles, sin usar latest |
| F7-03 | Idempotencia/readiness y backups para todos los deploys | TODO | Prom/CRM/EVA tienen mejoras; deploy-cadvisor-all sigue usando rm -f |
| F7-04 | Retirar/rotar secretos heredados y proteger estado Terraform | TODO | .env nuevo ignorado no resuelve perm.env/tfstate/tfvars ya rastreados |
| F7-05 | Revisar SSH/TLS/privilegios y autenticación de métricas | TODO | Terraform insecure y opciones SSH heredadas; no modificadas ahora |
| F7-06 | Definir DR sostenido, retención, RPO/RTO y ensayos periódicos | TODO | Restauraciones F3 pasadas no equivalen a una política continua |
| F7-07 | Corregir digest EVA y dependencia apk de su arranque | TODO | Heredados; requiere revisión funcional y aprobación de cualquier cambio de imagen/comando |
| F7-08 | Revisar RAM temporal CRM y deriva de inventario/discos | TODO | No reducir ni aplicar Terraform general automáticamente |
| F7-09 | Automatizar validación local/CI y continuidad del roadmap | IN PROGRESS | D059: documentación consolidada y APIs contrastadas; CI y política de commits pendientes |

## Implementación, validación, despliegue y aceptación

No iniciada como intervención global. Se reconocen mejoras parciales anteriores, sin convertirlas en aceptación de toda la fase.

## Riesgos

Estado Terraform puede contener secretos; no publicarlo. Limpiar Git no revoca credenciales. TLS/SSH mal migrados bloquean accesos. Un apply general puede cambiar otros servicios. No reducir RAM CRM sin evaluar carga y posible reinicio del proveedor.

## Entregables

Cadena de herramientas reproducible, validaciones CI, procedimientos seguros, inventario contrastado y política DR con pruebas periódicas.

## Criterios de aceptación

Herramientas instalables con versiones/checksums fuera de /tmp; pruebas CI; secretos nuevos y heredados gestionados; planes acotados sin deriva inesperada; segundos despliegues sin cambios; backups externos restaurados según RPO/RTO aprobados; rollback y control de acceso ensayados. No cumplidos globalmente.

## Evidencias y referencias

- [README](../../../README.md), [Makefile](../../../Makefile), [main.tf](../../../main.tf).
- [Deploy Prom](../../../services/infra-prom/deploy-prom.sh), [deploy común](../../../scripts/deploy-common.sh), [cAdvisor heredado](../../../scripts/deploy-cadvisor-all.sh).
- [Backups/restauración F3](../../../services/infra-prom/PHASE2-EXECUTION.md).
- [DECISIONS](../DECISIONS.md), [AGENTS](../../../AGENTS.md).


## D-042 — consolidación Git

Preparación histórica: 2026-11-06 (Europe/Madrid). F7-01 entonces IN PROGRESS, autorizado commit/push normal de
cambios seguros. Respaldo privado verificado;230tests, validadores Prom/AM, enlaces
y diff --check PASS. Estados/credenciales locales preservados y excluidos del
índice; secretos históricos pendientes de rotación (F7-04 no DONE). Sin producción.
[Auditoría, alcance y pendientes](../GIT-CONSOLIDATION-D042.md).

Cierre D042: push principal confirmado, main/origin iguales (0/0); F7-01 DONE
solo para consolidación de monitorización. F7 global IN PROGRESS y F7-04 pendiente.
Árbol residual preservado, sin aceptar cambios de aplicaciones. Ver evidencia D042.

## Seguimiento D059

F7 global IN PROGRESS; F7-01 DONE solo para el conjunto publicado D042. El árbol
actual tiene trabajo posterior y cambios ajenos sin consolidar, sin nueva
publicación ni sincronización remota afirmada. Documentación actualizada, APIs
leídas y enlaces locales comprobados; no despliegues ni aceptación de seguridad/DR.
[Informe](../DOCUMENTATION-D059-REVIEW.md). Siguiente: revisión F6 y autorización
específica del pendiente elegido; sin commits/push.

## Handoff D060 — F6 cerrada

2026-11-10: F6DONE; nueve dashboards IaC, providers/mountsGrafana saneados ymisma
imagen fijada enrecipe, sin recrear activo. Persistencia ensayadaaisladamente.
Esto no cierra seguridad/secretos/CI/DR global ni publica el trabajo posteriorD042.
[InformeF6](../PHASE6-D060-CLOSURE.md). Próximo: elegir yautorizar un pendienteF7;
no intervención productiva ni commits/push autorizados por ese cierre.

## Cierre D061

2026-11-10:7.1 DONE, publicación normal SSH verificada;7.4 READY FOR FIRST REAL
PROVISIONING TEST, con mocksDocker/nativo ysin creación real.7.2/7.3 OUT OF SCOPE
por decisión, nunca DONE. Los estados históricos de deuda no autorizan ejecutarlas.
No nuevosCT/apps/DNS/recursos ni despliegues productivos; cambios funcionales ajenos
conservados. Próximo: definir yautorizar primerCTreal, no ejecutado por este cierre.
[Informe](../PHASE7-D061-EXECUTION.md), [Git](../evidence/2026-11-10-d061-git-published.json).

## D-088 Voicebox y autorización condicional D-089

13nov2026 Europe/Madrid. Dos cargas autorizadas consumidas; candidata FP32 carga
en38,88s, RSS máximo4,557GiB frente a6,556GiB original. Reducción por assign=True
verificada sin cambiar pesos. Producción Qwen es/en intacta y Chatterbox deshabilitado.
D089 BLOCKED: no hay mediciones de activaciones/generación/decoder que acrediten
margen. No despliegue ni audio. Propuesta pendiente de autorización: ensayo aislado
instrumentado bajo guardas originales. Informe: [D088](../PHASE7-D088-CHATTERBOX-MEMORY-OPTIMIZATION.md). Sin commit/push.
## IA-CHAT-A — preflight autorizado — IN PROGRESS

13 de noviembre de 2026 (Europe/Madrid). Fase 7. IaC Reliability, Security & Disaster Recovery; subproyecto IA local, Fase A (la «Fase 1» del encargo no renumera el roadmap). Solo lecturas PVE/API pública, hashes y plan local. No crear CT, instalar, descargar pesos, cargar modelos ni modificar CT existentes/627/red/storage.cfg. Parada obligatoria tras plan, B–F requieren confirmación. Sin commit/push.

### IA-CHAT-A — resultado BLOCKED

13nov2026 Europe/Madrid. Qwen y mmproj ausentes de la ruta declarada en PVE; hashes locales imposibles. Parada aplicada sin crear/modificarCT. Plan parcial630/631, IP230/231 pendientes DHCP, Gemma Unsloth14,249GB seleccionado por metadatos; Debian12 en catálogo/no descargado. MemAvailable22,42GiB puntual, red100Mb/s. Versiones/compatibilidad aún incompletas; no declarar A DONE. [Informe y evidencias](../IA-CHAT-PREFLIGHT-2026-11-13.md). Sin despliegue/inferencia/commit/push. Siguiente: aclarar ruta Qwen, completar preflight y pedir confirmación antes de B–F. Fase7 global IN PROGRESS; pendientes ajenos conservados.


## IA-CHAT A–F — reanudación autorizada — IN PROGRESS

13nov2026 Europe/Madrid. El propietario sustituye bloqueo por ausencia de pesos:
autoriza descarga en630, altas630/631 DHCP, volúmenes96GiBSSD, instalación,
compilación, benchmarks/validaciones, reinicios solo nuevosCT, backups/jobs propios,
README /root/ia-local y reservas MikroTik exclusivamente si acceso existente.
627 excluido por completo; exclusión de uso manual/riesgo aceptado, sin mecanismos.
Sin cambios otrosCT/storage.cfg/redhost ni commit/push. Guardas: parar SHA tras
dos intentos, MemAvailable<21GiB antes de cargas, afectación fuera alcance o
aceptación sin solución interna. No pedir permiso entre fases. IPs antiguas propuestas
230/231 descartadas: usar DHCP y reserva si acceso existente; si no, comandos al dueño.
Siguiente: completar A y ejecutar B–F condicionado a guardas; no repetir otros trabajos.

### IA-CHAT — compatibilidad Docker en631

Runtime runc actual rechaza sysctl dentro deLXC conAppArmor antiguo (lxc-pve6.0.0-1). Se prepara OCI crun1.31 oficial/SHAfijo y registro exclusivoDocker631; elección de implementación dentro delCTnuevo. No actualización delhost, no cambiosAppArmor/seccomp ni CTexistentes, no downgrade. Validación pendiente; no afirmar resuelto.

### IA-CHAT — excepción AppArmor631 aprobada

13nov2026 Europe/Madrid. Tras falla real tanto runc como crun1.31, propietario
autoriza expresamente `lxc.apparmor.profile: unconfined` SOLO631 y reinicio deeseCT.
Mantener unprivileged/namespaces/seccomp; pérdida deAppArmor exterior aceptada
solo631, sin extender aotrosCT ni modificar perfiles/paquetes globales. Volver
a runtimeoficialrunc. Crun queda evidencia deintento/no configuración activa.
B–F siguen autorizadas conguardas originales; implementación/validación pendientes.

### IA-CHAT — ajuste interno de memoria de llama.cpp

Primer benchmarkGemma interrumpido(SIGINT/rc130), no válido: repacking por defecto
duplica pesos, RSS≈21,2GiB ymemory.high en630; sinOOM, swap630≈0,76GiB yhost
≈7,12GiB frentea2,47previos. No modificar otrosCT ni swapglobal. Se desactiva
repacking (`--repack 0` enbench, `no-repack=true` enpreset), mmap ybatch512/ubatch128.
Repetir solo benchmarks incompletos conguarda21GiB, sin ampliar recursos.

### IA-CHAT — B DONE; C/D IN PROGRESS

Cuatro pesos verificados al primer intento; volumen630 RO/backup0 y plantillaDebian12.
630/631 creados, IP DHCP67/66 yreservas pendientes delpropietario. Primerbenchmark
válido Gemma3h:pp51216,395t/s,tg1287,961t/s sinrepacking. ExcepciónAppArmor631
aprobada/aplicada ySearXNG JSON10resultados; WebUI noarrancado aún. E/F TODO.
[Informe vigente](../IA-CHAT-EXECUTION-2026-11-13.md); siguiente: completar benchmarks/router/WebUI/backups/aceptación
con guardas, sin627/otrosCT ni commit/push. Fase7 global IN PROGRESS.

### IA-CHAT — contexto Qwen reducido según guarda90%

Chat inicial correcto, pero RSSrouter+hijoQwen19,8195GiB supera90% de22GiB
(19,8GiB), aunqueworkingset17,10GiB. Se reduce contexto total131072→65536,
dos slots32768, sin modificarRAM ni otrosCT. Evidencia inicial conservada y
revalidación pendiente. Watcher vigila tantoRSS como workingset. Gemma65536 intacto.

### IA-CHAT — validación y ajustes dentro de los CT nuevos

Qwen con65536total: RSS18,96GiB, chatPASS. FalsoHALT alvolver aGemma: workingset
incluía caché no mapeada delmodelo descargado; RSS6,53GiB/anon0,15GiB aldetenerse.
Observador corregido: máximoderesident_tasks(anon+file_mapped+kernel) yRSS,
conserva current/working_set porseparado; Gemma65536 revalidado. SinOOM.
Visión: primera imagen pixelada falló enQwen; PNG DejaVuSans normal pasó4821
enambos. Sin cambio deversión/modelo/proyector. Thinkingoff0chars/on1040chars
yrespuestaCarlaPASS. STTsmallint8>1GiB incremental ytranscripción errónea; se
usa baseint8. FP32 descartado por2,97GiBworking/1GiBswap en631 sinOOM ysinmejorar.
RAM631 permanece3072MiB. Propuesta noaprobada:4096MiB solo si se quisiera investigar
FP32; no necesaria paraelperfilint8 elegido. STTaproximado4/5palabras: sustituye
prueba→nueva; exactitud limitada se conserva comoresultado, no transcripción exacta.
Criterio operativo de«parecerse»: WER<=20%, registrando errores; noUAT humana.
RAG/STT concurrentes yreboots/limpieza/idempotencia todavía pendientes.

### IA-CHAT — corrección de configuración persistida de audio

Auditoría de SQLite detecta `audio.stt.whisper_model="small"` pese al cambio de
entorno a base. Los ensayos etiquetados base anteriores siguieron usando small;
se conserva su evidencia y se corrige esa clasificación. El pico FP32 de2,97GiB
corresponde a small/FP32. Se precarga base en caché local y se fija mediante API
admin `/api/v1/audio/config/update`, verificando respuesta y valor persistido.
Repetir STT y concurrencia/RAM antes del cierre; no reutilizar sus cifras como
evidencia de base. El backup13:41 se conserva como anterior a esta corrección.
Sin cambios de RAM/otrosCT/627 ni commit/push.


## IA-CHAT — ampliación de alcance aprobada: patrón del repositorio y observabilidad

13nov2026 Europe/Madrid. El propietario solicita integración reproducible completa de
630/631 en Terraform/inventario YAML, docs/inventory, monitorización y Grafana como
el resto del pool; autoriza los cambios necesarios para ello. Aprobación limitada
a los dos CT nuevos y modificaciones aditivas de observabilidad que los incorporen,
con backup/rollback, validación e idempotencia. No rollout global de exporters,
no cambios de aplicaciones/recursos de otros CT y **627 excluido por completo**.
Sin commit/push ni aumento automático de RAM631. Mantener DHCP y reservas pendientes,
unprivileged, volúmenes/modelos y contratos CPU/RAM del repositorio.

Estado IN PROGRESS: la receta pct aislada anterior no basta como cierre del patrón
solicitado; preparar adopción Terraform sin recreación, SSH verificado si procede,
exporters apropiados para630sinDocker y631conDocker, integración aditiva enPrometheus/
Blackbox/Grafana e inventario. Conservar cambios previos ajenos. La validación devoz
sigue pendiente tras corregir WHISPER_MODEL persistido; no declararla aprobada.
