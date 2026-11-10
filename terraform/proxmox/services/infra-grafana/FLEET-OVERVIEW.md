# Grafana — Fleet Overview y LXC Details

Actualizado: **2026-11-10 (Europe/Madrid)**. **Fase 6 DONE**, cierre técnico conforme
a los once criterios autorizados D060. [Informe](../../docs/roadmap/PHASE6-D060-CLOSURE.md).

## Dashboards desplegados y navegación

- [Proxmox · LXC Fleet Overview](http://192.168.1.111:3010/d/proxmox-lxc-fleet/proxmox-lxc-fleet-overview?theme=dark).
- [Proxmox · LXC Details, CT 614](http://192.168.1.111:3010/d/proxmox-lxc-details/proxmox-lxc-details?var-lxc=614&theme=dark).

Fleet:17 CT, identidad, exporters, Infrastructure/Application/Monitoring/Overall,
estado PVE, uptime, CPU/RAM/disco y alertas. CTID abre Details y conserva rango.
Details: selector CT dinámico yservicio, IP, capacidad CPU/RAM/raíz, red/históricos,
Dockeraislado por LXC, sondas/latencia/disponibilidad, readiness, targets/frescura,
alertas y rutas verificadas de inventarios existentes. Enlace superior vuelve a
Fleet con CT/rango. Environment y panel Docker retirados de Fleet siguen ausentes.

Los siete dashboardsanteriores se conservan, incluidos tres antes manuales, ahora
exportados yprovisionados. Nueve modelosIaC, UIDs ycarpetas conservadas; no se afirma
una auditoría nueva de todas las consultas heredadas. Datasources existentes, incluido
BigQuery, intactos. Grafana12.3.1 y misma imagen, fijada pordigest.

## Rutas y provisioning

- [Generador Fleet](../../scripts/generate-fleet-dashboard.py),
  [generador Details](../../scripts/generate-lxc-details.py).
- [JSONFleet](config/provisioning/fleet-assets/proxmox-lxc-fleet.json),
  [JSONDetails](config/provisioning/fleet-assets/proxmox-lxc-details.json).
- [Provider Fleet/Details](config/provisioning/dashboards/fleet.yml):
  `proxmox-lxc-fleet`, carpeta Proxmox, polling30 s, sin edición UI.
- [Providerlegado](config/provisioning/dashboards/default.yml): único`default`,
  modelos en `config/provisioning/legacy-assets/`; subdirectorio Infra conserva esa
  carpeta, raíz General. [Providerduplicado](config/provisioning/dashboards/provider.yml)
  retirado con lista vacía. Los dos providers protegen contra eliminación.
- [Compose](compose/docker-compose.yml): tresmounts efectivos, sin duplicados,
  imagen instalada fijada. No cambiar credenciales al restaurar volumen existente.

Configuración del servidor: `/opt/infra-grafana/config`; provisioning en
`/etc/grafana/provisioning`; volumen `infra-grafana_grafana_data`. No editar JSON en
la UI. Modificar generador/fuentes yregenerar; no usar scripts antiguos deapply
contra baselines D052/D057, que ya no representan el estado actual.

## Variables, altas y consultas

Fleet: Service/LXC admiten All/multi. Details: CTIDsingle-select desde
`label_values(lxc:cpu_inventory:expected, ct_id)`; servicio derivado del CTseleccionado.
No listas estáticas17 CT. Inventario esperado conserva filas sin métricas.

Altasreales: inventario YAML/Terraform, exporters ycontratos validados,
`exporter-migration.yml`, targetsfile_sd generados enstaging ypublicación exclusiva
tras autorización. Ver [proceso F4](../../docs/roadmap/phases/04-exporters-coverage.md)
y [generador](../../scripts/gen-prom-targets.py). Una vez publicadas las etiquetas,
Grafana incorpora el CT sin ediciónmanual. El exporter PVE descubre CT para uptime,
pero no descubre/despliega automáticamente exporters ni aplicaciones.

| Señal | Fuente y semántica |
|---|---|
| CPU LXC / RAM / raíz | Contratocgroup F4, LXCFS y filesystem Node; no recursos del host |
| CPU/RAMasignadas | Capacidadcgroup yMemTotalLXCFS |
| Disco | Capacidad del filesystem raíz, no cuota Terraform/maxdisk PVE |
| IP | Etiqueta instance del target Node; sin inferir CT por IP |
| Estado / uptime | pve_up y pve_uptime_seconds; fuente UP, frescura≤45 s y unicidad |
| Application | Sondasfuncionales, readiness CRM, checks Odoo/PG; no UAT |
| Monitoring | Exporters/cobertura y edad de scrape/fuente CPU/cAdvisor/sonda/PVE |
| Docker | Solo cgroups frescos≤45 s, cAdvisorUP; identidad incluye servicio+instance+ID+nombre |
| Disponibilidad / latencia | Media observada deprobe_success yprobe_duration_seconds |
| Alertas | ALERTSreal; descripción decontrato IaC, evaluación/activeAt enlazados a Prometheus |

STOPPED procede exclusivamente de PVE. Sin datos=UNKNOWN, nunca éxito implícito.
613 sinappverificada y611/616 como infra:Application N/A, Monitoringreal. DEMOnoexime
ni declara mantenimiento. 621 ping JSONFocalboard;623 Odoo8069+PG;625 pg_isready;
618 readiness CRM. Las señales existentes no se cambiaron para cerrar F6.

Docker SINHEALTHCHECK no es HEALTHY; sin contador fiable no se muestran reinicios
inventados. ACTIVO significa cgroup observado fresco, no API Docker State exacta.
CPU Docker usa%deun core, CPU LXC%de su capacidad. No se mezclan IDs clonados de otros CT.
Las rutas `docs/inventory/<CTID>-LXC-INVENTORY.md` se muestran solo si existen en
el repositorio; no se generan URLsweb a páginas sin publicar. Ausencia deficha se
expresa como tal. Los detalles dinámicos de alertas se consultan en Prometheus.

## Operación y comprobación

```sh
python3 scripts/generate-lxc-details.py
python3 scripts/phase6-grafana-final.py verify
python3 scripts/validate-lxc-details.py
python3 scripts/validate-phase6-final-browser.py
```

Generador Details regenera también Fleet. Los validadores D060 escriben evidencias
conprefijo09 nov: para nueva intervención escoger otro prefijo/namespace antes de
usarlos, conservando los originales. Browserrequiere Playwright ycredenciallocal
ignorada en `config/.env` o `GRAFANA_CREDENTIAL_FILE`; no imprime valores.
SSHestricto: known_hosts delpropietario, checking=yes y Batch Mode. No deploy-all.

[Transacción D060](../../scripts/phase6-grafana-final.py):baseline/config/Compose/
SQLite respaldados yrestaurados enstaging, hashes e integrity_check. Candidato
validado, diffacotado, escritura solo archivos propios yrecargade provisioning. Elapply
sin cambios verifica yproduce0 escrituras/recargas/reinicios. No ejecutar nuevoapply
tras cambiar fuentes contra el baseline histórico; crear transacción/baseline frescos y
obtener alcance correspondiente. No sacar a Git los backups ni credenciales.

## Recuperación y persistencia

Conservar/restaurar volumen o snapshot SQLite verificado, configuración completa,
fuentesIaC ymisma imagen fijada. Rutas/mounts/UIDs estables. Dosdashboardsnuevos y
siete previos se provisionan desdearchivos; volumen conserva usuarios, credenciales,
datasources yotros datos Grafana. No arrancar con volumen vacío usando defaults heredados.

Backupprivado en `/opt/infra-grafana/.runtime/d060/` y
`~/.local/share/mailerblend-recovery/grafana/d060/`. Rollback D060 protege eliminación
antes de retirar asociaciones de provisioning yreponer archivos anteriores; conserva
modelosadoptados yno elimina automáticamente el UIDDetails. Verificar antes/después.
No restaurarSQLite completo sobre Grafana activo ni borrarvolumen/backups.

[Ensayo aislado](../../scripts/verify-grafana-recreation.py):candidato final exacto,
misma imagen, SQLiteconsistente, red none ysin puertos; nueve modelos/carpetas cargados,
contenedor de ensayo detenido yconservado. Producción no se recreó. Su conectividad
no se atribuye al ensayo aislado: datasource/consultas se comprobaron en producción.
[Pruebafinal](../../docs/roadmap/evidence/2026-11-10-d060-recreation-replay-final-20261110.json).

[Provisioning oficial Grafana](https://grafana.com/docs/grafana/latest/administration/provisioning/).
Pendientes F7/host/Grafanajob/aplicaciones en
[CURRENT-STATUS](../../docs/roadmap/CURRENT-STATUS.md), sin ejecutarlos por estecierre.

## Preparación D061 — sin despliegue nuevo

7.4 añade compatibilidad de cAdvisor opcional mediante la métrica declarada
`lxc:cadvisor:required=0`, y exclusión de falsa ausenciaDocker. Código/JSON fuente
preparados y versionados, no recargados en producción duranteD061. El despliegue
aceptadoD060 sigue en servicio. Primera integración nativa requiere alcance y
baseline/rollback coordinado, sin editarJSON por cadaCT. Ver
[runbook de altas](../../docs/runbooks/NEW-LXC-PROVISIONING.md).
