# Fase 2. Telegram Alerting & Blackbox Deduplication

Estado: **DONE**. Actualizado: 2026-11-02 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo

Entregar incidentes y resoluciones por Telegram, conservando contratos diferentes y evitando avisos equivalentes.

## Alcance y dependencias

Receptor Telegram, secretos por archivo, readiness/reload e identidad de sondas/alertas. No incluye rutas por severidad ni nuevos umbrales.

Dependencias: F1; bot/chat configurados; acceso saliente y configuración Alertmanager válida.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F2-01 | Validar entrega FIRING y RESOLVED | DONE | Propietario confirmó ambas; contadores y prueba controlada documentados |
| F2-02 | Corregir carrera SIGHUP y SSH explícito de infra-prom | DONE | Despliegue previo e idempotencia; script conserva verificación estricta |
| F2-03 | Consolidar sondas equivalentes y preservar variantes útiles | DONE | 11 peticiones activas, dos Nucleotecnológico y un incidente lógico |
| F2-04 | Mantener vigilancia de errores de entrega | DONE | Regla existente; incremento de fallos reciente 0, no se borra el contador histórico |

## Implementación, validación, despliegue y aceptación

Desplegada y aceptada. La propuesta F4 suma 3 Journal en otro catálogo (14 futuras sondas totales); no modifica las 11 peticiones base ni constituye un despliegue nuevo.

## Riesgos

Telegram depende de Internet; readiness no acredita entrega. El endpoint Nucleotecnológico sigue en incidente y no se oculta por deduplicación. La configuración de inhibición avanzada queda para F5.

## Entregables

Catálogo aceptado de 11 sondas, reglas deduplicadas, receptor y runbook Telegram.

## Criterios de aceptación

FIRING/RESOLVED recibidos y confirmados; 11 sondas base correctas; variantes conservadas; reglas sanas; sin nuevos fallos de envío. Aceptados previamente por el propietario.

## Evidencias y referencias

- [TELEGRAM](../../../services/infra-prom/TELEGRAM.md).
- [DEDUPLICATION](../../../services/infra-prom/DEDUPLICATION.md).
- [Validación desplegada](../../../services/infra-prom/PHASE2-INCIDENTS.md).
- [Catálogo base](../../../services/infra-prom/config/targets/blackbox.json).
- [Snapshot de targets/contadores](../evidence/2026-11-02-monitoring-audit.json).
