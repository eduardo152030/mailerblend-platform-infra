# infra-webui — CT 631

Debian12 sin privilegios;2CPU,4096MiB RAM,1741MiB swap (~1,7GiB),raíz20GiB.
Terraform: `svc["infra-webui"]`, declaración `inventory/services/infra-webui.yml`.
Compose canónico en `compose/`, configuración en `config/` y runtime `/opt/ia-chat`.
Recetas compartidas: [ia-chat](../../scripts/ia-chat/README.md).

DHCP observado192.168.1.66, MAC BC:24:11:0D:41:78; reserva de router pendiente.
Web `http://192.168.1.66:3000`. SearXNG solo red Compose, sin puerto publicado.
Imágenes por digest; datos persistentes, secretos600 y directorio datos700.
La excepción AppArmor `unconfined` está aprobada exclusivamente para631:
receta `scripts/ia-chat/apparmor-631.py`. No ampliar a otrosCT.

Whisper efectivo small/int8, CPU, español; verificar también valor persistido en
SQLite/API, pues el entorno no sobreescribe configuración previamente guardada.
RAG local multilingual-e5-small. TTS oculto mediante custom.css y visibilidad UI.
Administrador del propietario existente; preservar cuenta, historial y documentos.

Node Exporter nativo9100, CPU cgroup textfile/RAM LXCFS. cAdvisor8085 digest fijado,
namespace cgroup host del LXC y socket containerdRO solo631; límite256MiB.
Blackbox `/health`. Backups diario03:30 HDD,7daily/4weekly.
Voz sintética tiene20% error; UAT humana pendiente. Pico working set>2,7GiB:
4096MiB aprobados y aplicados en vivo; nueva prueba RAG/STT sinOOM. Informe: [ejecución](../../docs/roadmap/IA-CHAT-EXECUTION-2026-11-13.md).

Perfil de latencia en `config/chat-performance.json`; títulos/consultasOFF,
funciones nativas implícitasOFF. Ver informe IA-CHAT-LATENCY para estado de pruebas.
