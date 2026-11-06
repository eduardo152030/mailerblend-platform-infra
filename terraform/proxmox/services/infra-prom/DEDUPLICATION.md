# Fase 1: deduplicación de sondas e incidentes

Desplegado y validado el 2026-11-02 con autorización explícita. Esta ejecución
conservó contenedores y no necesitó SIGHUP. Las fases de recursos, exporters,
severidades y herramientas de instalación quedan fuera de este cambio.
Telegram se considera validado por las pruebas FIRING y RESOLVED del destinatario.

## Evidencia y decisiones

Se compararon `/api/v1/targets`, los módulos efectivos de Blackbox en `/config`,
los JSON locales y las reglas cargadas. El módulo efectivo `http_2xx` usa GET,
permite redirecciones y acepta 200/204/301/302. `http_2xx_strict` usa GET, no sigue
redirecciones y acepta 200/204. `http_collect_200` usa HEAD, no sigue redirecciones
y acepta 200/204. Ninguna de estas sondas verifica el procesamiento de eventos GA4.

| Servicio | Antes | Contrato y equivalencia | Decisión y cobertura conservada |
|---|---|---|---|
| svc01 | 3 | GET raíz con `http_2xx`. Dos URLs idénticas y una con `/`; una URL sin path envía igualmente `/` en HTTP. Solo cambian etiquetas. | Un GET a `https://infra-svc01.mailerblend.com/`. Sin pérdida de cobertura funcional. `service=svc01` coincide con inventario. |
| Documentación | 2 | Misma URL `https://infra-doc.mailerblend.com/` y mismo módulo. | Una sonda; sin pérdida de cobertura. |
| Mailerblend collect | 3 | Misma URL completa, parámetros y módulo HEAD; etiquetas `name`/`service` distintas. | Una sonda con los mismos parámetros. Se mantiene el contrato HEAD 200/204. |
| Nucleotecnológico collect | 2 | Mismo endpoint, módulo, v/en/tid/dl decodificados; `cid=blackbox-test` frente a `cid=local-cli-test`. Ambas fallan sin respuesta HTTP; eso no demuestra equivalencia del comportamiento de la aplicación. | Se conservan ambas URLs completas y ambos client IDs; un incidente lógico si falla cualquiera. Cero pérdida de cobertura. |
| Internet | 2 | Misma URL Google, módulos distintos: seguir redirecciones frente a exigir respuesta directa. | Se conservan ambos contratos; un incidente de conectividad si falla cualquiera. |
| Pulpo, EVA | 1 cada uno | GET público con `http_2xx`. | Se conservan. |
| Prometheus, Alertmanager | 1 cada uno | GET interno `/-/healthy` con `http_2xx_strict`. | Se conservan; no se sustituyen por readiness en esta fase. |

Referencias remotas anteriores: `blackbox-infra-svc01.json`,
`blackbox-infra-doc.json`, `blackbox-edge-collect.json`,
`blackbox-edge-mailerblend-collect.json` y `blackbox-edge-nucleotecnologico.json`.
Los antiguos `blackbox-http.json`, `blackbox-collect.json`,
`blackbox-internet.json` y `blackbox-internal-critical.json` estaban también
representados en el repositorio. Sus definiciones conservadas se incorporan al catálogo.

## Fuente declarativa e identidad

`config/targets/blackbox.json` contiene las 11 peticiones conservadas, frente a
16 targets activos observados antes del cambio. No añade servicios nuevos.
Cada petición tiene `probe_id` único, `service`, `module`, `probe_type`,
`alert_target` y, para HTTPS, `tls_target`.

Prometheus lee solamente este archivo para el job Blackbox. Los archivos antiguos
que rsync conserva en el servidor dejan de participar en discovery; no se borran.
El nombre `blackbox.json` no coincide con el wildcard anterior `blackbox-*.json`:
la copia del nuevo catálogo no activa sondas adicionales antes de recargar Prometheus.

Se eliminan del árbol local los cuatro JSON antiguos consolidados. El generador de
Node Exporter/cAdvisor/Grafana no modifica este catálogo.

Las métricas conservan `instance` con la URL completa y `probe_id` de cada petición.
Las reglas de disponibilidad normalizan únicamente la identidad de la alerta a
`alert_target` y agregan el mínimo por job/servicio/tipo/endpoint. Cualquier variante
fallida activa un único incidente; todas deben recuperarse para resolverlo.
Las reglas TLS usan el mínimo de expiración por servicio e identidad TLS, para no
repetir la misma advertencia por módulos o parámetros distintos.

No cambian umbrales, tiempos `for`, severidades, rutas Telegram ni persistencia.
La agrupación conserva incidentes de servicios diferentes; no silencia una sonda
fallida porque otra variante esté sana.

Los detalles por variante se consultan con:

```promql
probe_success{job="blackbox",service="edge-nucleotecnologico-collect"}
probe_success{job="blackbox",service="internet"}
```

## Validación local

Desde `/home/jainer/work/mailerblend-platform-infra/terraform/proxmox`:

```bash
python3 scripts/validate-blackbox-targets.py
python3 tests/monitoring/test_blackbox_catalog.py
./scripts/validate-monitoring.sh
```

El último comando mantiene los requisitos actuales de promtool/amtool y el `.env`
ignorado. Si todavía no están en PATH, utilizar los overrides documentados en
TELEGRAM.md. Eliminar esa dependencia de instalación pertenece a la fase 5.

El catálogo se valida automáticamente antes de desplegar. Las pruebas verifican
peticiones únicas, cobertura anterior, variantes conservadas, discovery explícito,
un único incidente ante variantes fallidas, recuperación y deduplicación TLS.
La validación completa de preparación se realizó con herramientas oficiales y
secretos ficticios en un directorio temporal, sin tocar los secretos reales.

## Procedimiento de despliegue

```bash
READINESS_TIMEOUT=120 READINESS_INTERVAL=2 \
  ./services/infra-prom/deploy-prom.sh
```

Comprobar después 11 targets Blackbox activos, métodos/módulos correctos y las dos
variantes de Nucleotecnológico. Esperar al menos el `for` de 2 minutos más margen
de scraping/evaluación. Si persiste la caída, PublicUrlDown de svc01 debe tener una
instancia y CollectEndpointDown de Nucleotecnológico una instancia. Las métricas
crudas deben seguir mostrando las dos variantes de Nucleotecnológico.

La normalización cambia etiquetas/fingerprints. Durante la migración puede haber
RESOLVED de las identidades antiguas y FIRING de las nuevas tras su `for`, aunque
el endpoint no se haya recuperado. No confundir esa transición con una recuperación.
No se prometen alertas nuevas para variantes que estén ausentes de discovery: la
validación de cobertura esperada se ampliará en su fase correspondiente.

## Rollback de esta fase

Se guardó una copia de la configuración realmente desplegada, sin token ni `.env`,
en `.rollback/phase1-20261102T090137Z/config/`, bajo un directorio ignorado y restringido.
Incluye discovery anterior y la regla Blackbox anterior. El despliegue conserva
además su backup remoto habitual antes de sincronizar.

Tras aprobación de rollback, restaurar en el árbol local **solo** `prometheus.yml`,
`rules/blackbox-alerts.yml` y los JSON Blackbox anteriores de esa copia. Validar y
redesplegar con el mismo procedimiento IaC. Revertir también la invocación del nuevo
validador de catálogo si se vuelve a la estructura anterior; no mezclar ambas versiones.
No restaurar `.env`, el Chat ID, reglas de recursos o volúmenes como parte de este rollback.
El wildcard anterior volverá a leer los JSON conservados en el servidor; el nuevo
`blackbox.json` no coincide con ese wildcard y queda fuera. Confirmar los 16 targets
anteriores. La deduplicación se revierte, pero la entrega Telegram permanece configurada.

## Resultado del despliegue autorizado

Ver [PHASE2-INCIDENTS.md](PHASE2-INCIDENTS.md) para el backup verificado,
las comprobaciones de API, el estado de entrega y los incidentes que permanecen.
