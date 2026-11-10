# Fase 6. Grafana & Dashboards — Uptime PVE D-056

**Uptime DONE técnico: 17/17 valores reales. Fase 6 IN PROGRESS.** D055 autorizado
expresamente por el propietario y ejecutado. No cierre automático del resto de F6
ni aceptación visual del propietario. Sin commit/push.

[Dashboard](http://192.168.1.111:3010/d/proxmox-lxc-fleet/proxmox-c2b7-lxc-fleet-overview?theme=dark) ·
[Operación, fuentes, secretos y recuperación](../../services/infra-pve-uptime/README.md).

## Implementación y resultado

Un único exporter central `prometheus-pve-exporter3.11.0` en CT610, no root, sin
capabilities ni puertos publicados, red Prometheus existente. Paquete sin modificar,
base Python3.12 fijada por digest y dependencias exactas enIaC. Fuente HTTPS PVE
`/cluster/resources`, collectors resources/status; no agentes en los17CT ni consultas
privilegiadas periódicas por SSH. Tres familias: `pve_uptime_seconds`,
`pve_guest_info` y `pve_up`; ct_id se deriva del id `lxc/VMID` mediante relabeling.
Nombre y estado proceden de info/up, no de una inferencia deDocker.

La API descubre **26 LXC**, sin lista manual. Grafana filtra y une porCT ID al
inventario dinámico de los17monitorizados, conservando todas las columnas y su UID.
La columna Uptime muestra duración, por ejemplo `50 d 19:57:06` o `5 d 06:05:49`.
Los4UNKNOWN heredados de **Application Health** son independientes y no se alteran.

Nueva fuente caída/antigua, CTdetenido, duplicados o dato nofinito producen UNKNOWN.
Scrape30s, frescura<=45s. Reinicio real delLXC resetea el contador dePVE; Docker y
exporters no intervienen en el cálculo. No se usa `node_boot_time_seconds`.

## Permisos y TLS

Usuario `prometheus-uptime@pve`, token `uptime`, `privsep=1`. Únicamente dos ACL
PVEAuditor propagadas en `/`: una alusuario y otra altoken. Derechos efectivos
iguales para ambos:

- Datastore.Audit
- Mapping.Audit
- Pool.Audit
- SDN.Audit
- Sys.Audit
- VM.Audit

Sin modificación/energía/administración. Comprobados los derechos y ACL mediante
lectura, sin intentar escrituras. No se reutiliza credencialTerraform.

Secreto capturado por el script sin imprimirlo, fueraGit. CT610: archivo0400 con
propietario65534, bindsecret de lectura; nunca valor env/CLI/JSON público. Copias
privadas restringidas enPVE y fueraPVE. CA obtenida porSSH estricto ya verificado,
`PVE_VERIFY_SSL=true`, cadena/certificado/hostname verificados. No se modificó la
CA deProxmox ni se desactivó la verificaciónTLS.

## Validación

| Control | Resultado |
|---|---|
|Identidad y permisos|PVEAuditor exclusivo, privsep1, seis privilegiosAudit efectivos; ACL previas conservadas|
|Backup/restauración|Config610/611 enCT/fueraPVE, SHA256 y extracción/hashrestore-check; copia privada authPVE previa|
|Exporter|API con token/TLS200, uptime/info/status reales, usuario65534/rootfsRO/cap_dropALL/no puerto publicado|
|Prometheus|Jobpve_uptimeUP; familias porCT,17Node/17cAdvisor/17Blackbox/probesuccess1 conservados|
|Comparación|17CT comparados conPVE;611/618/624además con status/current; diferencia máxima11s, límite45s|
|Descubrimiento|26LXC deAPI iguales al conjunto guest_info, sin duplicados ni configuración porCT|
|NuevoLXC/reinicio|Caso sintético9999 se une con generador sin editarJSON;530→5 trasreset de fuente; no crear/reiniciarLXC para probar|
|Consultas|28consultas reales;11queries tabla con17CT únicos, Uptimepositivo y sinNaN/Inf|
|Navegador|17duraciones, rango1h, filtrosCT/servicio, navegación y paneles PASS; sin erroresJS/consulta detectados|
|Conservación|Targets anteriores, identidades de contenedores previos y apps,7dashboards ajenos/datasources y reglasF5 intactos|
|Idempotencia|Usuario/token sin nuevaACL/token; exporter sinpull/build/up/recreación; configsinwrites/reloads; identidades iguales|
|Alertas|SinFIRING, reglas sanas; no nuevas reglas ni cambios de umbrales/Telegram|

Los9casos del contratoPVE incluyen fuente caída, detenido, ausencia/antigüedad,
duplicados, hostboot rechazado y nuevoCT. Los14casos de saludtipada y12de salud
previos pasan como regresión relevante del dashboard; no suites extensas F4/F5.
No se realizó reinicio productivo para ensayar detección; la fuentePVE y los casos
sintéticos constituyen la evidencia disponible, sin afirmar esa prueba real.

## Incidencia TLS resuelta sin ampliar permisos

La primera imagen upstream con Python3.14 rechazó la CA PVE por faltar extensión
keyUsage. La integraciónProm/Grafana quedó detenida antes de modificar esosarchivos.
Mismo paquete3.11.0 enPython3.12 soportado, base/dependenciasfijadas: validaciónCA/API
con token200 antes de arrancar el servicio compatible. No adaptadores TLS propios,
`verify=false`, flagsdesactivados ni cambios de CA/ACL para resolverlo.

Solo se sustituyó el **exporter nuevo no integrado**. El primero quedó detenido
como `pve-uptime-exporter-d056-py314-rejected`; su imagen se conserva. No se reinició
ningún LXC, aplicación o servicio que existiera antes de esta intervención.
La validación local inicial también se corrigió para no depender de un parser
Python no instalado. No hubo rollback productivo de Prometheus ni Grafana.

## Evidencias

- [Resultado y tiempo](evidence/2026-11-07-d056-result.json).
- [Permisos efectivos](evidence/2026-11-07-d056-permissions.json).
- [Exporter/familias/TLS](evidence/2026-11-07-d056-exporter.json).
- [Comparación y seguridad](evidence/2026-11-07-d056-comparison.json).
- [Despliegue/conservación](evidence/2026-11-07-d056-deployment.json).
- [Idempotencia](evidence/2026-11-07-d056-idempotence.json).
- [PromQL](evidence/2026-11-07-d056-promql.json).
- [Navegador](evidence/2026-11-07-d056-browser.json), [captura](evidence/2026-11-07-d056-fleet.png).
- [Transacción IaC](../../scripts/deploy-pve-uptime.py),
  [comparación repetible](../../scripts/verify-pve-uptime.py).

Seguimiento enEurope/Madrid; timestampsJSON conservados enUTC. Las diferencias y
valores son observaciones fechadas, no constantes del dashboard. El ciclo de alta
Node/inventario sigue siendo necesario para monitorización completa de futurosCT;
PVE descubre sus métricas sin necesidad de editarJSON o mantener listasVMID.

Siguiente paso: revisión visual del propietario. Fase6 sigue IN PROGRESS; no
continuar EtapaB ni modificar apps/recursos/F5. Mantener backups, imagen rechazada,
secretos privados y evidencia. RotaciónCA/token requiere transacción revisada.
