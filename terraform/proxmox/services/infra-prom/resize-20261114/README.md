# Ampliación del disco de CT610

14/11/2026, Europe/Madrid. Fase 7. IaC Reliability, Security & Disaster Recovery.
Autorización expresa: aumentar15GiB el disco real10GiB de infra-prom. El YAML ya
establece25GiB; no elevar a40GiB. Terraform ignora `disk` en lifecycle para evitar
encogimientos: reconciliar con esta receta acotada, sin apply general.

Desde la raíz del repositorio:

```bash
python3 services/infra-prom/resize-20261114/reconcile.py --label preflight
python3 services/infra-prom/resize-20261114/monitor.py before
python3 services/infra-prom/resize-20261114/reconcile.py --execute --label applied
python3 services/infra-prom/resize-20261114/reconcile.py --execute --label idempotent
python3 services/infra-prom/resize-20261114/monitor.py after
```

La receta lee el YAML; solo acepta610/infra-prom/local-lvm:vm-610-disk-0/ext4,
10→25GiB o25→25GiB. Verifica SSH estricto, CT activo, ausencia de tareasPVE,
salud y margen thinpool y HDD, igualdad LV/FS, readiness Prometheus/Alertmanager,
PID e identidades/inicios/restarts Docker y configuraciones de otrosCT.
El preflight es solo lectura. Aplicar requiere `--execute`.

Antes del crecimiento: config privada y backup completo vzdump snapshot/zstd en
HDD sin reinicio, SHA256, lectura completa zstd/tar y extracción de configuración.
No equivale a restauración funcional ni garantiza consistencia transaccional del
TSDB activo. Evidencia pública filtrada; archivos/logs privados permanecen enPVE.
Después: `pct resize610 rootfs25G` (argumentos separados en script), verificación
LV/FS25GiB, espacio libre>15%, servicios/otrasconfiguraciones intactos.
Una segunda aplicación a25GiB no crea backup ni ejecuta resize.

No encoger como rollback: ante error detener, conservar LV/FS/datos y respaldos.
Si fuera necesaria recuperación de datos, restaurar backup en CT aislado con nueva
autorización; no sobrescribir el CT activo ni activar un clon en su misma red.
No borrar backups, reiniciar CT/apps ni alterar retención/reglas/silences.
`monitor.py` captura espacio/targets y alertas filtradas tras el siguiente scrape y
evaluación; recepción humana Telegram requiere confirmación del propietario.
