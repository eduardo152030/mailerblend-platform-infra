# CT 631 — infra-webui

Estado: **RUNNING observado; Notes sincronizadas y verificadas**.
Fecha de observación: 13 de noviembre de 2026, Europe/Madrid; evidencia UTC
`2026-11-13T16:18:41Z` (captura inicial). Actualización posterior de latencia:
configuración reconciliada bajo autorización exclusiva630/631; ver el informe vigente.

## Propósito y estado
 interfaz privada de chat con Open WebUI, búsqueda SearXNG,
RAG multilingüe y STT local. Servicio `infra-webui`, nodo `pve`; RUNNING observado
el 13/11/2026 a las 17:18 CET (16:18 UTC). WebUI y cAdvisor healthy; SearXNG running
sin healthcheck Docker. La observación original de17:18 no ejecutó inferencias; las pruebas posteriores
de latencia están documentadas por separado.

## Arquitectura y recursos
 Debian 12, LXC sin privilegios, 2 vCPU, 4096 MiB RAM,
1024 MiB swap, onboot=1 y Europe/Madrid. Raíz de 20 GiB en
`local-lvm:vm-631-disk-0`; sin mountpoints PVE adicionales. Docker con nesting/keyctl;
excepción AppArmor `unconfined` aprobada únicamente para631, documentada en IaC.
RAM ampliada con autorización expresa; no extender la excepción a otros CT.

## Red, puertos y acceso
 DHCP 192.168.1.66/24, MAC BC:24:11:0D:41:78,
vmbr0/firewall=1; gateway y DNS 192.168.1.254 observados. UI
http://192.168.1.66:3000 (publicado en IPv4/IPv6 hacia8080), SSH22,
Node Exporter 192.168.1.66:9100 y cAdvisor 192.168.1.66:8085.
SearXNG8080 solo red Compose, sin publicación; SMTP25 solo loopback.
Reserva DHCP, dominio, TLS y reglas WAN/ACL efectivas: no verificados.

## Servicio y dependencias
 Compose `/opt/ia-chat/docker-compose.yml`;
Open WebUI v0.13.3 y SearXNG 2026.11.9-57ff753ad, imágenes fijadas por digest.
Ambos restart=unless-stopped. API compatible OpenAI de630 en
http://192.168.1.67:8080/v1; Ollama desactivado. Embedding local
intfloat/multilingual-e5-small y Whisper small/int8/es; búsqueda externa mediante
SearXNG. La configuración persistida prevalece sobre variables de entorno.

## Persistencia y seguridad
 `/opt/ia-chat/data` -> `/app/backend/data` (RW),
incluye SQLite, historial, documentos y cachés locales; `/opt/ia-chat/custom.css`
-> `/app/build/static/custom.css` (RO). SearXNG usa `/opt/ia-chat/searxng`
-> `/etc/searxng` (RW) y volumen Docker anónimo para `/var/cache/searxng`.
No tratar ese volumen de caché como datos funcionales imprescindibles.
Secretos en archivos privados600; no publicar entornos, claves ni bases de datos.
Autenticación habilitada; administrador del propietario existente y preservado.
Registro cerrado; no publicar datos de usuarios ni sus sesiones.

## Salud y monitorización
 healthcheck Docker WebUI healthy y sonda JSON `/health`
UP; SearXNG carece de healthcheck Docker, búsqueda funcional probada previamente,
no repetida ahora. Node Exporter1.10.2 nativo, CPU cgroup v2 textfile/5s y RAM LXCFS;
cAdvisor0.60.6 con socket containerdRO solo631, límite256MiB. Node, cAdvisor y Blackbox del servicio UP; sin alertas FIRING en la captura.
Grafana Fleet/Details porCT631; uptime/estado desde API PVE. Recepción Telegram:
no verificada. Un estado healthy no acredita calidad de voz ni UAT de chat.

## Backup y recuperación
 job `ia-chat-webui-631` habilitado, diario03:30,
storage `storage` (HDD según despliegue), snapshot/zstd, siete diarios/cuatro semanales.
Backup manual final del13/11/2026 a16:35 CET verificado por SHA256/zstd/tar y archivos
críticos; evidencia en el informe IA-CHAT. Restauración funcional completa:
no verificada. Preservar datos, secretos, configuración e imágenes de rollback.

## IaC y operación
 `inventory/services/infra-webui.yml`, Terraform
`proxmox_virtual_environment_container.svc["infra-webui"]`, configuración canónica
`services/infra-webui/{compose,config,monitoring}`. Operar Compose solo en
`/opt/ia-chat`; no down-v/prune ni deploy-all. Receta `scripts/ia-chat/README.md`;
ficha `docs/inventory/631-LXC-INVENTORY.md` e informe
`docs/roadmap/IA-CHAT-EXECUTION-2026-11-13.md`. Optimización posterior documentada en `docs/roadmap/IA-CHAT-LATENCY-2026-11-13.md`.

## Límites
 STT sintético previo4/5palabras (WER20%), no calidad exacta ni UAT humana.
RAG/STT concurrentes con cuota4096MiB: pico residente2,510GiB, sin OOM.
Contador max jerárquico atribuible a cAdvisor256MiB; límite local del CT sin eventos max. Móvil/micrófono real pendientes. CT627 (Voicebox) excluido;
no modificarlo, reiniciarlo ni añadir coordinación automática.

## Fuentes, sincronización y límites de verificación

Fuente canónica de Notes: [services/infra-webui/NOTES.md](../../services/infra-webui/NOTES.md).
Declaración: [inventory/services/infra-webui.yml](../../inventory/services/infra-webui.yml).
Operación: [README del servicio](../../services/infra-webui/README.md) y
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

Actualización vigente: [informe de latencia](../roadmap/IA-CHAT-LATENCY-2026-11-13.md).
[Notes sincronizadas](../roadmap/evidence/ia-chat-latency-2026-11-13/notes-sync-verified.json),
[plan Terraform no-op](../roadmap/evidence/ia-chat-latency-2026-11-13/terraform-plan.json).
