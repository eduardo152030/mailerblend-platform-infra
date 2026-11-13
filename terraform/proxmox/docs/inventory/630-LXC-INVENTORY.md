# CT 630 — infra-llm

Estado: **RUNNING observado; Notes sincronizadas y verificadas**.
Fecha de observación: 13 de noviembre de 2026, Europe/Madrid; evidencia UTC
`2026-11-13T16:18:41Z` (captura inicial). Actualización posterior de latencia:
configuración reconciliada bajo autorización exclusiva630/631; ver el informe vigente.

## Propósito y estado
 inferencia local de chat, código, razonamiento y visión con
llama.cpp en CPU. Servicio `infra-llm`, nodo `pve`; RUNNING observado el
13/11/2026 a las 17:18 CET (16:18 UTC). Salud del router verificada mediante
Blackbox; la observación original de17:18 no cargó modelos. Las pruebas posteriores
de latencia se documentan por separado.

## Arquitectura y recursos
 Debian 12, LXC sin privilegios, 4 vCPU, 22528 MiB RAM,
1024 MiB swap, onboot=1 y Europe/Madrid. Raíz de 16 GiB en
`local-lvm:vm-630-disk-0`; volumen de modelos de 60 GiB en
`local-lvm:vm-630-disk-1`, montado en `/models`, ext4, solo lectura y backup=0.
llama-server nativo systemd; sin servicio Docker activo ni cAdvisor requerido.

## Red, puertos y acceso
 DHCP 192.168.1.67/24, MAC BC:24:11:6F:79:36,
vmbr0/firewall=1; gateway y DNS 192.168.1.254 observados. API LAN
http://192.168.1.67:8080/v1; SSH 22 y Node Exporter 192.168.1.67:9100.
SMTP 25 solo loopback, sin función de aplicación verificada. Reserva DHCP, dominio,
TLS y exposición externa: no verificados; no asumir que firewall=1 implica ACL LAN.
La API requiere clave; se conserva fuera de Git en `/etc/llama/api.key` (600).

## Servicio, dependencias y persistencia
 llama.cpp v1.0.0, commit
b1b770d90d94cad9e9ea5b993bdbc383a522fb28, CPU AVX2. Unidad
`llama-server.service` activa y habilitada. Preset `/etc/llama/models.ini`;
código/binarios `/opt/llama.cpp`; pesos GGUF y proyectores Qwen3.6/Gemma4 en `/models`.
Router con un modelo grande máximo y dos slots. Gemma: contexto total 16384
(8192 por slot), SWA completa y plantilla de caché versionada; Qwen: total 65536
(32768 por slot). Reposo 3600 s; cache_prompt activo y caché auxiliar RAM desactivada. Descargas iniciales requieren Hugging Face; inferencia local.
Antes de cargar pesos, comprobar MemAvailable del host >=21 GiB. No inferir
capacidad concurrente a partir de los límites virtuales.

## Salud y monitorización
 `/health` HTTP/JSON, sin inferencia. Node Exporter
1.10.2 nativo, CPU cgroup v2 textfile cada 5 s y collector.cpu desactivado; RAM
LXCFS. Node/Blackbox UP, CPU y RAM publicadas, sin alertas FIRING del servicio en
la captura. Grafana Fleet/Details por CT630; uptime/estado desde API PVE.
`lxc:cadvisor:required=0`: Docker N/A explícito. No sondear automáticamente
`/metrics?model=...`, que puede cargar pesos. Recepción Telegram: no verificada.

## Backup y recuperación
 job `ia-chat-llm-630` habilitado, domingo 04:00,
storage `storage` (HDD según despliegue), snapshot/zstd, cuatro semanales.
`/models` queda excluido: reconstruir desde el manifiesto de bytes/SHA256.
Ejecución y restauración funcional de este job: no verificadas. Conservar volúmenes,
API key y configuraciones. No destroy ni recuperación sobre un CT existente.

## IaC y operación
 `inventory/services/infra-llm.yml`, Terraform
`proxmox_virtual_environment_container.svc["infra-llm"]`, configuración canónica
`services/infra-llm/{config,systemd,monitoring}`. Arranque/parada/logs mediante
systemctl/journalctl exclusivamente en630; receta compartida `scripts/ia-chat/README.md`.
Ficha `docs/inventory/630-LXC-INVENTORY.md`; informe y evidencia de pruebas previas
`docs/roadmap/IA-CHAT-EXECUTION-2026-11-13.md`. Optimización posterior documentada en `docs/roadmap/IA-CHAT-LATENCY-2026-11-13.md`.

## Límites
 reserva DHCP y UAT del propietario pendientes; logind tiene una
limitación NAMESPACE documentada, sin relajar AppArmor630. CT627 (Voicebox) queda
excluido: no modificarlo ni coordinarlo automáticamente. No usar LLM y Voicebox
simultáneamente; no usar Gemma mientras un futuro agente utilice Qwen.

## Fuentes, sincronización y límites de verificación

Fuente canónica de Notes: [services/infra-llm/NOTES.md](../../services/infra-llm/NOTES.md).
Declaración: [inventory/services/infra-llm.yml](../../inventory/services/infra-llm.yml).
Operación: [README del servicio](../../services/infra-llm/README.md) y
[recetas IA-CHAT](../../scripts/ia-chat/README.md).
Evidencia actual: [auditoría filtrada](../roadmap/evidence/ia-chat-2026-11-13/notes-live-audit.json).
Pruebas del despliegue: [informe IA-CHAT](../roadmap/IA-CHAT-EXECUTION-2026-11-13.md).

El generador `scripts/generate-lxc-inventory.py` lee las rutas `documentation` del
YAML, incorpora el cuerpo canónico de Notes a `inventory/generated/lxc-notes.json`
y actualiza el índice `docs/inventory/LXC-INVENTORY.md` y su manifiesto. La ficha
individual se mantiene como fuente documental; el generador no la sustituye.
La plantilla `templates/lxc-notes.tftpl` produce el mismo Markdown para Terraform.
Sincronización de esta intervención: exclusivamente el campo description/Notes
mediante API PVE y control de digest; ningún Terraform apply general.

Datos no verificados se indican explícitamente. La captura inicial acredita configuración,
procesos, sondas y métricas puntuales. Las inferencias posteriores constan en el
informe de latencia; no renuevan la UAT ni acreditan restauración funcional o
recepción humana de alertas. La vigencia de
reservas DHCP y accesos externos exige comprobación independiente.

Sincronización verificada el13/11/2026 a17:21 CET (16:21 UTC): fuente canónica y
Notes visibles idénticas, solo description modificado; servicios e identidades
conservados. [Recibo de aplicación](../roadmap/evidence/ia-chat-2026-11-13/notes-sync-applied.json).

Actualización de latencia (13/11/2026): defaults sin herramientas nativas, títulos
ni generación de consultas. Búsqueda explícita mediante botón; sistema de una línea
con CURRENT_WEEKDAY y CURRENT_DATE. Fuentes y pruebas en el informe IA-CHAT-LATENCY.
Las observaciones de17:18 anteriores se conservan como evidencia histórica.

Perfil CPU validado r3: Gemma batch2048/ubatch512; Qwen batch512/ubatch512,
generación3h/prompt4h. Selección canónica: `config/performance-tuning.json`.

Actualización vigente: [informe de latencia](../roadmap/IA-CHAT-LATENCY-2026-11-13.md).
[Notes sincronizadas](../roadmap/evidence/ia-chat-latency-2026-11-13/notes-sync-verified.json),
[plan Terraform no-op](../roadmap/evidence/ia-chat-latency-2026-11-13/terraform-plan.json).

## Uso del contexto de Gemma

8192 tokens por conversación, incluyendo sistema, historial, recuperación y respuesta.
Se recomiendan chats cortos y temáticos, carpetas y búsqueda del historial. Guardar
un chat no implica enviar todo su contenido al modelo. Contexto lleno y su tratamiento
exacto no verificados. [Límites y plan futuro](../roadmap/IA-CHAT-CONTEXT-PLAN.md).
