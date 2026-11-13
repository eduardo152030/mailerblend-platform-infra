# IA-CHAT — swap de CT 631

13 de noviembre de 2026, Europe/Madrid. Fase 7. IaC Reliability, Security & Disaster Recovery.
Tarea IA-CHAT-SWAP-631: **DONE técnico**. Commit y push autorizados por el propietario.

El propietario solicita ampliar «1.7» a partir de 1 GiB. Se interpreta como
**1,7 GiB**, redondeado hacia arriba a **1741 MiB** (1,7002 GiB). PVE usa MiB.

| Dato | Antes | Después |
|---|---:|---:|
| Cuota de swap | 1024 MiB | 1741 MiB |
| Uso observado | 1023,28 MiB (~99,93 %) | ~1023,28 MiB (~58,8 %) |
| RAM | 4096 MiB | 4096 MiB |
| Reinicios de servicios | 0 | 0 |

Fuente canónica: [infra-webui.yml](../../inventory/services/infra-webui.yml).
[Script versionado](../../scripts/ia-chat/resize-swap-631.py): API PVE, digest,
backup privado y validación; modifica exclusivamente swap631. Notas se sincronizan
por separado y únicamente en631. No Terraform apply general, swapoff, limpieza de
cachés ni cambios a CT630/627 u otros CT. El script verifica hashes de los demás CT
y conserva identidad/StartedAt/restart count de los tres contenedores de631.

PVE y memory.swap.max reflejan 1825570816 bytes. Node Exporter y Prometheus también
publican 1741 MiB. WebUI /health devuelve200; no se ejecutan inferencias ni UAT.
OOM/oom_kill permanecen en0. El contador max jerárquico es histórico: se conserva,
no se resetea ni se atribuye todo su valor a este aumento.

Segunda aplicación: cero escrituras, sin reinicios. Plan Terraform acotado630/631
no-op con TLS verificado. Notes visibles idénticas a su fuente; inventario yREADME
actualizados. Terraform validate y16 pruebas de inventario PASS.

Este cambio amplía la **cuota del CT sobre la swap del host**: no crea swap física
adicional ni garantiza mejorar el rendimiento. Uso alto puede incluir páginas frías;
no se fuerza su retorno a RAM. El host tenía ~8,9 GiB de swap libre antes del cambio.

## Evidencia y siguiente paso

[Antes](evidence/ia-chat-swap-631/before.json),
[aplicación](evidence/ia-chat-swap-631/applied.json),
[idempotencia](evidence/ia-chat-swap-631/idempotent.json),
[exporter](evidence/ia-chat-swap-631/exporter.json),
[Prometheus](evidence/ia-chat-swap-631/prometheus.json),
[plan no-op](evidence/ia-chat-swap-631/terraform-plan.json),
[Notes verificadas](evidence/ia-chat-swap-631/notes-sync-verified.json).

Siguiente: observar swap y latencia con el uso habitual; ampliar cuota no sustituye
un diagnóstico de presión sostenida. Fase 7 global sigue IN PROGRESS y sus UAT,
DHCP, restauración y aceptación de alertas pendientes no se cierran con esta tarea.
