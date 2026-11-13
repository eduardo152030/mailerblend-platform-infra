# D084 — crecimiento online del rootfs CT627

Alcance autorizado: 50→100GiB absolutos en `local-lvm`, sin reiniciar ni crear
volúmenes adicionales. Conservar D081, todos los datos y protecciones Terraform.
[Informe](../../../docs/roadmap/PHASE7-D084-CT627-SSD-RESIZE.md).

1. Leer ROADMAP/CURRENT-STATUS/DECISIONS y volver a comprobar thin pool libre≥20%,
   metadatos saludables, CT627 running/50G, mismo volumen, ausencia de inferencias,
   locks/tareas de almacenamiento y OOM. Capturar `capture.py`, `inspect-ssd.py`
   de la auditoría D083 y `verify-production.py` mediante SSH estricto existente.
   Guardar resultados privados, no publicar configuración completa ni datos.
2. Verificar copia D082 externa mediante SHA y sus117 archivos. Ejecutar `backup.sh`
   solo una vez: vzdump snapshot, almacenamiento existente `storage` en `/dev/sdb`,
   zstd1hilo, I/O50MiB/s, temporales HDD, no pruning. Vigilar pool y salud durante
   el backup. El snapshot temporal desaparece al finalizar; nunca retenerlo para
   intentar deshacer un crecimiento ext4.
3. Copiar captura previa al directorio privado HDD, ejecutar `verify-backup.py`
   con ruta exacta de archivo final y captura. Comprueba checksum zstd, SHA256,
   extracción completa al HDD,111 archivos protegidos, SQLite/perfil/WAV/modelos y
   permisos. No crea ni arranca otro LXC. Conservar archivo y recibo `verified.json`.
   No afirmar que esta extracción es una prueba DR de arranque.
4. Respaldar también unidad y controlador Qwen del host y configuración627 en HDD.
   Actualizar inventario a100, precondición a50/100 y Notes generadas. Revisar plan
   exclusivamente627, sin delete/create ni cambios en CPU/RAM/swap/runtime.
5. Revalidar recursos/salud. Ejecutar `resize-live.py --execute --backup-receipt
   /mnt/storage/d084-627/verified.json` en PVE. Usa `pct resize 627 rootfs 100G`.
   Con100G es no-op verificado. Otro tamaño, estado o margen: abortar. El script
   no cambia Notes ni estado Terraform. No lanzar si falló la verificación previa.
6. Verificar LV y ext4 exactamente107374182400bytes, mismo UUID/volid/PID/servicio.
   Si solo creció LV, detenerse y diagnosticar: jamás shrink/lvreduce.
7. Aplicar solo Notes generadas mediante `pct set 627 --description` tras revisar
   su diferencia; operación en caliente, sin cambios de runtime. Reconciliar
   Terraform con plan refresh-only guardado y objetivo exclusivo627. Revisar JSON,
   aplicar ese plan de estado y exigir plan normal dirigido final sin cambios.
   No quitar `ignore_changes=[clone,disk]`, no apply general ni deploy-all.
8. Repetir verificadores: datos, modelos, perfil, grabaciones, checkpoints,
   historial/descarga de WAV existente, exporters, sin OOM, otros17 configs intactos.
   Segundo pase resize debe ser no-op. No ejecutar inferencias para validarlo.

## Recuperación

No hay reducción online segura100→50GiB. Ante fallo posterior conservar100G y
recuperar solo configuración/código necesario. El backup completo contiene
rootfs y `etc/vzdump/pct.conf`; el controlador Qwen PVE se guarda aparte. Para DR,
verificar SHA y restaurar mediante `pct restore ID_NUEVO ARCHIVO --storage ...`
en un entorno aislado con capacidad y autorización adicionales; revisar identidad,
red/MAC/IP antes de cualquier arranque. Nunca restaurar sobre627 en producción.
Validar DB/archivos/UUID/modelos/servicios antes del cambio autorizado. No reclamar
que el procedimiento se ensayó como arranque de otro CT durante D084.

Todos los scripts de captura/verificación son de lectura productiva; backup y
extracción escriben solo nuevos archivos HDD. `resize-live.py` es el único resize.
Backups privados, planes/tfstate/tfvars y grabaciones nunca deben incorporarse aGit.
