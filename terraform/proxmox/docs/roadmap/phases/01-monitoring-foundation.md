# Fase 1. Monitoring Foundation

Estado: **DONE**. Actualizado: 2026-11-09 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo

Establecer una base operativa de recogida, evaluación y persistencia para el resto del proyecto.

## Alcance y dependencias

Prometheus, Alertmanager, discovery y reglas básicas. La cobertura de los 17 servicios y la exactitud LXC pertenecen a F4; no se presentan como logradas aquí.

Dependencias: Inventario y LXC existentes, Docker Compose y conectividad de gestión.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F1-01 | Mantener Prometheus/Alertmanager operativos y persistentes | DONE | APIs readiness 200; configuración y runbooks existentes |
| F1-02 | Scraping/evaluación de 30s y carga de reglas | DONE | Base inicial 13 reglas; hoy 26 alertas / 34 de grabación sanas tras F5 (D059) |
| F1-03 | Establecer discovery y scraping de la base existente | DONE | Base inicial 14 Node / 14 cAdvisor; cobertura actual 17/17 cerrada F4 (D041/D059) |

## Implementación, validación, despliegue y aceptación

Base desplegada/verificada. La ampliación F4 está desplegada y cerrada en D041; su aceptación es independiente de la base F1.

## Riesgos

Prometheus puede recoger métricas equivocadas. La disponibilidad del exporter no prueba la de la aplicación. La persistencia local no sustituye una política DR (F7).

## Entregables

Base operativa, configuración de Prometheus y mecanismos de despliegue existentes.

## Criterios de aceptación

Prometheus y Alertmanager readiness 200; self-scrapes disponibles; reglas health=ok; persistencia declarada. Todos satisfechos para este alcance base, sin exigir aún los objetivos de F4.

## Evidencias y referencias

- [Auditoría real de monitoring](../evidence/2026-11-02-monitoring-audit.json).
- [Configuración Prometheus](../../../services/infra-prom/config/prometheus.yml) (ampliada por F4/F5/F6; runtime contrastado D059).
- [Compose Prometheus](../../../services/infra-prom/compose/docker-compose.yml).
- [Procedimiento operativo](../../../services/infra-prom/TELEGRAM.md).
- [Ejecución previa](../../../services/infra-prom/PHASE2-INCIDENTS.md).
