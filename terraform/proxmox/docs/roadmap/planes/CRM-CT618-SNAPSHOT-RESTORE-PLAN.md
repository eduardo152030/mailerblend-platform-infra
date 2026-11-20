# CT618 — respaldo en caliente y restauración aislada

[Issue #23](https://github.com/eduardo152030/mailerblend-platform-infra/issues/23).
Fase 7, IN PROGRESS. 20/11/2026 Europe/Madrid.
Rama `ops/crm-618-snapshot-rehearsal`, worktree hermano
`mailerblend-platform-infra-crm-618-snapshot`, inicio `c5ca57c4`.

El propietario autoriza una copia actual por snapshot sin detener servicios,
y una restauración desechable con login sintético. Se elige `storage`
(`/mnt/storage`) por el [runbook](../../../services/infra-composable-crm/recovery/RECOVERY.md)
y capacidad observada. No se autoriza rotar CT618 en esta fase. #24 queda
pendiente de hostname, DNS y certificado concretos.

Preflight de solo lectura: Proxmox 8.3, CT618 running, un rootfs thin de 50 GiB,
soporte snapshot confirmado en API, sin mountpoints adicionales ni snapshots
preexistentes. Almacenamiento disponible superior a 1 TiB; 9618 libre. Una
copia histórica del 02/11 sigue retenida. El snapshot es consistente a nivel
de disco; la consistencia funcional se verifica mediante un arranque aislado.

El [script](../../../scripts/backup-crm-618-snapshot.sh) limita ancho de banda
e I/O, no poda archivos y verifica identidad e inicio de los cinco servicios.
Validar además log de modo snapshot, checksum y lectura del archivo antes
de restaurar. Restauración propuesta en 9618 sin arranque automático, NIC
desconectada y sin salida, con IP de producción únicamente en loopback del
clon, siguiendo el [aislamiento existente](../../../services/infra-composable-crm/recovery/isolation/README.md).
Probar CouchDB, Budibase D051 y login con cuenta sintética sin exportar
credenciales ni registros. Preparar runbook final y detenerse antes de rotar.

## Evidencia del respaldo actual

- Backup `storage:backup/vzdump-lxc-618-2026_11_20-08_23_42.tar.zst`,
  4.580.840.105 bytes, 08:23:42–08:33:39 CET. El log confirma modo snapshot
  y limpieza del snapshot temporal. Estado running y los cinco IDs e inicios
  de Docker iguales antes y después. Budibase y CRMAPI respondieron 200.
- SHA256 `00ee6dede0762aabba15676411f64971c5396540de617f8b688a3a0cf0fba30b`,
  checksum comprobado y `zstd -t` PASS. Archivo y checksum 0600. El
  archivo se conserva en un disco distinto del rootfs del CT, en el mismo
  host PVE. Copia fuera del host sin comprobar.
- Restauración al volumen nuevo en CT9618, extracción y confinamiento
  `onboot=0`, NIC desconectada, cero rutas por defecto IPv4/IPv6 y bind
  en loopback del clon. La primera comprobación funcional salió antes
  de acreditar CouchDB. Se apagó el clon y se reanudó sobre el mismo
  volumen con espera de readiness y señalización de la etapa.
