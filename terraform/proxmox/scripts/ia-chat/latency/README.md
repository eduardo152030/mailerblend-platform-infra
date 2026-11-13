# Optimización IA-CHAT

Alcance: CT630/631. No ejecutar comandos dentro de627 ni otros CT. El único informe
transversal es `swap-report.py`, que lee cgroups del host y nombres de configuración.
Sin commit/push ni apply general. Seguimiento y resultados en
[IA-CHAT-LATENCY](../../../docs/roadmap/IA-CHAT-LATENCY-2026-11-13.md).

Perfil canónico WebUI: `services/infra-webui/config/chat-performance.json`.
`render-compose.py` sincroniza solo sus parámetros de rendimiento en Compose;
segunda aplicación sin diferencias no escribe. Copiar perfil a
`/opt/ia-chat/chat-performance.json` antes de ejecutar `webui-check.py init`.

## Auditoría y pruebas graduales

`create-fixture.py` se ejecuta mediante `docker exec -i ... python -`, dentro de
la imagen WebUI. Usa la API interna versionada para cuenta y token efímeros,
conservando usuarios reales. Un backup SQLite privado antes de cambios se guarda
fuera del bind WebUI, en `/opt/ia-chat/.runtime/latency`. No restaurarlo sobre la BD
activa como forma de limpiar pruebas: descartaría conversaciones nuevas del propietario.

`run-ui-probe.py <etapa> '["mensaje1","mensaje2"]' [alias]` es un orquestador local;
usa SSH PVE estricto y el cliente `ui-probe.py` dentro de la imagen. Invoca la ruta
HTTP stream real `/api/chat/completions` y recibe los deltas por Socket.IO, como UI.
Conserva sesión/chat/historial y opciones de background; no cuenta solo el tiempo HTTP
hasta el ACK. La medida usa el primer delta visible, no el evento final.

`apply-ui-stage.py a|b|c|e|g` usa API administrativa con el perfil público. Preserva
claves de configuración ajenas y no imprime exports con secretos. Config/modelos
iguales no se reescriben. Las etapas no son tareas de despliegue rutinarias de otros CT.

`summarize-ui.py` correlaciona petición, slot, lectura y generación. Para peticiones
sin usage expuesto al cliente (título), deriva input=KV al liberar-generados+1 y
cache=input-procesados; contrasta esa relación con todos los usage principales.
Logs filtrados solo de ventanas sintéticas; no copiar logs completos del propietario.

## CPU, memoria y selección

Los scripts `guarded-warm.py`, `long-prompt.py`, `swap-report.py`, `rag-stt-memory.py`,
`benchmark-matrix.py`, `select-benchmarks.py` e `idle-residency.py` se ejecutan enPVE,
con copias en `/root/ia-local/latency`. Modelo previo descargado antes de cada carga;
MemAvailable host>=21GiB y mayor deRSS/residente630<90%22GiB. No swapoff, drop_caches,
ni reinicio de otros CT para superar una guarda.

La matriz usa r3; PP512/PP2048 a4h yTG128 a3h se ejecutan por separado porque esta
versión de llama-bench no admite --threads-batch. b512/2048 y ub128/256/512.
Los resultados completos verificados se reutilizan al reanudar; no repetirlos por
rutina. Contexto de benchmark no equivale a memoria máxima del servicio: después
se valida el candidato real con su contexto, proyector y prompt3000 bajo la guarda.
Si un candidato falla en runtime se conserva el fallo y se prueba el siguiente ranking.

`select-benchmarks.py` prioriza PP2048, con PP512/TG como desempate, y escribe ranking
más `/root/ia-local/latency/performance-tuning.json`. Solo tras validar en servicio,
conservar la selección en `services/infra-llm/config/performance-tuning.json` y copiar
a `/root/ia-local/performance-tuning.json`. `install-llama.py` usa ese override y
reconcilia INI/unidad/template: no reinicia si los bytes permanecen iguales.

Gemma usa un template derivado del GGUF, con hash de procedencia, que mantiene el
prefijo vacío reasoning-off en mensajes históricos. SWA completa permite reutilizar
el prefijo; contexto16384total/8192por slot para ajustarse a RAM. Primera petición
idéntica al upstream y thinking-on preservados. Qwen conserva65536total.
La caché RAM auxiliar de snapshots se desactiva (`cache-ram=0`) para evitar copias
extra de estados grandes. La KV del slot ycache_prompt=true siguen activos; se
verifica reutilización real en el mismo slot.
No activar SWA completa a64kGemma: la estimación de KV excede el margen. No repetir
repacking si no existe margen medido para la duplicación de pesos ya observada.

## Cierre

Aplicar perfil completo y Compose exclusivamente631; comprobar fecha/weekday y
búsqueda mediante botón. Verificar5min sin inferencias con `idle-residency.py`,
seguido de `run-ui-probe.py idle-final` (TTFT<=15s). Tres turnos cortos finales deben
cumplir<=10s y reutilización medida de historial. RAG/STT4096MiB registra eventos
antes/después y atribuye jerarquía: max de cAdvisor no significa max del CT.

Antes de borrar la fixture: limpiar su Knowledge/file mediante `webui-check.py
rag-clean` con IA_RESULT_PATH propio y copiar solo evidencias públicas seleccionadas.
`cleanup-fixture.py` borra solo la cuenta temporal y sus chats, comprueba JWT401 y
preserva usuarios reales; no reabre registro. Eliminar también la copia propia de
credencial en `/root/ia-validation-auth.json` comprobando su email antes. Backups
privados conservados fuera de Git. Verificar idempotencia, secretos, Notes/inventario
y estado final, sin convertir preparaciones locales en despliegue/aceptación.
