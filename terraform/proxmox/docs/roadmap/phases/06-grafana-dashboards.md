# Fase 6. Grafana & Dashboards

Estado: **DONE**. Cierre: **2026-11-10 (Europe/Madrid)**, D-060.
[Roadmap](../ROADMAP.md) · [Estado actual](../CURRENT-STATUS.md) · [Decisiones](../DECISIONS.md)

## Objetivo y alcance aprobado

Fleet Overview y LXC Details útiles, con métricas reales, navegación bidireccional,
provisioning reproducible y preservación de los siete dashboards anteriores.
La solicitud D-060 establece once criterios verificables de cierre; no exige
nueva UAT de aplicaciones ni aceptación visual humana separada para cerrar.
El navegador automatizado sí se ejecutó. La dispensa de F3 no se amplía.

## Tareas

| ID | Tarea | Estado | Resultado |
|---|---|---|---|
| F6-01 | Datasource, UID y variables de las vistas entregadas | DONE | Datasource existente, selectores dinámicos, consultas de17 CT y navegador; modelos heredados conservados |
| F6-02 | Resolver mounts y providers duplicados | DONE | Dos providers únicos; receta Compose con tres mounts efectivos e imagen fijada, sin reiniciar Grafana activo |
| F6-03 | Entregar Fleet y LXC Details | DONE | Salud/uptime/recursos, Docker por LXC, aplicaciones, monitoring y alertas; navegación ida/vuelta |
| F6-04 | Validar rango, navegación y persistencia | DONE | Navegador, CT 614/615/618/613; arranque aislado del candidato final desde snapshot consistente, sin recrear producción |
| F6-05 | Documentar provisioning y recuperación | DONE | Manual, transacción acotada, backup CT/fuera PVE, restore-check, idempotencia y rollback con protección de eliminación |

## Implementación, pruebas, despliegue y cierre

Dos dashboards entregados en CT 611; nueve modelos provisionados por archivos IaC.
Los siete anteriores conservan UID, carpeta y contenido, incluidos tres exportados
antes presentes solo en SQLite. No se afirma que todas sus consultas heredadas
hayan sido auditadas de nuevo.

34 casos sintéticos relevantes, 663 consultas instantáneas en17 CT, 28 históricas,
navegador sin errores con654 frames y navegación real PASS. Comparación uptime PVE
para17 CT y tres endpoints independientes: diferencia máxima20 s, límite45 s.
Ensayo aislado final10 nov: nueve dashboards cargados, sin red ni puertos publicados,
misma imagen, candidato exacto y SQLite consistente. Grafana activo no se reinició.
Idempotencia final:0 escrituras/0 recargas/0 reinicios.

Revisión10 nov08:08 CET:17 Node/17cAdvisor/18 Blackbox y exporter PVE UP; reglas F5 y targets
conservados; sin FIRING/PENDING ni UNKNOWN en salud consolidada de los17 CT.
[Resultado final](../evidence/2026-11-10-d060-result.json).

DONE según los once criterios D060, no UAT de negocio ni afirmación de recreación
productiva. Implementado, probado y desplegado; sin commit/push por restricción
expresa. Siguiente fase: F7, sin ejecución autorizada por este cierre.

## Límites documentados

No contador fiable de reinicios Docker; estado Docker representa cgroup observado
fresco. Disco es capacidad real del filesystem, no cuota Terraform. Descripciones
de alertas muestran contrato IaC y enlazan evaluación/activeAt a Prometheus. Rutas de
inventarios locales solo si existen, sin URLs web inexistentes. Readiness y medias
de sondas no certifican UAT ni disponibilidad durante huecos. Altas necesitan
publicar inventario/targets medianteIaC; no hay despliegue automático deexporters.
Scrape propio Grafana, observabilidad completa del host y seguridad/DR/aplicaciones
siguen como complementos F4/F7; no bloquean los criterios autorizados de esta fase.

## Evidencias y operación

- [Cierre D060 y once criterios](../PHASE6-D060-CLOSURE.md).
- [Manual Fleet/Details](../../../services/infra-grafana/FLEET-OVERVIEW.md).
- [Navegador](../evidence/2026-11-09-d060-browser.json), [consultas](../evidence/2026-11-09-d060-promql.json), [uptime](../evidence/2026-11-09-d060-uptime.json).
- [Persistencia aislada](../evidence/2026-11-10-d060-recreation-replay-final-20261110.json).
- [Tiempos y revisión documental](../evidence/2026-11-10-d060-closure-validation.json).

Historial: [D052](../PHASE6-D052-EXECUTION.md),
[D053](../PHASE6-D053-APPLICATION-HEALTH-AUDIT.md),
[D054](../PHASE6-D054-STAGE-A-EXECUTION.md),
[D056](../PHASE6-D056-UPTIME-EXECUTION.md),
[D057](../PHASE6-D057-COMPLETE-HEALTH.md). Bloqueos de esas etapas resueltos según
informes posteriores; no reejecutarlos ni reutilizar permisos históricos.
