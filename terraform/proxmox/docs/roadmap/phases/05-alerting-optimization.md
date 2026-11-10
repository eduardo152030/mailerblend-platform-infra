# Fase 5. Alerting Optimization

Estado: **DONE — Accepted**. Actualizado: 2026-11-09 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo

Conseguir alertas accionables con severidades y frecuencia coherentes con los recursos reales.

## Alcance y dependencias

Warning/Critical, for, rutas Telegram, inhibición, agrupación, repetición y duración del incidente RESOLVED. No silenciar incidentes reales para mejorar el aspecto del panel.

Dependencias: F4 con métricas verificadas y contratos de disponibilidad aceptados; F2 como base de entrega.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F5-01 | Revisar umbrales y ventanas for por recurso | DONE | D050: métricas reales 17 CT, 26 alertas, cuatro conjuntos de fixtures |
| F5-02 | Definir rutas por severidad y repetición | DONE | D050: Telegram por severidad, cuatro pruebas de rutas/fallback |
| F5-03 | Corregir inhibición Critical → Warning | DONE | D050: cinco inhibiciones y quince aserciones con Alertmanager real aislado |
| F5-04 | Añadir duración RESOLVED y probar agrupación | DONE | D050: hora Madrid, duración, plantilla HTML y deduplicación; propietario confirma claridad |
| F5-05 | Probar FIRING/RESOLVED y rollback tras autorización | DONE | D050: cadena real CPU, API132→134/errores56 constantes, ambos recibidos; rollback preventivo ejecutado y backup restaurado en staging |

## Implementación, validación, despliegue y aceptación

Implementación IaC y recargas aplicadas en CT610. Prometheus/Alertmanager READY, 17 Node/17 cAdvisor/11 Blackbox conservados, 26 alertas y 34 entradas de grabación sanas. Segunda aplicación sin escrituras/recargas. Ensayo CPU real FIRING/RESOLVED recibido y claro según confirmación explícita del propietario; regla temporal retirada. [Informe, umbrales, riesgos y procedimiento](../PHASE5-D050-EXECUTION.md).

## Riesgos

Cambiar etiquetas puede resolver/reabrir incidentes por identidad. Inhibición demasiado amplia oculta fallos; ventanas cortas crean ruido. Datos LXC incorrectos invalidan umbrales.

## Entregables

Reglas y rutas revisadas, tests promtool/amtool con fixtures, matriz de severidad y runbook.

## Criterios de aceptación

Reglas sanas; fixtures demuestran thresholds/for/inhibición; un incidente genera avisos justificados; duración correcta; entrega real validada tras despliegue autorizado; rollback probado y aceptación registrada.

## Evidencias y referencias

- [Reglas actuales](../../../services/infra-prom/config/rules/infra-hosts.yml).
- [Alertmanager](../../../services/infra-prom/config/alertmanager/alertmanager.yml).
- [Plantilla Telegram](../../../services/infra-prom/config/alertmanager/templates/telegram.tmpl).
- [Validación](../../../scripts/validate-monitoring.sh), [fixtures](../../../tests/monitoring/alerts.test.yml).

## Ejecución D-050 autorizada

Auditoría, reglas/plantillas/rutas y recargas exclusivas Prometheus/Alertmanager,
backup restaurable externo, ensayo por regla temporal sobre CPU real sin carga.
Sin apps, exporters, recursos, reinicios LXC, commits ni push. Se conserva 17/17/11.
Se preparan pares RAM/disco y TLS, salud Docker y ausencia de métricas por CT,
autovigilancia y rutas por severidad. CRM/EVA unhealthy preexistente no se oculta.

## Cierre histórico D050

2026-11-07: DONE — Accepted dentro del alcance de alerting.
[Evidencia final](../evidence/2026-11-07-d050-result.json). Sin apps/exporters/recursos,
reinicios LXC, commit/push. Tres healthchecks unhealthy CRM/EVA son incidencias
preexistentes que ahora tienen cobertura; no se declaran resueltos. Grafana/CRM
no tienen nueva prueba HTTP específica; ampliación y AM adicional quedan separados.
En aquel cierre F6 requería autorización; posteriormente D052–D058 ejecutaron Fleet. No es un bloqueo actual.

## Seguimiento D051 — origen de tres WARNING corregido

2026-11-07: [healthchecks CRM/EVA](../HEALTHCHECKS-D051-EXECUTION.md) corregidos y
validados con autorización específica. Tres healthy/health1 y cero alarmas objetivo
FIRING; cobertura y reglas F5 conservadas. No se silencian incidencias ni se
aumentan umbrales. F5 DONE — Accepted se mantiene; sin UAT de negocio nueva.

## Estado contrastado D059

26 alertas / 34 de grabación sanas, sin FIRING/PENDING; Prom/AMREADY 200.
18 Blackbox actuales por ampliaciónF6;17 Node/17 cAdvisor conservados. No nuevo
ensayoTelegram ni cambios de reglas. [Evidencia](../evidence/2026-11-09-d059-documentation-audit.json).
