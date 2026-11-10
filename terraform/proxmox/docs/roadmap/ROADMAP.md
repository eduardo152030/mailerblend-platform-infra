# Roadmap de infraestructura

Actualizado: **2026-11-10 (Europe/Madrid)** — Fase 7 acotada, D-061.
Fuente central del proyecto Proxmox, Terraform, Docker Compose y monitorización.
Leer [CURRENT-STATUS](CURRENT-STATUS.md) para retomar; las autorizaciones y decisiones
se conservan en [DECISIONS](DECISIONS.md).

## Estado real por fase

| Fase | Estado | Implementación, producción y aceptación |
|---|---|---|
| [1. Monitoring Foundation](phases/01-monitoring-foundation.md) | DONE | Base Prometheus/Alertmanager desplegada y verificada; cobertura ampliada en F4/F6 |
| [2. Telegram Alerting & Blackbox Deduplication](phases/02-telegram-blackbox.md) | DONE | Entrega FIRING/RESOLVED confirmada; 11 sondas base aceptadas, ampliadas posteriormente a 18 en F6 |
| [3. Infrastructure Recovery — CRM & EVA](phases/03-infrastructure-recovery.md) | DONE — Accepted with UAT Waiver | Recuperación aceptada el 02 nov; dispensa expresa, sin UAT manual adicional. Healthchecks corregidos después en D051 |
| [4. Exporters & Monitoring Coverage](phases/04-exporters-coverage.md) | DONE — cobertura exporters 17/17 | Rollout cerrado D041; CPU LXC/cgroup, RAM LXCFS y cAdvisor por CT. Complementos abiertos en ficha, sin reabrir rollout |
| [5. Alerting Optimization](phases/05-alerting-optimization.md) | DONE — Accepted | D050: 26 alertas y 34 entradas de grabación; cadena real recibida y clara, rollback e idempotencia verificados |
| [6. Grafana & Dashboards](phases/06-grafana-dashboards.md) | DONE | D060: Fleet y LXC Details desplegados, navegación y17 CT verificados; nueve dashboards IaC, persistencia aislada e idempotencia PASS |
| [7. IaC Reliability, Security & Disaster Recovery](phases/07-iac-security-dr.md) | IN PROGRESS | D061:7.1 publicación en curso;7.4 READY FOR FIRST REAL PROVISIONING TEST;7.2/7.3 OUT OF SCOPE, no DONE |

DONE se refiere al alcance acreditado. Un test local no prueba un despliegue;
un despliegue no equivale a aceptación ni a UAT de negocio.

## Intervención vigente D061

Autorizados commits/push normal y preparación local de altas sobre el móduloIaC
existente. No crear CT, aplicar Terraform, modificar producción, recursos/apps/DNS/
credenciales. 7.2/7.3 OUT OF SCOPE por decisión, no aceptadas como completadas.
7.4 preparada con dos mocks (Docker/nativo), Notes/ficha y planes1create/0update/
0destroy; primer ensayo real pendiente. [Informe](PHASE7-D061-EXECUTION.md),
[runbook](../runbooks/NEW-LXC-PROVISIONING.md).

## Última comprobación real y cierre F6

**10 nov08:08 CET:**17 Node/17cAdvisor/18 Blackbox y exporter PVE UP, sondas correctas,
sin FIRING/PENDING. Nueve dashboards provisionados, los siete anteriores conservados;
salud consolidada17/17 sin UNKNOWN. Uptime real comparado con PVE; máximo20 s en ensayo09 nov.
Fleet↔Details con CT/rango comprobado en navegador. Reaplicación final sin escrituras/
recargas/reinicios y persistencia mediante arranque aislado del candidato exacto.
[Resultado final](evidence/2026-11-10-d060-result.json),
[cierre y once criterios](PHASE6-D060-CLOSURE.md).
No se afirma recreación de Grafana activo, nueva entrega Telegram ni UAT de negocio.

## Pendientes vigentes y siguiente paso

| Área | Pendiente real | Evidencia / límite |
|---|---|---|
| Complementos F4 | Scrape propio Grafana y observabilidad completa del nodo físico | Job Grafana ausente; estado/uptime CT resueltos, no host completo aceptado |
| F7 | Rotación histórica, estado Terraform, SSH/TLS global, herramientas/CI y política DR/retención | [Ficha F7](phases/07-iac-security-dr.md); no aceptación global |
| Aplicaciones | Digest EVA, prevencióncaducidadsGTM, UAT/GA4 y deriva inventario/discos | Trabajos separados; no se ejecutan por cierre F6 |
| Git | Trabajo posterior a D042 y cambios ajenos en el árbol | No commits/push autorizados todavía |

F6 DONE por los once criterios D060; no se bloquea por mejoras opcionales o UAT de apps.
Siguiente: revisión del resultado y seleccionar un pendiente F7/complemento F4 con
alcance explícito. Ejecución detenida; no avanzar automáticamente ni borrarbackups.

## Seguimiento y evidencias

- [Estado vigente y autorizaciones](CURRENT-STATUS.md).
- [Decisiones aprobadas y propuestas](DECISIONS.md).
- [Cierre exporters D041](EXPORTERS-D041-CLOSURE.md).
- [Alerting D050](PHASE5-D050-EXECUTION.md), [healthchecks D051](HEALTHCHECKS-D051-EXECUTION.md).
- [Uptime PVE D056](PHASE6-D056-UPTIME-EXECUTION.md), [salud D057](PHASE6-D057-COMPLETE-HEALTH.md).
- [Presentación D058](evidence/2026-11-09-d058-presentation.json), [navegador](evidence/2026-11-09-d058-browser.json).
- [Revisión documental D059](DOCUMENTATION-D059-REVIEW.md).
- [Cierre F6 D060](PHASE6-D060-CLOSURE.md), [ensayo final](evidence/2026-11-10-d060-recreation-replay-final-20261110.json).
- [Historial del roadmap](ROADMAP-HISTORY.md), [historial del estado](CURRENT-STATUS-HISTORY.md).

## Numeración histórica

| Documentación anterior | Fase central actual |
|---|---|
| “Fase 1” de [DEDUPLICATION](../../services/infra-prom/DEDUPLICATION.md) | Fase 2 |
| “Fase 2” de [PHASE2-INCIDENTS](../../services/infra-prom/PHASE2-INCIDENTS.md) y [PHASE2-EXECUTION](../../services/infra-prom/PHASE2-EXECUTION.md) | Fase 3 |
| Investigación de aislamiento LXC y Docker | Fase 4 |
| Antiguas propuestas de optimización/documentación | Redistribuidas entre F5 y F7 |

## Cómo se actualiza

Identificar fase/tarea y autorización antes de actuar; registrar ampliaciones.
Mantener estados TODO/IN PROGRESS/BLOCKED/DONE y distinguir local, probado,
desplegado y aceptado. Actualizar ficha, roadmap y estado con evidencias fechadas,
riesgos y siguiente paso. Documentación en español, seguimiento Europe/Madrid,
marcas UTC históricas identificadas. Conservar historial y backups; comprobar
links/diff y excluir secretos/cambios ajenos de cualquier futuro commit.
