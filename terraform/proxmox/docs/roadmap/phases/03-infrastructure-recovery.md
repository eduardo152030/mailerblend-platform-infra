# Fase 3. Infrastructure Recovery — CRM & EVA

Estado: **DONE — Accepted with UAT Waiver**. Actualizado: 2026-11-09 (Europe/Madrid).
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo

Recuperar disponibilidad CRM y margen de almacenamiento EVA preservando completamente datos y rollback.

## Alcance y dependencias

Recuperación conservadora Budibase 3.27.4, RAM temporal 6 GiB, backups fríos, restauraciones aisladas, caché/journal y logging EVA. No incluye nuevas imágenes de aplicación, resolver todos los healthchecks ni corregir el digest heredado.

Dependencias: F1/F2; aprobación explícita de recuperación y sus excepciones; backups externos íntegros y restauración funcional.

## Tareas

| ID | Tarea | Estado | Evidencia / pendiente |
|---|---|---|---|
| F3-01 | Recuperar CRM con una instancia y conservar ambos /data | DONE | Overlay aplicado, worker y app originales detenidos, mismo software/datos |
| F3-02 | Crear/verificar backups y restauraciones aisladas | DONE | CRM CT 9618 y EVA CT 9622; copias externas descifradas/checksum; pruebas funcionales |
| F3-03 | Recuperar >=25% libre en EVA y limitar crecimiento | DONE | ~7,9 GB recuperados; ~34,15% libre; journal/logging aplicados |
| F3-04 | Validar exporters, recursos e idempotencia | DONE | Cuatro up=1 durante 10 min; sin OOM nuevos; segunda aplicación sin reinicios |
| F3-05 | Obtener decisión del propietario sobre aceptación/UAT | DONE | Aceptación formal y dispensa expresa; UAT NO ejecutada |

## Implementación, validación, despliegue y aceptación

Implementada, validada, desplegada y aceptada. La prueba manual adicional de login y flujos de negocio no se ejecutó y fue dispensada por el propietario. Esto NO demuestra que todos los flujos funcionales fueran probados. No hay recuperación pendiente de ejecutar.

## Riesgos

Los OOM previos pudieron afectar operaciones antes del backup; no se certifican todos los flujos. Los tres healthchecks heredados se corrigieron posteriormente bajo D051; permanece el digest heredado; RAM CRM no se reduce automáticamente. Las copias no tienen purga automática.

## Entregables

Recuperación desplegada, backups y ensayos, runbooks y evidencias; decisión formal D-011.

## Criterios de aceptación

Verificaciones técnicas/automatizadas y restauraciones aisladas pasadas; servicios operativos según lo comprobado; preservación de datos/volúmenes e idempotencia. Aceptación formal del propietario el 2026-11-02 con UAT dispensada. Cumplidos bajo esa dispensa, no bajo una UAT ejecutada.

## Evidencias y referencias

- [PHASE2-EXECUTION](../../../services/infra-prom/PHASE2-EXECUTION.md): nombre histórico, corresponde a F3.
- [RECOVERY CRM](../../../services/infra-composable-crm/recovery/RECOVERY.md).
- [STORAGE-PLAN EVA](../../../services/infra-eva-assistant-bot/recovery/STORAGE-PLAN.md).
- [D-011](../DECISIONS.md).
- [Revalidación de solo lectura](../evidence/2026-11-02-runtime-audit.json).

## Seguimiento D051 (2026-11-07)

[Corrección de los tres healthchecks](../HEALTHCHECKS-D051-EXECUTION.md): healthy
y alertas resueltas con IaC, imagen/entorno/datos/recursos conservados. No es una
repetición de recuperación F3 ni de su restauración DB; no amplía su dispensa UAT.
