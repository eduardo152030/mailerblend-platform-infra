# CT618 — Monitorización del CRM activo

21/11/2026 Europe/Madrid. Ronda `implementation`, base
`d6cc3fef5911e6fe99a3f3e9364bd20654118f20`. Rama
`ops/crm-618-monitoring`, worktree `../mailerblend-platform-infra-crm-monitoring`.
El propietario solicita retirar Budibase del contrato y cubrir los
componentes activos. Inventario vivo: UI, API, GoTrue, PostgreSQL y worker
de notificaciones. Quitamos la expectativa de Budibase y preservamos su
contenedor detenido. Añadir presencia para los cinco, sondas HTTP para
UI/API/GoTrue, healthchecks nativos donde existen y frescura para el worker.
Aplicar solo archivos acotados de Prometheus y los dos dashboards Grafana,
sin reiniciar aplicaciones ni servicios de observabilidad.

## Resultado

Budibase estaba detenido y `ApplicationContainerMissing` estaba FIRING.
Se retiró solo su expectativa. Se registraron tres sondas HTTP estrictas
desde Blackbox y la cobertura de los cinco contenedores. Las siete series
de salud valían 1. Prometheus y Alertmanager sin alertas de CT618 tras la
convergencia. Grafana autenticado confirmó Fleet HEALTHY y Details con los
cinco componentes. Las sondas HTTP miden su propia latencia interna.
La presencia del worker no certifica que un aviso haya sido entregado.

Promtool y pruebas PromQL de Fleet/Details PASS. Segunda aplicación de
CT610 y CT611: sin cambios. Se preservaron los IDs activos de CT618.
Los respaldos de los archivos modificados se conservaron en CT610/611 y
se copiaron fuera de PVE. Para revertir, aplicar el script de activación
con `--rollback` en cada host y su bundle original. No se ejecutó
rollback en producción.

[PR #93](https://github.com/eduardo152030/mailerblend-platform-infra/pull/93).
