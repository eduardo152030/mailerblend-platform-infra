# Fase 6. Grafana & Dashboards — D-057 salud LXC completa

Estado: **DONE técnico para este alcance**, Fase 6 global **IN PROGRESS**.
Cierre: 2026-11-09 09:44 CET (Europe/Madrid). Aceptación visual del propietario pendiente.

## Resultado y evidencias

17/17 filas reales, cero UNKNOWN; Infrastructure/Monitoring/Overall HEALTHY en esta
instantánea. No garantiza disponibilidad futura ni acredita UAT de negocio.
STOPPED solo desde pve_up fresco, nunca ausencia de exporters. No se apagó ningún CT;
la rama STOPPED se probó con PromQL sintético, no mediante parada productiva.

| CT ID | Service | Infrastructure Health | Application Health | Monitoring Health | Overall Status | Uptime |
|---|---|---|---|---|---|---|
| 610 | infra-prom | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:58:02 |
| 611 | infra-grafana | HEALTHY | NOT APPLICABLE | HEALTHY | HEALTHY | 52d 11:57:59 |
| 613 | infra-hola | HEALTHY | NOT APPLICABLE | HEALTHY | HEALTHY | 1d 15:43:55 |
| 614 | infra-nucleoedge | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:57:52 |
| 615 | infra-mailerblend-edge | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:57:48 |
| 616 | infra-blackbox | HEALTHY | NOT APPLICABLE | HEALTHY | HEALTHY | 52d 11:57:44 |
| 617 | infra-orbit | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:57:40 |
| 618 | infra-composable-crm | HEALTHY | HEALTHY (readiness) | HEALTHY | HEALTHY | 6d 22:06:42 |
| 619 | infra-pulpo | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:57:29 |
| 620 | infra-excraper | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:57:24 |
| 621 | infra-project-gestion | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:57:18 |
| 622 | infra-eva-assistant-bot | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 6d 19:34:21 |
| 623 | infra-gestoria | HEALTHY | HEALTHY (readiness) | HEALTHY | HEALTHY | 52d 11:57:01 |
| 624 | infra-journal-web | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:56:40 |
| 625 | infra-journal-db | HEALTHY | HEALTHY (readiness) | HEALTHY | HEALTHY | 52d 11:56:33 |
| 626 | infra-journal-api | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:56:20 |
| 61211 | svc01 | HEALTHY | HEALTHY | HEALTHY | HEALTHY | 52d 11:56:13 |


Fuente: [despliegue](evidence/2026-11-09-d057-deployment.json), marcas UTC conservadas.
Uptime API PVE real; los valores de la tabla son una instantánea, no reloj estático.

## Cuatro casos pendientes

- **613**: inventario/Terraform y runtime contrastados: solo Node/cAdvisor y servicios
  del SO; Postfix loopback-only, sin app de negocio desplegada. Application NOT
  APPLICABLE fundamentado; DEMO es metadato. CPU/RAM/disco/exporters/uptime y PVE
  supervisados como los demás. Un apagado no implica mantenimiento autorizado.
- **621**: Focalboard7.10.0, puerto8081→8000. No healthcheck Docker configurado.
  `/ping` devuelve JSON propio con version7.10.0/db_type sqlite3/sku personal_server;
  Blackbox valida200 y los tres campos. `/api/v2/ping` HTML descartado. Se acredita
  liveness HTTP de la aplicación, no un flujo autenticado ni escritura en SQLite.
- **623**: Odoo17 en127.0.0.1:8069; PostgreSQL15 solo5432 internoDocker. Salud JSON
  `/web/health` y formulario Odoo `/web/login`, más pg_isready interno como usuario
  postgres existente. Nginx8080 de pruebas no se usa. Readiness conjunta, no UAT.
- **625**: PostgreSQL16-alpine en192.168.1.125:5432 preexistente; pg_isready dentro
  del contenedor. No puertos nuevos ni exposición pública añadida; sin SQL ni claves.

[Runtime sanitizado](evidence/2026-11-09-d057-runtime.json).

## IaC y despliegue

[Contratos/checker](../../services/common/functional-health/checks.yml) con timers15s
ya instalados el07nov; reanudación verifica contenido exacto y timer activo sin
reescribirlos. Tres series lxc_app_check_success y sus timestamps, éxito1/fallo0/
incertidumbre-1; publicación atómica en textfileNode existente, no modifica CPU.
Sonda621 adicional mediante [contrato](../../services/infra-prom/config/phase6/complete-health.yml),
file_sd aditivo, un módulo Blackbox y dashboard provisionado. Inventario dinámico
por métricas/IaC: ninguna lista manual de17CT en Grafana. Altas futuras requieren
inventario/targets IaC, no edición manual del dashboard.

[Ejecutor](../../scripts/phase6-complete-health.py),
[generador](../../scripts/generate-fleet-dashboard.py),
[manual Fleet](../../services/infra-grafana/FLEET-OVERVIEW.md).
Cambios productivos: configuración610/611/616; SIGHUP Prometheus/Blackbox y polling
Grafana, sin reiniciar servicios. Apps/DB/recursos/volúmenes/identidades conservados.
Reglas y umbralesF5 idénticos; otros siete dashboards y datasources idénticos.

## Seguridad, validación e idempotencia

SSH estricto, backups nuevos privados CT/fueraPVE y extracción con comprobación
hash antes de aplicar; archivos antiguos y backups07nov conservados. Namespace
privado d057-20261109; rollback coordinado del ejecutor conserva configuración
inicial610/611/616. Collectors623/625 preexistentes quedan fuera de ese rollback:
no fueron modificados en esta intervención. No secretos en evidencia pública.

Correcciones locales del ejecutor: file_sd candidato correcto; comparación canónica
de Mounts porque Docker cambia su orden entre lecturas. El hash opaco07nov no
permitía comparar configuración; línea base nueva, sin asumir ausencia de cambios
históricos. Dos lecturas frescas demostraron diferencias solo de orden en613.

- promtool y parser Blackbox real PASS; revisión semántica: solo un file_sd y módulo.
- 16 escenarios nuevos de PromQL PASS y 14 de regresión EtapaA PASS. La expectativa
  antigua de endpointUP sin recursos se actualiza a DEGRADED, conforme al contrato.
- [30 consultas reales](evidence/2026-11-09-d057-promql.json),17CT únicos en tabla/recursos.
- [Navegador](evidence/2026-11-09-d057-browser.json): uptime/filtros/rango/enlace PASS,
  cero errores de consulta/JS. [Captura](evidence/2026-11-09-d057-fleet.png).
-17Node/17cAdvisor/18Blackbox UP y success1; señales funcionales frescas; sin FIRING.
- Segunda aplicación:0escrituras/0recargas/0reinicios; collectors idénticos.
- Prometheus READY; reglas sanas; Grafana API/UI operativo y dashboard provisionado.

[Resultado y tiempos](evidence/2026-11-09-d057-result.json):3,5min desde línea base
hasta verificación; lectura inicial y cierre documental fuera de ese cronómetro.
No repetición de pruebas extensasF4/F5, sin pruebasTelegram ni commits/push.

## Pendientes y siguiente paso

Cero UNKNOWN actuales. N/A solo en Application de613/611/616; Monitoring real para
los17. Readiness no certifica disponibilidad pública ni transacciones de negocio.
No se modifica healthcheck Docker ni se requieren nuevos privilegios.
F6 global conserva pendientes de providers/otras vistas/persistencia por recreación;
no se declaran aceptados. Siguiente: revisión visual del propietario del Fleet.
Ejecución detenida, sin avance a otra etapa.
