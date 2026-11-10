# Fase 6. Grafana & Dashboards — D-054, Etapa A

**Etapa A DONE técnico. Fase 6 IN PROGRESS.** La columna Uptime está incorporada,
pero los valores reales están **BLOCKED por falta de fuente fiable**. No se
presenta la métrica del host como uptime LXC. Aceptación visual del propietario
pendiente. Sin aplicación de Etapa B, commits o push.

[Dashboard](http://192.168.1.111:3010/d/proxmox-lxc-fleet/proxmox-c2b7-lxc-fleet-overview?theme=dark) ·
[Procedimiento, contratos, uptime y recuperación](../../services/infra-grafana/PHASE6-STAGE-A.md).

## Resultado por CT

Application Health UNKNOWN **11→4**. Grafana y Blackbox no se clasifican como
aplicaciones de negocio; Monitoring Health muestra su salud real. CRM conserva
el significado de readiness interna. Uptime UNKNOWN no se oculta ni provoca una
salud global falsa; su ausencia no convierte los recursos válidos en datos fiables
de arranque.

| CT | Servicio | Application Health | Monitoring Health | Overall | Uptime |
|---|---|---|---|---|---|
|610|infra-prom|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|
|611|infra-grafana|NOT APPLICABLE|HEALTHY|HEALTHY|UNKNOWN|
|613|infra-hola|UNKNOWN|NOT APPLICABLE|UNKNOWN|UNKNOWN|
|614|infra-nucleoedge|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|
|615|infra-mailerblend-edge|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|
|616|infra-blackbox|NOT APPLICABLE|HEALTHY|HEALTHY|UNKNOWN|
|617|infra-orbit|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|
|618|infra-composable-crm|HEALTHY (readiness)|NOT APPLICABLE|HEALTHY|UNKNOWN|
|619|infra-pulpo|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|
|620|infra-excraper|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|
|621|infra-project-gestion|UNKNOWN|NOT APPLICABLE|UNKNOWN|UNKNOWN|
|622|infra-eva-assistant-bot|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|
|623|infra-gestoria|UNKNOWN|NOT APPLICABLE|UNKNOWN|UNKNOWN|
|624|infra-journal-web|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|
|625|infra-journal-db|UNKNOWN|NOT APPLICABLE|UNKNOWN|UNKNOWN|
|626|infra-journal-api|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|
|61211|svc01|HEALTHY|NOT APPLICABLE|HEALTHY|UNKNOWN|

## Aplicación y validación

- Backups de configuración CT610/611/616 y fueraPVE por SHA256; extracción en staging
  y hashes de todos los archivos cotejados. Backup/modelosAPI anteriores retenidos.
- Candidato aditivo desde runtime: referencia file_sd, catálogo propio y cinco
  módulos Blackbox para seis targets. Módulos/targets heredados conservados.
- Seis endpoints200 y contenido verificados desdeCT616. Ruta pública Orbit
  comprobada en NginxCT109 hacia617; sin ampliarallowlist ni enviar ingesta.
- Identidad CRM contrastada con DockerID real, Compose service, cgroupId compartido
  con last_seen, unicidad y frescura<=45s; ambos componentes requeridos.
- promtool sobre configcompleta/reglas, parserrealBlackbox y JSON PASS.26casos
  sintéticos relevantes:12anteriores y14EtapaA, incluyendo ausencias, antigüedad,
  identidades equivocadas/duplicadas, dosworkers y rechazo bootHOST. Sin suite F4/F5.
-28consultas reales PASS;11consultas tabla con17CT únicos, sin duplicados/NaN/Inf;
  recursos porcentuales correctos. FiltrosCT/servicio, rango1h, enlaces, estados
  tipados/readiness y Uptime en navegador PASS, sin errores detectados.
-17Node/17cAdvisor y11probes previas preservados;17BlackboxUP y probe_success1.
  Ninguna alerta FIRING; pendientes reportados en evidencia.26alertas/34recordings
  y sus definiciones/umbrales idénticos; Telegram no modificado.
- Recarga controladaSIGHUP de Prometheus/Blackbox; JSONGrafana porpolling.
  **Cero reinicios/recreaciones** de aplicaciones o monitorización, identidades y
  StartedAt/restartCount intactos. Siete dashboards ajenos ydatasources conservados.
- Segunda aplicación: **0escrituras/0recargas/0reinicios**. Backup/rollback coordinado
  disponible; no fue necesario rollback productivo en esta etapa.

## Uptime: evidencia y alcance pendiente

API PVE comparada para17CT, incluidos611/618/624. El boot de Node es idéntico en
17 y su duración coincide con elhost, mientras618 lleva mucho menos encendido.
node_time es reloj de pared; no hay métricas LXC/PVE de boot/uptime publicadas.
Se mantiene UNKNOWN en17CT según requisito6. No se instalaron collectors nuevos,
ni se alteraron exporters/contratos F4 o recursos.

La columna admite automáticamente nuevosCT por las etiquetas, conserva todas las
columnas anteriores y tiene unidad de duración; solo aceptaría una fuente LXC
explícitamente verificada. Un contrato de arranque futuro necesita autorización y
validación propia. **No se declara completado el objetivo de uptime medido de17CT.**

Otros límites:613sinapp/ciclo de vida;621contratoFocalboard;623Odoo local/DB;
625PostgreSQLreadiness. No se reclasifican ni reparan en EtapaA. Livenessworkers
no certifica tareas externas ni sesiones; JournalWeb no prueba integración conAPI;
readinessCRM no acredita acceso público/UAT. Providerslegados siguen pendientes.

## Evidencias

- [Resultado y tiempo](evidence/2026-11-07-d054-result.json).
- [Despliegue/estados/alertas](evidence/2026-11-07-d054-deployment.json).
- [Endpoints e identidadOrbit](evidence/2026-11-07-d054-endpoints.json).
- [Identidad y frescuraCRM](evidence/2026-11-07-d054-crm-readiness.json).
- [Comparación uptimePVE17CT](evidence/2026-11-07-d054-uptime.json).
- [PromQL](evidence/2026-11-07-d054-promql.json).
- [Navegador](evidence/2026-11-07-d054-browser.json), [captura](evidence/2026-11-07-d054-fleet.png).
- [Idempotencia](evidence/2026-11-07-d054-idempotence.json).

Seguimiento enEurope/Madrid; timestampsJSON conservados enUTC. Siguiente: revisión
visual del propietario y decisión de fuente uptime. No avance automático.
