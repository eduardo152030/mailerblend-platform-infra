# Fase7.4 — despliegue de entrada1200 en Chatterbox

Desplegado en CT627 desde código3987cab. UI compilada con fork/Bun fijados D085,
API en imagen nueva218dc413… sobre base21270364…, políticas coherentes de
controlador/worker. La imagen anterior y sus digests no se reemplazan ni borran.
Límites de salida400tokens/EOS/20sWAV/300s, stop7/hard8/CT19GiB sin cambios.
No inferencias ni suite ejecutadas; el propietario probará las narraciones largas.

Receta reproducible, no reejecutar contra nombres existentes sin revisar estado:

1. `candidate-d085/build_ui.py` usa archivo y Bun verificados/frozen-lockfile.
2. `prepare.py` produce contexto sin datos privados y manifiesto de hashes.
3. `backup.py --attempt input1200` dentro CT, sin trabajos activos; snapshotSQLite
   consistente, perfiles/referencias/historial/WAV/jobs/configuración preservados.
4. `verify-backup.py` en PVE copia/restaura y verifica180archivos en HDD/storage;
   no restaura bases antiguas sobre producción. `build.py` verifica base/receta y
   crea tag independiente sin red/pull, conservando USER999/entrypoint/CMD/env.
5. `transaction.py --action deploy` en PVE toma el mismo lock de inferencias,
   exige cola vacía, recursos20GiB/3CPU/2GiBswap/100GiB y pool>20%libre; conserva
   operaciones/controlador/receipt y source link, compara Compose completo salvo
   image/build, actualiza solo app/política/locks. Reinicia agente y recrea solo
   Voicebox. No reinicia CT ni modifica otros servicios.
6. Verifica health, capabilities, UI servida por hash y constante efectiva, UID999,
   guardas, fuenteQwen, efectos, historial/WAV previos, configsPVE/PID y OOM.
   Repetir deploy después de PASS realiza solo verificación sin escrituras/reinicios.
7. `verify-data.py --baseline /opt/voicebox/backups/input1200-before-deploy` dentro CT
   compara filas y audios originales. Nunca ejecutar una generación como validación.

Primer intento completó arranque pero activó rollback por un falso criterio del
observador: texto de descripción no referenciado eliminado en build. Se conservan
control-backup/transaction.py originales en HDD. La receta corregida r2 verifica
la función retenida y constante1200 del JavaScript servido; no cambia el audio ni
la imagen218dc413. Segundo intento PASS, idempotencia sin recargas PASS.

`--action rollback` restaura image/config/controlador/receipt/source link; jamás
SQLite ni audios de un backup antiguo. No hacerlo con trabajo activo. Ante fallo
post-deploy se aplica automáticamente; evidencias/backups/nuevas imágenes se conservan.
Los nombres r2 reflejan el intento efectivo y evitan sobrescribir el primero.

HDD privado: `/mnt/storage/input1200-deploy`, CTcontexto y copia operativa en
`/srv/voicebox/input1200-deploy` y `/opt/voicebox/deploy-input1200-r2`.
Nada de esos datos/archivos de backup se añade a Git. Deployment-lock versiona
solo identidades/hashes públicos. No aplicar Terraform/ProxmoxNotes en este flujo.
