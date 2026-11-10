# Uptime Proxmox centralizado — D-056

Implementación IaC aprobada para Fase 6. Grafana & Dashboards. Un solo exporter en
CT 610, sin agentes en los LXC ni uso de boot del host o uptime Docker.

## Fuente y descubrimiento

Se utiliza el paquete upstream `prometheus-pve-exporter==3.11.0`. Consulta la API
HTTPS de Proxmox en `192.168.1.100:8006` con los collectors resources/status; se
excluyen configuración por VM, backups, suscripciones y otras consultas por nodo.
La API descubre todos los LXC visibles a la identidad sin lista de VMID.

El [scrape](scrape.yml) conserva solo:

- `pve_uptime_seconds`: uptime real; `id=lxc/VMID` y `ct_id` por relabeling.
- `pve_guest_info`: nombre, nodo y tipo LXC.
- `pve_up`: estado running=1 / detenido=0.

Son tres familias complementarias; no se inventa una métrica de arranque ni un
estado textual en la serie de uptime. Se descubrieron **26 LXC de la API**; los
**17 monitorizados en Fleet** muestran uptime, mediante join con el inventario
Node dinámico ya existente. Otros LXC no se presentan como monitorizados por tener
solo datos PVE. Un futuro LXC aparece en la fuente automáticamente; al incorporarlo
al alta IaC de monitorización existente obtiene uptime sin editar el dashboard.

La [consulta](uptime.promql) exige estado running, scrape UP, muestra <=45 segundos,
valor no negativo/finito y unicidad de CT ID. El generador la une al inventario
filtrado y mantiene `UNKNOWN` para ausencia, detención, antigüedad o duplicados.
Formato Grafana `dtdhms`, por ejemplo `50 d 19:57:06`. Las demás columnas y estados
no dependen de este uptime. Un reinicio Docker/exporter no altera la fuente PVE;
un reinicio LXC resetea el uptime en la siguiente lectura (scrape 30 segundos).

## Identidad, secretos y TLS

Usuario `prometheus-uptime@pve`, token `uptime`, separación de privilegios activada.
Usuario y token tienen exclusivamente `PVEAuditor` propagado en `/`. Permisos
actuales comprobados: Datastore.Audit, Mapping.Audit, Pool.Audit, SDN.Audit,
Sys.Audit y VM.Audit. No roles de escritura, energía o administración. No se usa
el token Terraform. Verificación por lectura de ACL/derechos, sin ensayar escrituras.

El token se captura sin imprimir el resultado de creación. Archivo privado en
PVE y copia privada fuera de Git; en CT610 está en
`/opt/infra-pve-uptime/.runtime/pve_token`, modo0400, propietario65534. Se monta como
secretfile, nunca como valor en Compose, argumentos, logs o repositorio.
La CA pública se obtiene por SSH con known_hosts del propietario y checking=yes;
se monta de lectura y se indica con `REQUESTS_CA_BUNDLE`. `PVE_VERIFY_SSL=true`.
No se modifica la CA de Proxmox ni se desactiva verificación de certificado/hostname.

## Runtime reproducible y seguridad

[Dockerfile](Dockerfile), base Python3.12 fijada por digest, y
[dependencias exactas](requirements.lock). El paquete no se ha modificado: no hay
exporter propio ni adaptadores TLS a medida. La imagen local resultante es
`mailerblend/pve-uptime:3.11.0-py312-d056`; su image ID se registra en evidencia.

La imagen upstream inicial usaba Python3.14 y rechazó la CA PVE porque esta carece
de extensión keyUsage. La comprobación con Python3.12, soportado por el paquete,
validó la CA y la API sin tocar flags de verificación ni permisos. El primer
exporter, todavía sin integrar, se detuvo y conservó como
`pve-uptime-exporter-d056-py314-rejected`; su imagen también se conserva. Solo se
sustituyó ese servicio nuevo. Ningún contenedor previo o aplicación se reinició.
La validación inicial también eliminó una dependencia de parser local innecesaria.

[Compose](compose/docker-compose.yml): usuario65534, rootfs de lectura, ALL
capabilities eliminadas, no-new-privileges, sin puertos publicados, Docker socket
ni mounts del sistema. Red existente `infra-prom_default`, alias
`pve-uptime-exporter`. No se cambian límites o recursos de los LXC existentes.
La configuración/CA del runtime se lee exclusivamente desde los mounts previstos.

## Operación y reconciliación

[Transacción](../../scripts/deploy-pve-uptime.py):

```sh
python3 scripts/deploy-pve-uptime.py baseline  # solo primera vez; no sobrescribir
python3 scripts/deploy-pve-uptime.py identity
python3 scripts/deploy-pve-uptime.py exporter
python3 scripts/deploy-pve-uptime.py preflight
python3 scripts/generate-fleet-dashboard.py
python3 scripts/deploy-pve-uptime.py prepare
python3 scripts/deploy-pve-uptime.py apply
python3 scripts/verify-pve-uptime.py
```

Comprobar primero CURRENT-STATUS y el alcance autorizado. Para repetir sin cambios:

```sh
python3 scripts/deploy-pve-uptime.py identity
python3 scripts/deploy-pve-uptime.py exporter
python3 scripts/deploy-pve-uptime.py apply
```

No se regenera el token ni se añade ACL, no se descarga/reconstruye/recrea el
exporter, no se reescribe Prometheus/Grafana ni se recarga cuando ya coincide.
Las identidades, archivos y derechos se verifican antes de aceptar idempotencia.
Si existe un usuario no creado por la transacción o aparece drift, detener sin
sobrescribirlo. Rotación de credenciales/CA o cambios de dependencias requieren
una transacción revisada; no forzar la reconciliación con backups antiguos.

No ejecutar deploy-all ni compose up global. La transacción arranca solo el nuevo
servicio, valida API con el token/TLS, añade únicamente su job al config activo,
ejecuta promtool y recarga Prometheus por SIGHUP. Grafana toma el JSON por polling.
No reinicia Prometheus, Grafana, Blackbox, LXC ni aplicaciones.

Backups privados de config de CT610/611 y fuera de PVE, SHA256 y extracción/hash de
restore-check en `~/.local/share/mailerblend-recovery/phase6/d056/` y
`/opt/infra-{prom,grafana}/.runtime/d056/`. Backup de autenticación previo en PVE
`/var/lib/mailerblend-recovery/d056/`, restrictivo; no restaurar globalmente sobre
cambios ajenos. No borrar originales, secretos ni evidencia.

Fallo de aplicación restaura los dos archivos anteriores y recarga Prometheus;
el exporter y la identidad dedicados se retienen para diagnóstico, sin tocar
aplicaciones/DB/volúmenes. Una retirada posterior debe eliminar solo el job/JSON
propios y el servicio/identidad nuevos, con verificación de ownership y aprobación.

## Evidencia y límites

[Informe de ejecución](../../docs/roadmap/PHASE6-D056-UPTIME-EXECUTION.md),
[comparación](../../docs/roadmap/evidence/2026-11-07-d056-comparison.json),
[permisos](../../docs/roadmap/evidence/2026-11-07-d056-permissions.json).

Se comparan 17 CT con PVE y tres además con status/current independiente. No se
reinició un LXC para probar detección; el reset se prueba sintéticamente y la
métrica procede directamente del contador de PVE. Una caída del único exporter
produce UNKNOWN, no uptime físico ni cero inventado. El exporter no necesita
privilegios adicionales a los aprobados. El resto de Fase6 y los cuatro UNKNOWN
heredados de Application Health siguen fuera del cierre de uptime.
