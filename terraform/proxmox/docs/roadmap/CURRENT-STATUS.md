# Estado actual del proyecto

Actualizado: **2026-11-10 (Europe/Madrid)**. Cierre D-060.
[Roadmap](ROADMAP.md) · [Decisiones](DECISIONS.md) · [Informe F6](PHASE6-D060-CLOSURE.md).

## D-061 — cierre del alcance solicitado

**7.1 Git Consolidation: DONE.** Cinco commits principales publicados por SSH
normal, sin force; main/origin sincronizados0/0. Cierre documental separado.
**7.4: READY FOR FIRST REAL PROVISIONING TEST.** Flujo sobre módulo/inventario
existentes, dos fixtures con/sinDocker, Notes/ficha, exporters/targets/candidatos
preparados y dos planes mock1alta/0cambios/0destrucciones. Ningún CT creado.
**7.2 Security Hardening y7.3 Disaster Recovery: OUT OF SCOPE**, no DONE.
Cambios ajenos y secretos/estado/backups locales conservados fuera del commit.
[Informe](PHASE7-D061-EXECUTION.md), [Git](evidence/2026-11-10-d061-git-published.json),
[runbook](../runbooks/NEW-LXC-PROVISIONING.md).

## Fase actual

**Fase 6. Grafana & Dashboards — DONE**, conforme a los once criterios autorizados
D-060. Fases1–5 conservan sus cierres y límites de aceptación. **Fase7 IN PROGRESS**
con alcance D061:7.1 publicada y7.4 preparada;7.2/7.3 OUT OF SCOPE, no DONE.

Fleet Overview y LXC Details están desplegados, enlazados en ambos sentidos y
verificados en navegador. Los nueve dashboards son IaC, incluidos siete anteriores
preservados con UID, modelo y carpeta. Providers duplicados resueltos; receta
Compose con tres mounts efectivos e imagen actual fijada por digest.
Environment y tabla Componentes Docker no reaparecen en Fleet; Docker sí está en Details.

## Producción comprobada

Lectura **10 nov08:08 CET**:17/17 Node,17/17cAdvisor,18/18 Blackbox y exporter PVE UP;
sondas success1, tres checks periódicos Odoo/PG con resultado1, sin FIRING/PENDING.
Reglas F5 y catálogo de targets idénticos a baseline D060. Grafana disponible y
nueve dashboards provisionados. Salud consolidada de17 CT sin UNKNOWN y uptime real.
[Resultado](evidence/2026-11-10-d060-result.json).

CT 613 sin app de negocio verificada; Application N/A, sin exención por DEMO.
CT 621 ping JSONFocalboard; CT 623 Odoo8069+PG y CT 625 pg_isready periódicos; CT 618 readiness CRM.
CT 611/616 N/A solo como negocio; Monitoring real. STOPPED solo desde PVE.

## Validación y persistencia

Implementación/navegador09 nov:34 escenarios,663 consultas instantáneas/28 históricas,
654 frames reales, filtros y navegación CT/rango, sin errores. Uptime comparado con PVE
para17 CT, máximo20 s. Revisión10 nov y reaplicación final sin escrituras/recargas/
reinicios; sin cambios en Grafana activo ni reglas/targets.

Persistencia probada por arranque aislado del candidato exacto y SQLite consistente,
misma imagen, red none/sin puertos; nueve modelos cargados y carpetas conservadas.
Ensayo detenido y preservado. No recreación de Grafana productivo ni nueva UAT de apps.
[Ensayo final](evidence/2026-11-10-d060-recreation-replay-final-20261110.json).
Backups CT/fuera PVE y originales conservados, sin commits/push.

## Pendientes externos a F6

| Estado | Pendiente | Límite / siguiente acción |
|---|---|---|
| TODO | F4-05: scrape propio Grafana | Job aún ausente; sonda HTTP no lo sustituye |
| IN PROGRESS | F4-06: observabilidad completa del host | Estado/uptime CT resueltos; host físico completo no aceptado |
| TODO | F7: secretos históricos/estado Terraform, SSH/TLS global, CI/herramientas y DR continuo | No resueltos por snapshots o cierre de dashboards |
| TODO | Digest EVA, prevenciónsGTM, UAT/GA4 y deriva inventario/discos | Requieren alcance específico; no certificados por HTTP/readiness |
| DONE | Consolidación Git curada D061 | Publicada; cambios funcionales ajenos conservados fuera del commit |

Límites representados:sin contador fiable de reinicios Docker; capacidad del filesystem
en vez decuota PVE/Terraform; descripción decontrato dealerta con evaluación enlazada
a Prometheus; inventarioslocales sin hospedaje web. No quedan componentes esenciales
pendientes dentro de los once criterios F6. Aceptación visual humana no se inventa;
D060 autoriza el cierre tras comprobaciones objetivas y de navegador.

## Autorización y siguiente paso

La solicitud D060 autorizó provisioning Grafana y sondas necesarias; no se requirieron
sondas nuevas. Se preservan apps/DB/recursos/secretos/F5/Telegram por alcance.
D061 completado: publicación curada y preparación local, sin crear CT ni desplegar
servicios. Ejecución detenida. El primer ensayo real requiere un CT y alcance aprobados. No `deploy-all`, reinicios, recursos,
apps/DNS/credenciales ni borrado de backups. La prohibición de publicar deD060
queda sustituida solo en el alcanceD061. [InformeF7](PHASE7-D061-EXECUTION.md).

## Historial

[Revisión anterior D059](DOCUMENTATION-D059-REVIEW.md),
[historial previo](CURRENT-STATUS-HISTORY.md),
[decisiones](DECISIONS.md). Los informes originales conservan sus fechas/evidencias;
no reutilizar siguientes pasos históricos como permisos actuales.

## Preparado frente a desplegado en D061

Compatibilidad sinDocker en regla de ausencia y dashboards es código preparado,
no recargado en producción. Los17actuales mantienen el despliegueD060/F5 intacto.
El primer CTsinDocker exige autorización e integración coordinada de ese cambio.
Bootstrap/recibo son candidatos locales; estabilidad, segunda aplicación real y
cadena end-to-end no están probadas por mocks. Siguiente: autorización específica
del primer alta real. Sin hardening/DR global ni rotación histórica.
