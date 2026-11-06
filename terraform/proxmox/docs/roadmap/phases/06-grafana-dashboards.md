# Fase 6. Grafana & Dashboards

Estado: **TODO**. Actualizado: 2026-11-02 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo

Mostrar información útil y correcta, con dashboards reproducibles y navegación por servicio/ámbito.

## Alcance y dependencias

Datasource, provisioning, UID, variables de job/service/instance, dashboards host/LXC/Docker/app. El scraping de Grafana pertenece a F4.

Dependencias: F4; taxonomía de etiquetas y fuentes aceptadas. Acceso autorizado para comprobar provisioning/UI sin exponer credenciales.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F6-01 | Auditar datasource/UID y variables de dashboards | TODO | No inferir dashboard sano de /api/health 200 |
| F6-02 | Resolver mounts duplicados y dos providers default | TODO | Conflictos locales observados; contrastar runtime antes de cambiar |
| F6-03 | Construir/ajustar vistas PVE, LXC, Docker y aplicaciones | TODO | Usar métricas de F4 verificadas |
| F6-04 | Validar rango temporal, reinicio y persistencia | TODO | Requiere autorización de despliegue/reinicio y aceptación visual |
| F6-05 | Documentar provisioning/rollback sin borrar grafana_data | TODO | Conservar dashboards/usuarios existentes |

## Implementación, validación, despliegue y aceptación

Grafana responde, pero dashboards y provisioning no se han aceptado ni corregido en esta intervención.

## Riesgos

Consultas para jobs/datasources antiguos producen paneles vacíos. Mounts repetidos y providers con mismo nombre hacen que el YAML local no represente el runtime. Latest no es un pin reproducible.

## Entregables

Provisioning coherente, dashboards versionados y evidencia de consultas/UI con datos reales.

## Criterios de aceptación

Paneles CPU/RAM/disco/Docker correctos para los 17 servicios dentro del alcance; datasource conectado; variables y UID estables; provisioning idempotente sin duplicados; datos y usuarios preservados; aceptación visual tras despliegue.

## Evidencias y referencias

- [Compose Grafana](../../../services/infra-grafana/compose/docker-compose.yml).
- [Datasource](../../../services/infra-grafana/config/provisioning/datasources/datasource.yml).
- [Provider 1](../../../services/infra-grafana/config/provisioning/dashboards/default.yml), [provider 2](../../../services/infra-grafana/config/provisioning/dashboards/provider.yml).
- [Node dashboard](../../../services/infra-grafana/config/dashboards/node-exporter-full.json).
- [Health y métricas HTTP](../evidence/2026-11-02-supplementary-audit.json).
