# CT632–635 — Activación de observabilidad

21/11/2026 Europe/Madrid. Fase 7. Ronda `implementation`, base
`c235c27b7e3ef34c19a46e8fac6c620a5e762c20`. Rama
`ops/monitoring-ct632-635`, worktree `../mailerblend-platform-infra-monitoring-632-635`.

Prometheus no devuelve targets de los cuatro VMID. CT632 es nativo y ya
expone Node/cgroup/correo en la LAN. Instalar Node y cAdvisor solo en
CT633–635 con el bundle canónico y el socket exacto autorizado por el
propietario `/run/containerd/containerd.sock`, namespace `moby`.
CT632 debe aparecer con cAdvisor N/A. Verificar identidad y contrato de
CPU antes de activar. Conservar catálogos existentes y respaldar CT610,
validar promtool y recargar solo Prometheus. Verificar las filas y los
selectores de Grafana tras la publicación. Actualizar el runbook vigente
como último paso tras la confirmación solicitada.

## Resultado en producción

CT632 ya se raspaba con `job=node`. Se añadió únicamente la etiqueta
`job=node_exporter` a su entrada viva, conservando la IP, identidad, reglas
y métricas de correo. Las verificaciones de CPU, RAM y namespace de los
bundles pasaron. Se añadieron 3 Node Exporter y 3 cAdvisor. Promtool validó
la configuración, CT610 preservó todos los demás targets y se confirmó la
recarga. El respaldo de ambos catálogos se conservó en CT610 y se copió
fuera de PVE. Segunda aplicación: siete targets UP y sin cambios.
Grafana autenticado: cuatro filas Fleet, los cuatro enlaces y fichas
Details, cAdvisor N/A para CT632. Prometheus devolvió CPU válida y porcentaje
para los cuatro. cAdvisor devolvió series individuales en CT633–635.
Las IP son concesiones DHCP observadas.

[PR #88](https://github.com/eduardo152030/mailerblend-platform-infra/pull/88).
