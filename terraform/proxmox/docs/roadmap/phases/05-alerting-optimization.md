# Fase 5. Alerting Optimization

Estado: **TODO**. Actualizado: 2026-11-02 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo

Conseguir alertas accionables con severidades y frecuencia coherentes con los recursos reales.

## Alcance y dependencias

Warning/Critical, for, rutas Telegram, inhibición, agrupación, repetición y duración del incidente RESOLVED. No silenciar incidentes reales para mejorar el aspecto del panel.

Dependencias: F4 con métricas verificadas y contratos de disponibilidad aceptados; F2 como base de entrega.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F5-01 | Revisar umbrales y ventanas for por recurso | TODO | Basar CPU/RAM en límites LXC correctos |
| F5-02 | Definir rutas por severidad y repetición | TODO | Requiere decisión del propietario; receptor único actual |
| F5-03 | Corregir inhibición Critical → Warning | TODO | Revisar igualdad alertname y pares reales; probar no silenciar incidentes distintos |
| F5-04 | Añadir duración RESOLVED y probar agrupación | TODO | Plantilla actual muestra fechas UTC, no duración |
| F5-05 | Probar FIRING/RESOLVED y rollback tras autorización | TODO | No enviar nuevas pruebas a Telegram durante esta reorganización |

## Implementación, validación, despliegue y aceptación

Optimización no iniciada. Las reglas básicas desplegadas no equivalen a esta fase completada.

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
