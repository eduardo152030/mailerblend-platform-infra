# Fase 6. Grafana & Dashboards — Etapa A, D-054

**Vigente D-056:** Uptime real17/17, [operación y fuentePVE](../infra-pve-uptime/README.md).
Los límites de UptimeUNKNOWN descritos abajo son históricosD054, resueltos porD056.

Alcance autorizado: monitorización Grafana611/Blackbox616, readiness CRM618,
Orbit617, workers620, Journal Web624/API626 y columna Uptime. Sin aplicaciones,
healthchecks Docker, recursos, umbrales/reglas F5, reinicios ni commits/push.
La etapa siguiente (613/621/623/625) queda excluida.

## Fuentes y estados

Application Health conserva las sondas anteriores. Para611/616 muestra
**NOT APPLICABLE**, porque son servicios de monitorización, y la nueva columna
**Monitoring Health** utiliza señales reales:

- Grafana: Blackbox a `/api/health`, HTTP200 y JSON `database=ok`. No NodeUP.
- Blackbox: su `up{job="blackbox_exporter"}` existente; aquí el exporter es el
  propio servicio monitorizado, no un sustituto de otra aplicación.

Overall Status exige la salud técnica de estos servicios, aunque Application
Health sea NOT APPLICABLE. Una sonda de Grafana fallida o el exporter Blackbox
caído produce CRITICAL, no un verde por clasificación.

CRM muestra **HEALTHY (readiness)** únicamente con los dos componentes requeridos
por `app:container:expected`: Budibase y CRM API. Se comprueba correspondencia entre
`name` y `container_label_com_docker_compose_service`, unicidad, cgroup Docker `id`
igual entre health y last_seen, frescura<=45s, timestamps válidos y cAdvisorUP.
Identidades de métricas y contenedores se contrastan con Docker antes/después.
Cualquier componente ausente, duplicado o antiguo conserva UNKNOWN. El fallo
conocido de la señal completa muestra CRITICAL. **No acredita disponibilidad
pública**, sesión de usuario ni UAT de negocio. No se modifica ningún Dockercheck.

## Nuevas sondas

[Contrato IaC aditivo](../infra-prom/config/phase6/application-health.yml):

| Servicio | Endpoint | Validación |
|---|---|---|
|Grafana611|`http://192.168.1.111:3010/api/health`|200 y `database=ok`|
|Orbit617|`https://edge.nucleotecnologico.es/orbit/healthz`|200 y cuerpo `ok`; ruta Nginx acreditada hacia617:18088/healthz|
|LinkedIn worker620|`http://192.168.1.120:3000/health`|200, statushealthy y servicelinkedin-worker|
|Signals worker620|`http://192.168.1.120:3001/health`|200, statushealthy y servicesignals-worker|
|Journal Web624|`http://192.168.1.124:8090/`|Contrato existente http_2xx_strict; frontend, no flujoAPI|
|Journal API626|`http://192.168.1.126:3000/health`|200 y statusok; contratoHTTP existente con comprobación del cuerpo|

Se preservan las11sondas anteriores; total17. No se publica el contrato TCP de625.
Nuevas sondas con probe_id único y etiquetas service/vmid/health_signal. El scraping
continúa cada30s. No se cambian alertas/umbrales ni Telegram. Los módulos añadidos
solo realizan GET, sin redirecciones, con TLS verificado. No se amplía la allowlist
de Orbit, no se usa `/ingest` ni se envían eventos Analytics. Los dos workers se
agregan exigiendo ambos targets; su liveness no acredita sesión LinkedIn, cuotas,
trabajos reales o conectividad con todos los proveedores externos.

## Uptime: investigación y límite explícito

`node_boot_time_seconds` presenta el mismo valor en los17CT y el uptime derivado
coincide con **el host Proxmox**. `node_time_seconds` es reloj de pared, no tiempo
transcurrido desde el arranque del LXC. No existe una serie LXC/PVE de boot/uptime
publicada en Prometheus. Se ha comparado con la API PVE para los17CT, superando
el mínimo solicitado de tres; en618 el desfase es de varias semanas.

Por ello **Uptime muestra UNKNOWN en los17CT**. No se publica el uptime del host
como si fuera LXC, ni se utiliza Docker/exporter como sustituto. La columna tiene
unidad de duración legible `dtdhms` y participa en el join dinámico por CT sin
eliminar ninguna columna existente. Para admitir valores exige una fuente de boot
con contrato explícito `boot_scope=lxc_verified`, NodeUP y duración no negativa y
finita. **Esa etiqueta/fuente no existe hoy y no se ha inventado ni desplegado**;
la consulta queda cerrada por defecto. Nuevos CT aparecen por inventario/targets,
con UNKNOWN hasta disponer de una señal acreditada.

Propuesta pendiente, no implementada: exporter/collector PVE que publique boot o
uptime por CT con identidad y frescura verificadas, bajo autorización separada.
El objetivo de una columna con valores reales para17CT no se declara cumplido;
solo están implementados la columna segura y el rechazo de la métrica incorrecta.

## Transacción, validación y recuperación

[phase6-stage-a.py](../../scripts/phase6-stage-a.py) utiliza SSH estricto,
backup CT/fueraPVE y restore-check de configuración en610/611/616. Baseline incluye
modelos de dashboards/datasources, targets, reglas e identidades de contenedores.
El candidato se construye desde configuración **activa verificada**, añadiendo solo
el catálogo propio, su referencia file_sd y módulos propios. No despliega el
catálogo global ni los jobs históricos de otro alcance.

```sh
python3 scripts/generate-fleet-dashboard.py
python3 scripts/validate-phase6-uptime.py
python3 tests/monitoring/test_phase6_stage_a.py
python3 scripts/phase6-stage-a.py baseline  # primera transacción, no sobrescribir
python3 scripts/phase6-stage-a.py prepare
python3 scripts/phase6-stage-a.py validate
python3 scripts/phase6-stage-a.py apply
python3 scripts/phase6-stage-a.py apply     # idempotencia
FLEET_EVIDENCE_ID=d054 python3 scripts/validate-fleet-browser.py
```

Validación: promtool sobre configuración completa con reglas heredadas intactas,
parser `--config.check` del binario Blackbox real, consultas PromQL, contratos
sintéticos de identidad/frescura/ausencia y arranque, navegador/filtros y aplicación
idéntica. No se repiten ensayos Telegram ni ventanas extensas de F4/F5.

Aplicación: escribir conservando inodes de mounts individuales, SIGHUP solo a
Blackbox y Prometheus; Grafana toma el JSON por polling. **Sin reiniciar o recrear
ningún contenedor.** Fallo revierte los archivos propios y recarga ambos lectores;
se conservan backups. No restaurar DB/volúmenes ni borrar originales.

Backups privados: `~/.local/share/mailerblend-recovery/phase6/d054` y
`/opt/infra-{prom,grafana,blackbox}/.runtime/d054/`. No versionar archivos privados.
El modelo JSON sigue aprovisionado bajo UID `proxmox-lxc-fleet`; no edición UI.
El estado histórico de D052 no es baseline válido para aplicar esta nueva etapa:
usar la transacción D054 coordinada, sin reutilizar backups antiguos a ciegas.
