# Fase 7. IaC Reliability, Security & Disaster Recovery

Estado: **IN PROGRESS**. Actualizado: 2026-11-02 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo

Cerrar las diferencias entre reproducibilidad declarada y operación real, con seguridad y recuperación sostenidas.

## Alcance y dependencias

Herramientas fijadas, CI, inventario/estado, SSH/TLS, secretos, backups, retención y restauraciones periódicas. Trabajo de fiabilidad de aplicaciones heredado que requiera alcance específico.

Dependencias: Inventario real, resultados F3/F4 y decisiones del propietario sobre seguridad, retención, RPO/RTO y ventanas.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F7-01 | Consolidar commits curados y documentación de cambios previos | IN PROGRESS | Árbol amplio sin commit; no incluir secretos/estado ni cambios ajenos por lote |
| F7-02 | Eliminar dependencia de promtool/amtool en /tmp | TODO | Versiones y checksums reproducibles, sin usar latest |
| F7-03 | Idempotencia/readiness y backups para todos los deploys | TODO | Prom/CRM/EVA tienen mejoras; deploy-cadvisor-all sigue usando rm -f |
| F7-04 | Retirar/rotar secretos heredados y proteger estado Terraform | TODO | .env nuevo ignorado no resuelve perm.env/tfstate/tfvars ya rastreados |
| F7-05 | Revisar SSH/TLS/privilegios y autenticación de métricas | TODO | Terraform insecure y opciones SSH heredadas; no modificadas ahora |
| F7-06 | Definir DR sostenido, retención, RPO/RTO y ensayos periódicos | TODO | Restauraciones F3 pasadas no equivalen a una política continua |
| F7-07 | Corregir digest EVA y dependencia apk de su arranque | TODO | Heredados; requiere revisión funcional y aprobación de cualquier cambio de imagen/comando |
| F7-08 | Revisar RAM temporal CRM y deriva de inventario/discos | TODO | No reducir ni aplicar Terraform general automáticamente |
| F7-09 | Automatizar validación local/CI y continuidad del roadmap | TODO | Roadmap/AGENTS creados; falta integración de CI y política de commits |

## Implementación, validación, despliegue y aceptación

No iniciada como intervención global. Se reconocen mejoras parciales anteriores, sin convertirlas en aceptación de toda la fase.

## Riesgos

Estado Terraform puede contener secretos; no publicarlo. Limpiar Git no revoca credenciales. TLS/SSH mal migrados bloquean accesos. Un apply general puede cambiar otros servicios. No reducir RAM CRM sin evaluar carga y posible reinicio del proveedor.

## Entregables

Cadena de herramientas reproducible, validaciones CI, procedimientos seguros, inventario contrastado y política DR con pruebas periódicas.

## Criterios de aceptación

Herramientas instalables con versiones/checksums fuera de /tmp; pruebas CI; secretos nuevos y heredados gestionados; planes acotados sin deriva inesperada; segundos despliegues sin cambios; backups externos restaurados según RPO/RTO aprobados; rollback y control de acceso ensayados. No cumplidos globalmente.

## Evidencias y referencias

- [README](../../../README.md), [Makefile](../../../Makefile), [main.tf](../../../main.tf).
- [Deploy Prom](../../../services/infra-prom/deploy-prom.sh), [deploy común](../../../scripts/deploy-common.sh), [cAdvisor heredado](../../../scripts/deploy-cadvisor-all.sh).
- [Backups/restauración F3](../../../services/infra-prom/PHASE2-EXECUTION.md).
- [DECISIONS](../DECISIONS.md), [AGENTS](../../../AGENTS.md).


## D-042 — consolidación Git

2026-11-06 (Europe/Madrid). F7-01 IN PROGRESS, autorizado commit/push normal de
cambios seguros. Respaldo privado verificado;230tests, validadores Prom/AM, enlaces
y diff --check PASS. Estados/credenciales locales preservados y excluidos del
índice; secretos históricos pendientes de rotación (F7-04 no DONE). Sin producción.
[Auditoría, alcance y pendientes](../GIT-CONSOLIDATION-D042.md).
