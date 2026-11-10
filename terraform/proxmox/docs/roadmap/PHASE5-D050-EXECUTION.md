# Fase 5. Alerting Optimization — D-050

Seguimiento: 2026-11-07 (Europe/Madrid). Estado: **DONE — Accepted**.
[Roadmap](ROADMAP.md) · [Estado](CURRENT-STATUS.md) · [Fase](phases/05-alerting-optimization.md)

## Alcance y autorización

Solicitud del propietario: implementar y aplicar únicamente reglas, rutas y
plantillas Prometheus/Alertmanager; prueba controlada FIRING/RESOLVED. Sin cambios
de apps, exporters, recursos, volúmenes, reinicios LXC, commits ni push. F4 17/17
no se repite. Se conservan los 17 Node, 17 cAdvisor y 11 Blackbox y sus etiquetas.

## Auditoría y resultado del candidato

Baseline: 15 alertas y 21 reglas de grabación. Candidato: **26 alertas y 34 reglas
de grabación (60 entradas)**; las 17 entradas del inventario CPU comparten nombre
pero representan CT diferentes, no alertas duplicadas. Se añaden 13 entradas de
inventario de contenedores esenciales con identidades service/name revisadas.

12 alertas nuevas: HostMemoryPressure, HostDiskAlmostFull,
DockerContainerUnhealthy, SgtmHealthFailed, LxcMemoryMetricsMissing,
LxcDockerMetricsMissing, ApplicationContainerMissing, BlackboxScrapeFailed,
MonitoringReloadFailed, PrometheusRuleEvaluationFailed,
PrometheusNotificationErrors, PrometheusAlertmanagerMissing.

14 alertas conservadas reciben CT cuando existe y enlace Prometheus. CPU utiliza
exclusivamente lxc:cpu_usage:percent; desaparece la rama física legacy. ExporterDown
separa el fallo de scrape de una sonda (BlackboxScrapeFailed) del exporter mismo.
TLS y recursos incorporan etiquetas de correlación para inhibición. Se conserva
la agregación de variantes de sondas y TLS por incidente lógico.

Se elimina HostMemoryFillingFast: extrapolaba cualquier caída lineal de RAM sin
exigir presión actual. Se sustituye por capacidad disponible sostenida, sin subir
los límites críticos existentes ni ocultar incidentes. container-restarts.yml sigue
vacío: no se inventa un contador de reinicios a partir de tiempos de inicio.

Contexto real: 17 fuentes CPU fiables; máximo de CPU en 24h ≈58,6% (CRM), los demás
<17%; MemAvailable actual >54%; disco root libre mínimo ≈28,5% (Prom610), EVA≈33,4%.
La ventana histórica contiene migraciones de etiquetas: no mezclar memoria legacy
con cpu_contract=lxc_cgroup_v1. Se conservan CPU90/10m, RAM10/5m y disco15/10m;
los nuevos avisos anticipan capacidad y el disco crítico atiende agotamiento.

## Umbrales y severidades

| Regla / condición | Umbral | for | Severidad |
|---|---|---|---|
| HostHighCpuUsage | CPU LXC >90%, rate5m/capacidad cgroup | 10m | WARNING |
| HostMemoryPressure | MemAvailable <20% | 10m | WARNING |
| HostLowMemory | MemAvailable <10% | 5m | CRITICAL |
| HostDiskFilling | Libre / <15%, FS reales | 10m | WARNING |
| HostDiskAlmostFull | Libre / <5% | 5m | CRITICAL |
| HostOutOfService | Node up=0 | 2m | CRITICAL |
| ExporterDown | cAdvisor/Blackbox exporter/Prom/AM up=0 | 2m | CRITICAL |
| BlackboxScrapeFailed | scrape de sonda up=0 | 2m | CRITICAL |
| LxcCpuTargetMissing | inventario sin target de contrato esperado | 2m | WARNING |
| LxcCpuCollectorInvalid | CPU ausente/obsoleta/inválida según contrato F4 | 2m | WARNING |
| LxcMemoryMetricsMissing | inventario sin MemAvailable | 2m | WARNING |
| LxcDockerMetricsMissing | inventario sin container_last_seen con nombre | 2m | WARNING |
| DockerContainerUnhealthy | health=0; -1 significa sin check | 5m | WARNING |
| SgtmHealthFailed | health=0, Serving/Preview CT614/615 | 2m | CRITICAL |
| ApplicationContainerMissing | falta contenedor esencial esperado | 2m | CRITICAL |
| NoInternetConnectivity / PublicUrlDown / CollectEndpointDown / InternalEndpointDown | probe_success=0 | 2m | CRITICAL |
| SSLCertExpiringSoon / SSLCertExpiringVerySoon | <14d / <7d | 30m / 15m | WARNING / CRITICAL |
| AlertmanagerDeliveryErrors | increase(failed[10m])>0 | 1m | WARNING |
| MonitoringReloadFailed | última recarga Prom/AM=0 | 1m | CRITICAL |
| PrometheusRuleEvaluationFailed | errores de evaluación en 5m >0 | 2m | CRITICAL |
| PrometheusNotificationErrors | errores de envío a AM en 5m >0 | 2m | CRITICAL |
| PrometheusAlertmanagerMissing | AM descubiertos <1 | 2m | CRITICAL |

Las expresiones de ausencia comparan inventario esperado con series; no sustituyen
por cero. Alertname lo genera la regla; severity se declara; instance y service se
conservan de las series o se asignan explícitamente en autovigilancia. Summary y
description están en annotations; ct_id procede de ct_id/vmid. Docker se une al
inventario CPU por service sin modificar los exporters.

## Rutas, agrupación e inhibiciones

Receptor principal único Telegram, send_resolved=true. Agrupación:
[alertname, service, instance], manteniendo separados incidentes de apps diferentes.

| Ruta | group_wait | group_interval | repeat_interval |
|---|---|---|---|
| CRITICAL | 15s | 1m | 1h |
| WARNING | 30s | 5m | 6h |
| INFO (solo ensayo; ninguna regla permanente informativa) | 15s | 1m | 24h |
| Fallback para severidad desconocida | 30s | 5m | 4h |

Cinco inhibiciones:

1. CRITICAL→WARNING con mismo instance/service/resource y recurso memory/disk/tls.
2. SgtmHealthFailed→DockerContainerUnhealthy con mismo instance/service/name.
3. HostOutOfService→LxcCpuCollectorInvalid/LxcMemoryMetricsMissing del mismo service.
4. ExporterDown/cAdvisor→LxcDockerMetricsMissing del mismo service.
5. ExporterDown/Blackbox exporter→BlackboxScrapeFailed: las 11 sondas dependen
   del único Blackbox configurado. No inhibe probe_success=0 ni apps independientes.

## Telegram y salud de aplicaciones

Plantilla HTML concisa, hasta cuatro alertas del grupo. Estado, severidad, service,
CT/nombre cuando existe, summary, descripción/valor/umbral, hora Europe/Madrid,
fin y duración en RESOLVED. Enlace a /alerts de Prometheus, válido en la red de
operación; no se publica una URL de Grafana sin validar. Sin token/chat ID ni URLs
collect con parámetros en los mensajes. Las direcciones internas de identidad no
se repiten como campos adicionales.

Serving/Preview se vigilan mediante container_health_state de sus checks nativos
/healthz recuperados en D044/D048. La sonda collect HEAD sigue siendo cobertura
HTTP diferente y no demuestra salud de bootstrap ni entrega GA4. Sin eventos
Analytics de prueba ni modificación de sondas/aplicaciones.

CRM/EVA: se detectan **tres unhealthy preexistentes**, budibase-app y crm-api en
CT618 y focalboard en CT622. Se notifican como WARNING; no se reparan ni silencian.
EVA API/DB y los cuatro sGTM tienen health=1. Ausencia de healthcheck (-1) no es
salud ni fallo: Grafana/Blackbox se cubren por presencia y disponibilidad existente,
no se declara una nueva prueba HTTP de Grafana/CRM. Añadir esos probes y corregir
los healthchecks de aplicaciones son pendientes separados, no un fallo de F4.
Un Alertmanager adicional preexistente (eloquent_ganguly) se conserva; no se hace
limpieza ni se afirma redundancia funcional.

Semántica de salud: [código cAdvisor](https://github.com/google/cadvisor/blob/master/lib/metrics/prometheus.go).
Formato temporal: [referencia Alertmanager](https://prometheus.io/docs/alerting/latest/notifications/).
Validación con los binarios exactos de las imágenes instaladas.

## Procedimiento reproducible y rollback

[scripts/phase5-alerting.py](../../scripts/phase5-alerting.py) limita operaciones a
CT610, SSH estricto con known_hosts del propietario y BatchMode. Baseline privado
bajo $HOME/.local/share/mailerblend-recovery/phase5/d050; copia CT610 bajo
/opt/infra-prom/.runtime/phase5-d050. Se incluyen config, Compose, configuración
renderizada AM y token en archivo privado; no se añaden backups/secretos a Git.
SHA256 CT/fueraPVE y restauración de archivos a staging comparados antes de aplicar.
No se extraen backups sobre producción para ensayar restauración.

Secuencia: baseline→prepare→validate→revisión diff→apply→verify→segunda apply→
test-on→observación firing→test-off→observación resolved→cleanup→verify.
No se usa deploy-all, Terraform apply ni Compose up. Conserva Prometheus config,
targets, inventario CPU real y runtime token/chat ID. Escribe solo el conjunto de
hashes revisado; respeta el inode del bind mount individual de Alertmanager.
Comprueba recarga efectiva por timestamp y éxito en ambos servicios, espera primera
evaluación, confirma identidades/arranques y cobertura. Una segunda aplicación
idéntica no escribe ni recarga. Rechaza drift y backups alterados.

Rollback: acción rollback con este baseline; retira únicamente su ensayo si
coincide su hash, restaura archivos afectados y recarga, sin recrear contenedores.
Ante fallo de apply, restauración automática antes de propagar el error. No usar
este checkpoint sobre cambios futuros ni borrar originales/backups/evidencias.

## Validación y ejecución

- promtool check config/rules, cuatro conjuntos de fixtures: umbrales, for,
  recuperación, CPU aceptada, ausencia, deduplicación, salud -1/0/1 y contenedor esencial.
- amtool check-config, render HTML FIRING/RESOLVED y cuatro rutas con fallback.
- Alertmanager real aislado local: quince aserciones de inhibición/independencia,
  sin integración de notificaciones ni contactos externos.
- [Auditoría AST/series](../../scripts/audit-phase5-series.py): entradas reales de
  las 26 alertas; el inventario app nuevo se valida al cargarse, no se considera
  ausencia inesperada durante preparación.
- Primera aplicación: rollback preventivo al comprobar health=unknown antes de
  primera evaluación. Hashes originales restaurados; errores de evaluación/envío
  en 10m=0. Se corrigió la espera del validador (hasta dos ciclos, aborta lastError)
  y se repitió el mismo alcance autorizado. No se relajaron umbrales ni criterios.
- Segunda aplicación y prueba de cadena: resultados finales en evidencia enlazada
  al cierre. El ensayo usa CPU LXC real>=0, for30s; no carga artificial ni POST AM.
  La aceptación API de Telegram se distingue de confirmación humana del receptor.

## Pendientes y aceptación

Recepción humana confirmada explícitamente por el propietario: «Recibidos ambos y claros». La dispensación
F3 no se extiende a F5. No atribuir los for productivos de 10/30m al ensayo corto:
los prueban los fixtures; la cadena usa su regla temporal independiente.

## Cierre y evidencia final

[Resultado verificable](evidence/2026-11-07-d050-result.json). **DONE — Accepted**.
26 alertas/34 entradas de grabación sanas; 17Node/17cAdvisor/11Blackbox UP y ambos
READY. Hashes activos iguales al candidato revisado y arranques/IDs intactos.
Segunda aplicación sin escrituras ni recargas, comprobada antes y después del ensayo.
Todos los inputs de las 26 alertas existen tras cargar el inventario nuevo de13.

52 casos en cuatro conjuntos de fixtures PASS, cuatro rutas y quince aserciones
de inhibición con AM aislado PASS. Enlaces locales y diff-check verificados al cierre.

Cadena real: FIRING en Prometheus y AM, contador Telegram132→133; RESOLVED con
regla inactiva y contador133→134; errores históricos56→56. Confirmación humana
para ambos y claridad móvil; no dispensa. Regla temporal retirada y no quedan
alertas del ensayo. Tres DockerContainerUnhealthy WARNING preexistentes sí están
FIRING tras cumplir5m: CRM budibase-app/crm-api y EVA focalboard. Son resultado
esperado de nueva cobertura, no degradación introducida ni motivo para silenciarlas.

Ejemplo renderizado desde el payload real del FIRING enviado (HTML de Telegram):

```html
🔴 <b>FIRING</b>

<b>INFO · infra-prom</b>
CT 610 ·
Prueba Fase 5 sin incidencia real
CPU real disponible; no se ha generado carga ni eventos Analytics.
Valor: 1.02% · Umbral: &gt;=0% (solo ensayo)
Inicio: 07/11 13:41:59 CET

<a href="http://192.168.1.110:9090/alerts">Ver monitorización</a>
```

El RESOLVED usa la misma identidad y añade fin/duración; ambos mensajes recibidos
según el propietario. No se atribuye al ensayo la duración de los for productivos.

Discrepancia heredada: prometheus.yml del repositorio contiene preparación adicional
respecto al activo. D050 conserva el activo en vez de activar Grafana/discovery
incidentalmente. Reglas/AM/plantilla sí coinciden con IaC; el generador F4 mantiene
el inventario CPU. No utilizar deploy genérico para reproducir solo esta intervención.

Tiempo total hasta evidencia: **17.4 minutos**, desde primera lectura del adjunto
(2026-11-07T13:30:53.235765+01:00) hasta 2026-11-07T13:48:19.541644+01:00. Incluye auditoría, implementación,
pruebas, aplicación, rollback preventivo, idempotencia y recepción Telegram.
Incluye documentación y revisión final; sin cambios productivos adicionales.

Siguiente: Fase 6. Grafana & Dashboards, pendiente de alcance y autorización.
No commit/push ni continuación automática. Backups/originales conservados.
