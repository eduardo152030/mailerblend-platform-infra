> Actualización posterior: RAM6314096MiB, perfil/contexto/caché y latencia vigentes
> en [IA-CHAT-LATENCY](IA-CHAT-LATENCY-2026-11-13.md). Los resultados de este informe
> se conservan como evidencia del despliegue inicial; el administrador del propietario
> ya existe y fue preservado en la intervención posterior.

# IA local para chat — ejecución A–F e integración en el repositorio

Seguimiento13nov2026, Europe/Madrid; los JSON conservan sus marcas UTC identificadas.
Fase7. IaC Reliability, Security & Disaster Recovery, con integración de Fases4/6.
Implementación y pruebas técnicas DONE; observación600s/21muestrasPASS. UAT humana, reservasDHCP,
restauración funcional y recepción Telegram de las nuevas cadenas no acreditadas.

## Alcance y autorización

La continuación autoriza A–F y sustituye el bloqueo del
[preflight](IA-CHAT-PREFLIGHT-2026-11-13.md). El propietario aprueba expresamente
AppArmor unconfined solo631 y amplía después a patrónIaC/inventario/monitorización/
Grafana para630/631. Cambios aditivos mínimos en610/616/611 con backup/rollback.
CT627 excluido: sin ejecución, reinicio ni cambios.27 hashes protegidos de los
25CT anteriores y storage.cfg/redhost siguen iguales. Sin commit/push ni RAMextra.

## Infraestructura y acceso

| CT | Nombre | MAC | DHCP observado | Recursos | Disco |
|---|---|---|---|---|---|
|630|infra-llm|BC:24:11:6F:79:36|192.168.1.67|4CPU;22528MiB RAM;1024MiB swap|16GiB raíz+60GiB /models|
|631|infra-webui|BC:24:11:0D:41:78|192.168.1.66|2CPU;3072MiB RAM;1024MiB swap|20GiB raíz|

Debian12, unprivileged, vmbr0/firewall, onboot1, Europe/Madrid.
`/models`:RO/backup0. WebUI **http://192.168.1.66:3000**;
API **http://192.168.1.67:8080/v1**, clave600 en630 `/etc/llama/api.key`.
SearXNG sin puerto publicado. RouterOS no accesible mediante acceso existente;
reservas pendientes, comandos exactos en [README operativo](../../services/ia-local/README.md).
No configurar IP estática ni intentar credenciales del router.

## Patrón IaC y observabilidad

Declaraciones canónicas [630](../../inventory/services/infra-llm.yml) y
[631](../../inventory/services/infra-webui.yml); recursos `svc["infra-llm"]` y
`svc["infra-webui"]` importados y adoptados sin recrear. Módulo extendido con campos
opcionales para plantilla de archivo, DHCP, unprivileged, swap y mountpoint;
los18 estados Terraform previos se conservan exactamente. Plantilla/selector de
volumen son parámetros de creación; no se reemplaza el volumen importado.
TLS verificado con CA PVE obtenida mediante SSH estricto; no bypass SSH/TLS.
Configuración por servicio en `services/infra-llm` y `services/infra-webui`;
los antiguos paths compartidos enlazan a esas fuentes. Creador pct histórico retirado
de la receta activa/idempotencia. [Recetas](../../scripts/ia-chat/README.md).
Inventario [630](../inventory/630-LXC-INVENTORY.md),[631](../inventory/631-LXC-INVENTORY.md)
y tabla global regenerados junto con Notes/manifiesto de frescura.

Node Exporter1.10.2 nativo en ambos: CPU cgroup v2 textfile cada5s, collector.cpu
inactivo, RAM LXCFS. Capacidad4/2CPU y22528/3072MiB comprobadas contra PVE.
cAdvisor0.60.6 solo631, digest fijado, socket containerdRO y namespace cgroup delLXC,
límite256MiB. NoDocker en630: `lxc:cadvisor:required=0`, N/A en Fleet/Details y
excepción explícita de LxcDockerMetricsMissing. Los CT sin declaración conservan
el contrato Docker anterior. Primer HALT por esa regla legacy conservado como
incidencia; regla validada por promtool y recargada antes de repetir observación.

Prometheus:2Node+1cAdvisor+2Blackbox funcionales, reglasCPU existentes e inventario
aditivo. Uptime/estado desde APIProxmox porCT. No scrape de `/metrics?model=...`, que
podría cargar pesos. Backups coordinados de config610/616 y DB/config611 fueraPVE
más copia localCT; extracción/restauración aislada y parsers antes de recarga.
Grafana Fleet yDetails provisionados:136 consultas reales de630/631, sin datos
cruzados;630sinseriesDocker. Solo cambió el panel de salud para admitir N/A.
No se tocaron aplicaciones de otros CT ni discovery global.

## Versiones fijadas

| Componente | Versión / identidad |
|---|---|
|llama.cpp|v1.0.0; commit b1b770d90d94cad9e9ea5b993bdbc383a522fb28; binario1.0.0-dev|
|Open WebUI|v0.13.3 @ sha256:46b59158e6558eeb980bc828e0f1b30238ad24d82ed84d5e5eda1dab2a082f14|
|SearXNG|2026.11.9-57ff753ad @ sha256:287af61f1a13e86d02974fcde91a3413a9945788de38b61ffbc491d81a19bcc2|
|Docker/Compose/containerd|29.9.3 /5.7.1 /2.4.2; runc oficial|
|cAdvisor|0.60.6 @ sha256:b8e7d1093144fd088f425ff003d75a4aa405de075db78dae3bc563730b1bd07a|
|Embedding|intfloat/multilingual-e5-small; revisión614241f622f53c4eeff9890bdc4f31cfecc418b3|
|Whisper|small/int8,es; revisión536b0662742c02347bc0e980a01041f333bce120|

Compilación GGML_NATIVE y-march=native para i5-6500/AVX2; CPU, sin CUDA.
Imágenes/manifiestos y paquetes en [versiones](../../services/ia-local/versions-installed.json).

## Pesos verificados localmente

Cuatro verificaciones bytes/SHA al primer intento; total34071899360bytes (~31,73GiB).
Repositorios públicos unsloth/Qwen3.6-35B-A3B-GGUF yunsloth/gemma-4-26B-A4B-it-qat-GGUF.

| Modelo / fichero | Bytes | SHA256 local |
|---|---:|---|
|Qwen3.6-35B-A3B-UD-IQ4_XS.gguf|17730509792|649d7508507b84638732c4f52c24c8b15843c6dca2f3ff793ae07c14a67ebbb3|
|Qwen mmproj-F16.gguf|899283680|8971ee4f331ff0a4c609374f32984b3d4e6dc086c0aa35f1d637fad1829e887f|
|gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf|14249047104|a7c5bc715f5ff8e99a3e8901ce7d2b42b402c669bf24f7c5250747633d0f5891|
|Gemma mmproj-F16.gguf|1193058784|d00f211a7d4f7fb19bd9b75d8e9342eccffb5920b08fd9562167560fdfcc5dd1|

## Benchmarks y parámetros efectivos

mmap,repack0,batch512,ubatch128,pp512,tg128,una repetición. No certifican throughput
con contexto lleno ni dos usuarios simultáneos.

| Modelo | Hilos | pp512 tokens/s | tg128 tokens/s |
|---|---:|---:|---:|
|Gemma|3|16,3953|7,9607|
|Gemma|4|18,2665|6,3783|
|Qwen|3|20,0136|5,1271|
|Qwen|4|19,4880|4,4238|

Router `--models-max 1`, sueño120s; total65536contexto/2slots32768 en ambos.
Gemma generación3/prompt4 hilos; Qwen3/3. Gemma temp1/top_p.95/top_k64;
Qwen temp.6/top_p.95/top_k20/min_p0. Thinkingoff por defecto.

| Ciclo final | TTFT s | Total respuesta s | Cambio incl. descarga/guarda s | tokens/s | RSS630 GiB | Residente630 GiB |
|---|---:|---:|---:|---:|---:|---:|
|Gemma1|58,933|59,826|61,897|8,941|16,306|16,393|
|Qwen|76,485|78,309|80,388|5,419|18,930|19,055|
|Gemma2|64,600|65,571|67,704|8,228|16,262|16,375|

Se observó como máximo un modelo principal mapeado. Límite63022GiB; residente
por debajo90%. Working set máximo Qwen20,123GiB y memory.current21,874GiB incluyen
caché; no equivalen a dos modelos residentes. HostMemAvailable mínimo del ciclo:
21,530/23,032/22,710GiB; swap máxima6,023/6,789/7,175GiB. Guarda>=21GiB antes de
cada carga (no mínimo durante inferencia). No swapoff ni liberación en otrosCT.

## Tabla F — pruebas reales

| Prueba | Resultado | Evidencia / límite |
|---|---|---|
|1API|OK|dos alias conkey200; sin401; repetida tras reboot|
|2Chat|OK|ambos responden; TTFT/tokens/s arriba|
|3Cambio|OK|Gemma→Qwen→Gemma; uno mapeado como máximo|
|4Visión|OK|ambos leen4821; PNG DejaVuSans68px900×240|
|5Thinking|OK|misma lógica:Carla;0chars off/1040on enreasoning_content|
|6SearXNG|OK|JSON desde contenedorWebUI;10resultados, config3/concurrencia1|
|7Voz|OK funcional, calidad limitada|small/int8:«¡Hola! Esto es... ¡Una nueva!»;4/5palabras,WER20%,no exacto|
|8RAG|OK|Knowledge devuelve7731; borrado al terminar; STT simultáneoPASS|
|9Interfaz/datos|OK técnico|HTTP200, bindpersistente, historial/búsqueda tras reboot; móvil/UATpendiente|
|10Memoria|OK con incidencia|contextoQwen reducido; picos medidos;631working2,85GiB>2,7,propuesta4GiBsinaplicar|
|11Reinicio|OK|bootID cambia en630/631, IPs iguales, serviciosauto, API200/401/UI200|

Evidencias [API/ciclo/visión](evidence/ia-chat-2026-11-13/validation-api.json),
[concurrencia](evidence/ia-chat-2026-11-13/rag-stt-concurrent.json),
[reboot](evidence/ia-chat-2026-11-13/reboot-verified.json),
[limpieza](evidence/ia-chat-2026-11-13/fixture-cleanup-final.json).
No hay usuario técnico, Knowledge ni credencial de prueba activos; JWT anterior401,
SQLitequick_checkok. Primera cuenta real disponible para el propietario.

## Memoria WebUI e incidencias

small/int8 incrementa anon0,853GiB respecto a baseline equivalente tras calentar
embedding (baseline1,232GiB/peak2,085GiB), por debajo1GB. Primera medición fría no era
comparable. Con exporters y RAG/STT simultáneos: residente2,692GiB,working2,847GiB;
noOOM. Se informa superación2,7GiB y propone4096MiB, **no aplicada**.
Reposo posterior con caché: residente1,952/working2,261GiB;630residente0,104GiB.
HostMemAvailable23,468GiB yswap5,747GiB en captura final. memory.events631max1033
(reclamaciones contra el límite),oom0/oom_kill0; no confundir max conOOM ni afirmar
holgura amplia. Conservar vigilancia del margen con3072MiB.

Incidencias preservadas:

- Repacking inicial duplicó pesos y alcanzóRSS~21,2GiB/memory.high: benchmark
  interrumpido, sinOOM, swapglobal subió. Repacking desactivado; no se repitió éxito.
- Qwen131072 dioRSS19,8195GiB>90%22GiB: contexto reducido65536 y revalidado.
- Observer inicial confundió caché no mapeada con residente: falsoHALT corregido,
  manteniendo current/working/RSS como magnitudes separadas.
- Primer PNG pixelado falló enQwen; se sustituyó por fuente legible, ambosPASS.
- Docker/runc ycrun fallaron por AppArmor antiguo. Excepción exterior solo631
  aprobada yreproducible; unprivileged/seccomp/namespaces conservados. Cruninactivo.
- Las pruebas inicialmente etiquetadas base aún usaban small porSQLite persistida.
  Se corrige su clasificación; base real/int8 yFP32 no mejoraron el WAV sintético.
  small/FP32~2,97GiB yswap~1GiB se descartó. Perfil final efectivo small/int8,
  tanto en entorno como en configuración persistida. No usar logs antiguos como
  evidencia de base ni del estado final.
- SSH630: conflicto ssh.socket/SIGHUP resuelto con modo servicio. logind recibe
  NAMESPACEdenied bajo AppArmor; acceso por clave verificado con timeout60s.
  No se relaja AppArmor630 para resolver el componente opcional de sesiones.

## Variables y persistencia v0.13.3

OllamaOFF/OpenAIAPI ON, modelos con nombres y visión,localees-ES, Gemmapordefecto;
prompt exacto español. Títulos/búsquedasON; tags/followup/autocomplete/RAGqueriesOFF.
Searx `SEARXNG_QUERY_URL` con `<query>`; webSearchfalse porchat en
`DEFAULT_INTERFACE_SETTINGS`. RAG_ENGINEvacío=local, RAG_EMBEDDING_MODEL,
RAG_TOP_K3,prefijosquery:/passage:,chunk600/overlap100.
`AUDIO_STT_ENGINE=''` selecciona Whisperlocal, `WHISPER_MODEL=small`,
`WHISPER_COMPUTE_TYPE=int8`,`WHISPER_LANGUAGE=es`. `AUDIO_TTS_ENGINE=''` por sí solo
selecciona TTS del navegador; se añade permisoTTSfalse, responseAutoPlaybackfalse,
visibilidadfalse ycustom.css oficial para ocultarlo también aladmin. Persistencia
SQLite prevalece sobre env: verificar/reconciliar claves explícitas porAPI sin
imprimir exports consecretos. Composeumask077,DB/secretos600/directoriodatos700.

## Backups y operación

CT631 diario03:30,7daily/4weekly;630domingo04:00,4weekly,modelosexcluidos.
Backup final integrado: `/mnt/storage/dump/vzdump-lxc-631-2026_11_13-16_35_10.tar.zst`,
5898708342bytes, SHA256
`0b3af35138c8cc5dbccf653feb62441eec5522c51e72fb5304522c3c25c200e6`.
zstd/tarPASS,124402miembros yDB/Compose/secrets/settings/CSS/pct.conf presentes.
[Evidencia](evidence/ia-chat-2026-11-13/backup-integrated-final-verified.json).
Backups anteriores13:04/13:41 conservados como históricos, no estado final.
No restauración funcional ensayada. README operativo entregado enPVE
`/root/ia-local/README.md`:arranque/parada/logs,router/modelos,key,registro,restore,
primeradmin,móvil,micrófonoWindows yexclusión627.

## Cierre verificable y pendientes

TerraformvalidatePASS; plan630/631no-op;18estadosanterioresidénticos; bundles
reproducibles einputs inválidos rechazados. Segunda aplicación de apps/jobs/exporters/
Prometheus/Blackbox/Grafana:0recreación/0recargas/0reinicios.136consultasGrafanaPASS; validación Fleetglobal29consultas/20CTPASS.
Observación600s/21muestras: **PASS**, sin anomalías. Consultar [registro](evidence/ia-chat-2026-11-13/monitoring-observation.json)
con marcas UTC, salud, frescura, CPU/RAM, estadoPVE y ausencia de alertasfiring.

Pendientes del propietario: reservarDHCP, crearadmin, probarvoz/móvil ycerrarregistro;
valorar4GiB631. Cadena Telegram de630/631 con recepción humanaFIRING/RESOLVED no
ensayada: estas fuentes no se declaran cadenas aceptadas bajo contratoF4 por tener
solo métricas/reglas/Grafana. Tampoco se dispensa UAT ni se cierra Fase7 global.
Norma manual: no usar Gemma mientras el futuro agente useQwen ni LLM juntoaVoicebox.
No agente nocturno implementado. Sin commit/push.

Captura de cierre posterior a observación: 2026-11-13T16:12:30.689144+00:00 UTC; MemAvailablehost23,407GiB,
swapusada5,512GiB. Identidades/StartedAt/restarts de ambasapps sigueniguales a la
prueba de idempotencia. Validadores Fleet/Details ahora derivan el conjunto esperado
del inventarioYAML, en vez de fijar17CT históricos.
