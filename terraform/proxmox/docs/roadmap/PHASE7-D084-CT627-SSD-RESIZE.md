# Fase 7.4 — D084: ampliación SSD de CT627

**DONE técnico**, 12 de noviembre de 2026, Europe/Madrid. D081 sigue
**ACCEPTED / PRODUCTION**. Rootfs ampliado50→100GiB en local-lvm/SSD, en caliente,
sin reiniciar CT627 ni Voicebox. No se ejecutaron inferencias. Se cierra esta
intervención; inglés y Chatterbox requieren una intervención separada.

## Preflight y capacidad inicial

Autorización explícita del propietario para CT627 exclusivamente. Comparación con
D083 sin cambio sustancial de capacidad. SSD `/dev/sda` Crucial_CT525MX300SSD1,
489,05GiB; PV `/dev/sda3`, VGpve488,05GiB y0extents libres. El crecimiento es thin:
no necesita extenderVG ni particionar. Autoextendthreshold100 permanece desactivado.

| Métrica | Inicial | Última lectura final |
| --- | ---: | ---: |
| Thin pool pve/data |400,086GiB|400,086GiB|
| Datos físicos usados |275.054GiB|275.481GiB|
| Datos físicos libres |125.032GiB|124.605GiB|
| Fracción libre |31.25%|31.14%|
| Metadatos ocupados |≈2,79%|2.797%|
| Reserva mínima operativa |80,017GiB;20%|Respetada|
| Capacidad virtual total |808GiB|858GiB|

Lectura final: **2026-11-12T15:14:22.452653+00:00**, UTC (16:14:22 Europe/Madrid). Estado rw, sin
healthflags; metadatos3,98GiB de capacidad. Los bloques asignados varían con la
inicialización de metadatos ext4 y escrituras normales; las cifras son mediciones,
no capacidad física reservada. Margen sobre reserva20% en esa lectura:
**44.59GiB**, compartido con otrosLXC/snapshots.
No autoriza llenar libremente todos los100GiB. Persiste sobreasignación thin≈2,145×.

Rootfs inicial exacto `local-lvm:vm-627-disk-0,size=50G`. Sin locks ni tareas
PVE activas incompatibles, sin workers ni jobs queued/running ni generaciones
activas enSQLite. Voiceboxhealthy y agenteQwenactivo. Los27 hashes deconfiguración
PVE coincidían con D083:18LXC de servicios más plantillas/otrosCT. No se modificaron
los otros17 de servicios. OOM/oom_kill0, sin nuevos errores kernel de memoria/I/O/ext4.

HostMemAvailable inicial20,70GiB sobre31,23GiB físicos. PSIhost ya elevado antes
(some14,25/full10,75 avg10) y osciló durante la intervención; última lectura
some20,05/full16,25 avg10. No se atribuye todo al mantenimiento ni se declara
resuelta esa presión previa. Sin OOM nuevo. Backup/validación comparten I/O físico,
con I/O delbackup limitado50MiB/s; no se promete latencia cero para otros usuarios.
La latencia cAdvisor618/623 yCRMparado de D083monitorización son incidencias
heredadas, no reparadas ni declaradas aceptadas enesta intervención.

## Backup completo verificado en HDD

BackupsD082 externos revalidados antes delresize:

- `accepted-final.tar.gz`: SHA256
  `3b1bd7eda2ca6368dbb1f46968fedf2a270c261b7a26b5412e1d55b3ad9a170a`,
  sus117 archivos coinciden con elmanifiesto.
- Imagen productiva externa D081:1279369082bytes,39blobsOCI íntegros, SHA256
  `b6fe07c13bcbc9091cbcc7626f38dbb9db8a73dfbd4402981ee7d15d1a259b43`.
  No se cargó ni reconstruyó laimagen.

Backup **completo delCT** nuevo:

`/mnt/storage/dump/vzdump-lxc-627-2026_11_12-15_49_14.tar.zst`

- Almacenamiento `storage`, XFS `/mnt/storage` sobre HDD `/dev/sdb`; no SSD.
- Tamaño **18952506863bytes = 17.651GiB**.
- SHA256 `3fa4107c8566fa9b0c4cd22b21a7423cc16901245ae613bf52f983bcd790afcb`.
- Permisos0600; temporales/extracción privados0700 en `/mnt/storage/d084-627`.
- Comando ejecutado por [backup.sh](../../services/infra-voicebox/resize-d084/backup.sh):
  `vzdump627`, modosnapshot, zstd1hilo, bwlimit51200KiB/s, stdexcludes0,
  remove0/keep-all; sin notificaciones, pruning ni parada. Duración9min34s.
- Snapshot temporalvzdump creado y retirado por Proxmox; lista final solo current.
- Copia adicional HDD delcontrolador `/opt/voicebox-qwen-627`, unidadsystemd y
  config627. Configdesbloqueada50G conservada aparte; no restaurar unlock transitorio.

[verify-backup.py](../../services/infra-voicebox/resize-d084/verify-backup.py) leyó
elarchivo completo, calculóSHA, verificó descompresión/checksumzstd yextrajo todo
elrootfs con GNUtar, propietarios/ACL/xattrs, a un **directorio aislado delHDD**.
Validación terminada15:11:45UTC, antes de resize:

- 111archivos protegidos coincidentes; propietarios/grupos/modos comparados aparte,
  también111/111. Directoriosjobs/originales0700 conservados.
- SQLiteintegrity_checkok, perfilEduardoUUIDoriginal,1referencia y6WAV completos.
- Checkpoints/modelos/referencias/originales/configuración incluidos; ambos pesos
  Qwen yconfig coinciden conlos originales porSHA256.
- `etc/vzdump/pct.conf` incluido para restauraciónPVE; datos/aplicación/modelos y
  capas Docker/containerd dentro delrootfs quedan enelbackup completo.
- Ningún CT de prueba creado o arrancado y ninguna restauración sobre producción.

La extracción demuestra integridad/legibilidad/recuperación de archivos, **no una
prueba DR de arranque**. Se conservan archivo, extracción, recibo ybackups previos.

## Ampliación ejecutada

Receta [resize-live.py](../../services/infra-voicebox/resize-d084/resize-live.py),
con recibo debackupPASS, revalida volumen/UUID, recursos, pool≥20%libre, metadatos,
sin locks/tareas/inferencias y Voiceboxhealthy/agenteactivo. Ejecutó una vez:

```sh
pct resize 627 rootfs 100G
```

Tamaño absoluto, no incremento relativo. Proxmox aumentó elmismo thinLV y ejecutó
resize2fs online. Salida:26214400bloques4KiB. No hubo estadoLV100/FS50 pendiente.
Advertencias de sobreasignación/autoextensión eran conocidas; no se eliminaron ni
se interpretaron como reserva física. No fstrim/drop_caches ni borrados.

| Verificación | Resultado |
| --- | --- |
| Volumen |local-lvm:vm-627-disk-0; mismoID|
| LV |107374182400bytes;100GiB|
| Ext4 |26214400×4096=107374182400bytes;100GiB|
| UUID |2c2fab31-95db-4d90-aeaf-b58fd4947d0c; sin cambio|
| df tamaño útil |48,916→98,122GiB; menor que tamaño bruto por metadatos|
| df disponible |19655892992→70323396608bytes;18,306→65,494GiB|
| df ocupación |61%→31%|
| CT |running, mismoPID31843|
| Recursos restantes |3vCPU/15360MiBRAM/2048MiBswap; sin cambios|
| Segundo pase receta |PASS;changedfalse; ninguna nueva ampliación|

Dockerdata-root `/var/lib/docker`, image-store `/var/lib/containerd`, HF/modelos,
jobs yWAV conservan susrutas. Se amplía elespacio que comparten; no se creómp0,
se movió Docker/modelos alHDD ni se descargó Chatterbox.

## Terraform e IaC

Cambios mínimos:

- `inventory/services/infra-voicebox.yml`:disk_gb100 únicamente627.
- `main.tf`: precondición627 permite50/100 manteniendoCPU3 yRAMmáxima15360;
  `ignore_changes=[clone,disk]` conservado. Ninguna protección global retirada.
- `services/infra-voicebox/NOTES.md` ygenerados: estadoactual100GiB; antecedentes
  D080/D081 conservados. Notes actualizadas conpctsetdescription, sin reboot.
- [RunbookD084](../../services/infra-voicebox/resize-d084/README.md) yverificadores
  versionables preparados; documentación central/fase/inventario actualizada.

Plan previo offline dirigido: únicaupdatedescription627; sin create/delete,
recreación ni cambio de CPU/RAM/swap. Tras comprobarLV+FS yactualizarNotes:
plan **refresh-only dirigido exclusivamente627** guardado yrevisado, deriva
solo `description` y `disk`; ninguna mutación remota enelplan dereconciliación.
Se aplicó eseplan deestado, no unapply general. Serial278→279; losestados de todos
los recursos ajenos son idénticos a lacopia previa privada. No se editó tfstate.
Plan normal final dirigido627: **NO CHANGES / exit0**. Esto se acompaña de pruebas
LV/FS reales: elignore de disk por sísolo no demuestra unresize.
Planes,estado,variables ycapturas completas permanecen privados fueraGit.

## Validación final ypreservaciónD081

- Voiceboxhealthy, mismaimagenAPP09774c5b…/mismoID/inicio/restartcount; worker
  bcc5c14f… retenido; agenteactivo yheartbeat vigente. No builds/pulls/deploys.
- QwenBase0.6B FP32/SDPA/español,semilla42,3hilos,A/B,guardas14GiB/workerhard9GiB,
  stop8,2GiB,decoder300/context25 y900s intactos por hashes decontrolador/worker.
- 111archivos protegidos idénticos. Tablas perfiles/referencias/generaciones
  conservan huellas lógicas:1perfil,1referencia,6registros dehistorial.
- CheckpointsD080/D081EOS/manifest/COMMITTED/codes íntegros. No cambios en grabaciones.
- HTTP200 health, agente, nodeexporter,cAdvisor ydescarga delWAV D081 existente;
  mismoWAV2753324bytes ySHA2566da5f689…; no inferencia nueva.
- Otros17LXC de servicios sin cambios deconfiguración; comparación adicional de
  **26configuracionesCT ajenas** (incluidas plantillas) idénticas. En627 solo
  difierenrootfs ydescription. No reinicios/migraciones/recursos de otrosCT.
- OOM/oom_kill0, memory.eventsigual albaseline; high251 heredado sin incremento.
  Ningún error nuevo kernel de memoria/I/O/ext4. Pool saludable y>20%libre.
- CandidatoD08316archivos conhashes intactos; sin activar inglés niChatterbox.

Validación local: sintaxisPython yshell, terraformvalidate/fmt,16tests inventario
+16aprovisionamientoPASS, inventario generado fresco, enlaces ygitdiffcheck.
No commit, staging ni push; cambios previos ajenos conservados.

## Recuperación y riesgos pendientes

No existe shrink online seguro100→50GiB. No ejecutarlvreduce ni falsear size50 en
config/estado. Si fallase soloelFS, conservarLV ydiagnosticar suampliación antes
de cualquier paso dependiente. Si falla otrocomponente, mantener100 yrecuperar
únicamente configuración/código necesario desdeD081.

Restauración física a50 requiere autorización adicional, capacidad para unvolumen
aislado yventana de cambio. Comprobar SHA delarchivo, `pct restore ID_NUEVO ARCHIVO
--storage ...` enalmacenamiento compatible, revisar identidad/IP/MAC yaislarred
antes dearrancar. ValidarDB/archivos/modelos/servicios; recuperar controladorPVE
porseparado. No sobrescribir627 ni descartar100 hasta aceptación. Esearranque
no se ejecutó enD084. Backupcompleto50GiB previo ycopiasD082 siguenconservados.

VGfree0, autoextensión deshabilitada ysobreasignación permanecen. Elobjetivo20%
libre es uncriterio operativo documentado/validado porlareceta, no unanuevaalerta
Prometheus desplegada. Revalidarlo antes de descargas, snapshots oampliaciones.
El margen de disco permite estudiar Chatterbox, pero no valida CPU/RAM/calidad.

## Evidencias yestado final

[Capacidad ypreservación](evidence/2026-11-12-d084-capacity-final.json),
[backup verificado](evidence/2026-11-12-d084-backup-verified.json),
[refresh-only revisado](evidence/2026-11-12-d084-terraform-refresh.json),
[runtime](evidence/2026-11-12-d084-runtime.json),
[datos ysalud](evidence/2026-11-12-d084-health.json).

**D084 DONE técnico: CT627 productivo con100GiB, sin reinicios ni inferencias.**
Fase7.4 D081 conserva aceptación; estaoperación no acepta funciones nuevas ni
Chatterbox/inglés. Siguiente trabajo separado: retomar candidatobilingüe yestudio
Chatterbox; no se ejecuta al cerrarD084. Sin commit/push.
