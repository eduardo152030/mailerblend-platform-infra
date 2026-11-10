# Uptime PVE centralizado — propuesta D-055, NO aplicada

Se reutiliza `prometheus-pve/prometheus-pve-exporter` 3.11.0, imagen oficial del
proyecto fijada por digest verificado en el registro. No desarrollar un exporter
propio. Un único contenedor nuevo en CT610, red Docker existente `infra-prom_default`,
sin puertos publicados, usuario no root, sin capacidades ni mounts del host/Docker.
No instalaciones en los17CT, reinicios, recursosPVE, reglasF5 o aplicaciones.

## Aprobación necesaria antes de aplicar

Actualmente no hay exporter PVE, métricas PVE, usuario ni token de lectura. El token
Terraform hereda PVEAdmin: **no se reutiliza**. Cambios de permisos propuestos:

1. Usuario `prometheus-uptime@pve`, sin contraseña interactiva ni privilegios previos.
2. Token `uptime` con separación de privilegios **activada**.
3. Rol incorporado **PVEAuditor** en `/`, propagado, para usuario y token. Es lectura
   de metadatos del clúster; no concede modificar configuración, recursos o energía.
   Incluye más lecturas que uptime; usar el rol estándar evita mantener uno propio.

Son permisos nuevos para una identidad dedicada y requieren aprobación expresa de
acuerdo con la petición. El secreto se captura a archivo privado sin imprimirlo,
se entrega a CT610 por SSH estricto, modo0400 con propietario65534, y se monta como
secretfile. Nunca `.env` en Git, logs, argumentosCLI o JSON público. Token ausente:
no desplegar. No copiar tokenTerraform ni dar SSHroot al contenedor.

## Fuente, TLS y descubrimiento

El collector `resources` usa `/cluster/resources`; `status` proporciona estado.
Se desactivan colectores de configuración, backups, suscripción y por nodo.
`pve_uptime_seconds{id="lxc/VMID"}` contiene segundos reales de uptime del CT;
`pve_guest_info` aporta nombre/nodo/tipo; `pve_up` aporta estado. El scrape añade
`ct_id` mediante relabeling y retiene solo estas tres familias deLXC. Son señales
complementarias, no una métrica inventada con un estado textual añadido.

API `https://192.168.1.100:8006`; certificado incluye esaIP. CA PVE se obtiene por
SSH ya verificado, se verifica contra certificado del servidor y se monta de solo
lectura con `REQUESTS_CA_BUNDLE`; TLS siempre activo. No `verify_ssl:false` ni `-k`.

API descubre todos losLXC visibles al rol, sin listaVMID. Grafana hace join por
ct_id con el inventario dinámico de Node ya usado en Fleet: los17monitorizados
siguen siendo17. NuevosCT con Node/inventario incorporado porIaC obtienen su uptime
sin tocarJSON. Un CT soloPVE sin exporters se descubre en esta fuente, pero no se
presenta como ya monitorizado en la tabla de salud de la flota.

## Integración propuesta

- [Compose](compose.yml), [job Prometheus](scrape.yml), [consulta base](grafana-query.promql) y [patch Grafana completo](grafana-uptime-patch.json).
- La consulta filtra no negativos/finitos, estado running, frescura<=45s y scrapeUP;
  rechaza duplicados. Se une al inventario de tabla y conserva fallbackUNKNOWN.
- Nombre y estado se consultan desde guest_info/up, no se infieren deDocker.
- Cambiar solo expresión de Uptime en generador/JSON; conservar unidad `dtdhms`,
  resto decolumnas, variables, estados deApplicationHealth y UID.
- Reinicio LXC: PVE resetea uptime y la siguiente lectura actualiza el valor. Un
  restartDocker/exporter no cambia la fuente. CTdetenido o fuente ausente/antigua:
  UNKNOWN en Uptime; estadoPVE se conserva por separado.

## Transacción pendiente de autorización

Antes de aplicar: backup privado/modelos/config de610/611, hashes, restore-check,
identidades y targets. Validar Compose, flags/binario, TLS desde610 y API usando
el token nuevo; probar que usuario/token tienen solo lectura. No intentar escrituras
para «probar» permisos: inspeccionar derechos efectivos. Descargar imagen fijada,
arrancar **solo el nuevo servicio** (sin compose global/pull/remove-orphans), comprobar
API/métricas y comparar conPVE al menos611/618/624, preferentemente17. Si falla,
no modificarProm/Grafana. Estado original conservado.

Después: añadir solo job propio a configactiva, promtool y recarga controlada,
verificar17uptimes, frescura, duplicados, estado y muestras tras reset sintético.
Actualizar JSON porpolling, comprobar navegador/filtros y segundaaplicación sin
escrituras/reloads/recreaciones. Sin reiniciar LXC/apps/exporters existentes.

Rollback: restaurar config/JSON propios y recargarProm; detener solo el nuevo
exporter si es necesario, conservando backups. Revocación del token/usuario queda
como operación explícita de reversión; no borrar otras identidades/roles ni datos.

Esta preparación **no prueba despliegue**, credencial API nueva, funcionamiento del
contenedor ni17uptimes enGrafana. La columna desplegada sigue UNKNOWN hasta aprobar
y ejecutar la transacción. La alternativa es conservar eseestado; otra alternativa
con SSHroot periódico no cumple mínimo privilegio y no se propone.

Referencia primaria:
https://github.com/prometheus-pve/prometheus-pve-exporter
