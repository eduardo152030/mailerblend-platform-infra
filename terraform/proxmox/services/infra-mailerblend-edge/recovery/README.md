# Recuperación sGTM CT615

Recuperado el 06/11/2026 mediante D048, con una recreación Preview y una Serving.
Procedimiento, backups, evidencias y límites:
[CT615-SGTM-D048-RECOVERY](../../../docs/roadmap/CT615-SGTM-D048-RECOVERY.md).

La base de referencia es `/opt/infra-mailerblend-edge/docker-compose.yml` ACTIVA,
con `/opt/infra-mailerblend-edge/healthcheck.native.yml`. No sobrescribirla con una
base histórica. La receta Node se reutiliza desde la implementación D044 y el
recuperador común selecciona explícitamente `--ct 615`.

No repetir recreaciones por consultar este documento. No instalar reinicios
periódicos sin revisión y autorización. Conservar backups privados y no publicar
entornos, configuración GTM ni logs sensibles.
