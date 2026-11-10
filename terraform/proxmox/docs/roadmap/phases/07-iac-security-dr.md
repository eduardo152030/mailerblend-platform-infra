# Fase 7. IaC Reliability, Security & Disaster Recovery

Estado: **IN PROGRESS**. Actualizado: 2026-11-10 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Alcance vigente D061 — numeración del propietario

| Subfase | Estado | Alcance |
|---|---|---|
| 7.1 Git Consolidation | DONE | D061: cinco commits principales publicados, origin/main sincronizado; cierre documental separado |
| 7.2 Security Hardening | OUT OF SCOPE | Decisión expresa; no DONE ni rotación de secretos históricos |
| 7.3 Disaster Recovery | OUT OF SCOPE | Decisión expresa; no DONE ni política global DR nueva |
| 7.4 Automated LXC Provisioning | READY FOR FIRST REAL PROVISIONING TEST | Flujo/fixtures/mocks preparados, sin creación ni aplicación real |

[Informe D061](../PHASE7-D061-EXECUTION.md),
[runbook de altas](../../runbooks/NEW-LXC-PROVISIONING.md).
7.4 no equivale al ID históricoF7-04, que trata secretos. Las tareas históricas
inferiores conservan sus antecedentes; no autorizan ejecutar7.2/7.3 en esta sesión.
El cierreD042 solo cubría aquella publicación, no estos cambios posteriores.

## Objetivo

Cerrar las diferencias entre reproducibilidad declarada y operación real, con seguridad y recuperación sostenidas.

## Alcance y dependencias

Herramientas fijadas, CI, inventario/estado, SSH/TLS, secretos, backups, retención y restauraciones periódicas. Trabajo de fiabilidad de aplicaciones heredado que requiera alcance específico.

Dependencias: Inventario real, resultados F3/F4 y decisiones del propietario sobre seguridad, retención, RPO/RTO y ventanas.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F7-01 | Consolidar commits curados y documentación de cambios previos | DONE | D042: monitorización curada publicada; apps ajenas preservadas fuera de alcance; [evidencia](../evidence/2026-11-06-git-consolidation.json) |
| F7-02 | Eliminar dependencia de promtool/amtool en /tmp | TODO | Versiones y checksums reproducibles, sin usar latest |
| F7-03 | Idempotencia/readiness y backups para todos los deploys | TODO | Prom/CRM/EVA tienen mejoras; deploy-cadvisor-all sigue usando rm -f |
| F7-04 | Retirar/rotar secretos heredados y proteger estado Terraform | TODO | .env nuevo ignorado no resuelve perm.env/tfstate/tfvars ya rastreados |
| F7-05 | Revisar SSH/TLS/privilegios y autenticación de métricas | TODO | Terraform insecure y opciones SSH heredadas; no modificadas ahora |
| F7-06 | Definir DR sostenido, retención, RPO/RTO y ensayos periódicos | TODO | Restauraciones F3 pasadas no equivalen a una política continua |
| F7-07 | Corregir digest EVA y dependencia apk de su arranque | TODO | Heredados; requiere revisión funcional y aprobación de cualquier cambio de imagen/comando |
| F7-08 | Revisar RAM temporal CRM y deriva de inventario/discos | TODO | No reducir ni aplicar Terraform general automáticamente |
| F7-09 | Automatizar validación local/CI y continuidad del roadmap | IN PROGRESS | D059: documentación consolidada y APIs contrastadas; CI y política de commits pendientes |

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

Preparación histórica: 2026-11-06 (Europe/Madrid). F7-01 entonces IN PROGRESS, autorizado commit/push normal de
cambios seguros. Respaldo privado verificado;230tests, validadores Prom/AM, enlaces
y diff --check PASS. Estados/credenciales locales preservados y excluidos del
índice; secretos históricos pendientes de rotación (F7-04 no DONE). Sin producción.
[Auditoría, alcance y pendientes](../GIT-CONSOLIDATION-D042.md).

Cierre D042: push principal confirmado, main/origin iguales (0/0); F7-01 DONE
solo para consolidación de monitorización. F7 global IN PROGRESS y F7-04 pendiente.
Árbol residual preservado, sin aceptar cambios de aplicaciones. Ver evidencia D042.

## Seguimiento D059

F7 global IN PROGRESS; F7-01 DONE solo para el conjunto publicado D042. El árbol
actual tiene trabajo posterior y cambios ajenos sin consolidar, sin nueva
publicación ni sincronización remota afirmada. Documentación actualizada, APIs
leídas y enlaces locales comprobados; no despliegues ni aceptación de seguridad/DR.
[Informe](../DOCUMENTATION-D059-REVIEW.md). Siguiente: revisión F6 y autorización
específica del pendiente elegido; sin commits/push.

## Handoff D060 — F6 cerrada

2026-11-10: F6DONE; nueve dashboards IaC, providers/mountsGrafana saneados ymisma
imagen fijada enrecipe, sin recrear activo. Persistencia ensayadaaisladamente.
Esto no cierra seguridad/secretos/CI/DR global ni publica el trabajo posteriorD042.
[InformeF6](../PHASE6-D060-CLOSURE.md). Próximo: elegir yautorizar un pendienteF7;
no intervención productiva ni commits/push autorizados por ese cierre.

## Cierre D061

2026-11-10:7.1 DONE, publicación normal SSH verificada;7.4 READY FOR FIRST REAL
PROVISIONING TEST, con mocksDocker/nativo ysin creación real.7.2/7.3 OUT OF SCOPE
por decisión, nunca DONE. Los estados históricos de deuda no autorizan ejecutarlas.
No nuevosCT/apps/DNS/recursos ni despliegues productivos; cambios funcionales ajenos
conservados. Próximo: definir yautorizar primerCTreal, no ejecutado por este cierre.
[Informe](../PHASE7-D061-EXECUTION.md), [Git](../evidence/2026-11-10-d061-git-published.json).
