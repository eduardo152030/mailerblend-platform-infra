# Fase 7.4 — D083: auditoría de ampliación SSD de CT627

**12 de noviembre de 2026, Europe/Madrid. Auditoría DONE; ampliación NO ejecutada.**
La prioridad vigente es rootfs50→100GiB en `local-lvm`, sin segundo disco HDD.
D081 continúa ACCEPTED / PRODUCTION. Candidato Qwen bilingüe y pruebas conservados;
Chatterbox permanece sin descargas, instalación, despliegue ni inferencias nuevas.

## Recomendación

**100GiB en el SSD es la opción preferible para el uso previsto**, mediante una
ampliación en caliente revisada, seguida de reconciliación Terraform. Mantiene
sistema operativo, Docker/containerd, modelos y rutas enel SSD; evita migrar datos.
Hay margen físico actual para el incremento previsto de Docker/Chatterbox.

La aprobación debe ser de una **ampliación lógica thin**, no de una reserva física
exclusiva de50GiB. No se puede garantizar que todos los LXC llenen sus discos
virtuales yretengan snapshots ilimitados: elpool ya está sobreaprovisionado.
La condición recomendada es conservar una reserva operativa global ycomprobarla
antes de cada descarga/cambio grande. No se modifica monitorización enesta auditoría.

## Capacidad física real

SSD: `/dev/sda`, Crucial_CT525MX300SSD1,525112713216bytes (**489,05GiB**).
PV `/dev/sda3`, VG `pve`:524036341760bytes (**488,05GiB**), **0 extents libres**.
ElSSD está particionado/asignado; elespacio libre útil está dentro delthinpool,
no como50GiB sinasignar fuera deél. No ampliar elVG niparticiones para esta operación.

| Medida | Valor real |
| --- | ---: |
| Pool `pve/data` |400,086GiB|
| Datos usados, dm-thin |275,051GiB;68,748%|
| Datos físicos libres |125,035GiB|
| Metadatos |3,980GiB totales;0,111GiB usados;2,794%|
| Estado pool |rw, sinhealthflags anómalos;monitorizado|
| Autoextensión |threshold100: desactivada; VGsinextents disponibles|
| Volúmenes thin contabilizados |27, incluyendo plantilla yvolúmenes adicionales|
| Suma de tamaños virtuales actual |808GiB;2,020veces elpool|
| Suma virtual tras50→100 en627 |858GiB;2,145veces elpool|
| ThinLV conorigin/snapshots adicionales observados |ninguno; `pct listsnapshot627` solo current|

Las cifras de datos vienen de bloques dm-thin, no de sumar los porcentajes de cada
LV. `pvesm status` redondea elpool a68,75%; los metadatos no se cuentan como espacio
libre para imágenes. ElVGsinextents no impide crecer unthinLV dentro de supool,
pero impide confiar en que elpool físico se extenderá automáticamente al agotarse.
La política actual incluye queue_if_no_space: agotar elpool puede afectar a todos
sus usuarios, no solo a627. [Referencia LVM thin](https://man7.org/linux/man-pages/man7/lvmthin.7.html).

## Margen para los otros LXC, snapshots ycrecimiento

Escenarios de capacidad, sin borrar ni ejecutar discard/trim:

| Escenario global | Pool libre aproximado |
| --- | ---: |
| Actual |125,04GiB|
| Crecimiento físico neto de10GiB |115,04GiB|
| Escribir50GiB físicos adicionales |75,04GiB|
| CT627 llega a100GiB físicamente asignados, sin nuevos snapshots |73,70GiB|
| Snapshot previo retenido yreescritura completa de100GiB de627 |25,04GiB antes de crecimiento ajeno|

ElLV actual de627 tiene97,33% de bloques asignados (**≈48,665GiB**) aunque ext4
solo usa28,09GiB. Limpiar archivos enelpasado no equivale a liberar bloques delpool.
No se ha ejecutado fstrim. Elescenario de llenar100GiB añade≈51,335GiB frente a esa
asignación actual; es una aproximación por elredondeo delporcentaje delLV.

Snapshots empiezan compartiendo datos, pero las escrituras posteriores consumen
bloques nuevos; no son unrollback de coste cero. No recomiendo retener unsnapshot
previo de627 mientras se llena/rewrite elvolumen ampliado. Preferir unbackup externo
verificado yretención explícita, sin borrar ningún snapshot existente enesta tarea.

Propuesta operativa, **no una regla ya desplegada**: conservar almenos20% delpool
(**80,02GiB**) libre antes de permitir grandes incrementos de datos; avisar al80%
ydetener nuevas descargas/crecimiento planificado al85% hasta revisar capacidad.
Actualmente hay **45,02GiB** de crecimiento físico global antes de consumir esa
reserva20%. Elpresupuesto estimado inicial Docker+Chatterbox,≈7–15GiB incluyendo
margen temporal, cabe dentro deella; otros LXC ysnapshots comparten ese presupuesto.
Asignar100GiB no autoriza consumir libremente toda sucapacidad sin vigilar elpool.

Si se exige garantía física para los858GiB lógicos simultáneos, **no existe**.
La recomendación favorable cubre eluso acotado previsto, no esa promesa imposible.

## Rootfs ydistribución de espacio

Actual: `local-lvm:vm-627-disk-0,size=50G`, dispositivoLVM sin particiones internas,
ext4 montadoRW,53687091200bytes. `df` observa:

- Tamaño utilizable delFS:52521566208bytes,48,916GiB.
- Usados:30164447232bytes,28,093GiB.
- Disponibles para usos normales:19655987200bytes,18,306GiB;61% según `df`.
- La diferencia incluye metadatos ybloques reservados ext4, no cachéRAM.

| Directorio/categoría | Ocupación física aproximada |
| --- | ---: |
| `/var/lib/containerd` |13,298GiB|
| └ snapshots overlayfs / blobs de contenido |11,206GiB /2,088GiB|
| `/var/lib/docker` |0,017GiB|
| `/opt/voicebox/backups` |7,132GiB|
| `/srv/voicebox/huggingface` |2,650GiB|
| `/srv/voicebox/pilot-d066` — modelo/piloto conservado |2,330GiB|
| `/srv/voicebox/openvoice` |0,322GiB|
| `/srv/voicebox/data` — modelosPiper,perfiles,BD,WAV,cachés |0,083GiB|
| `/srv/voicebox/qwen-worker/jobs` — checkpoints yWAV crudos |0,007GiB|
| `/srv/voicebox/private-originals` |0,005GiB|
| `/usr` |1,710GiB|
| `/tmp` |40KiB|

Filas anidadas no se suman otra vez. `docker system df` muestra tamaños lógicos y
capas compartidas: sus14,27GB deimágenes y6,713GB debuildcache no deben sumarse
como si fueran conjuntos físicos independientes. No hay volúmenes Docker con nombre;
elapp utiliza binds persistentes de data,HF yjobs. No se borra nada.

Dockerdata-root es `/var/lib/docker`, pero elimage-store containerd ocupa
`/var/lib/containerd`; mover solo data-root no movería las capas. La ampliación del
rootfs **sí da espacio a ambos**, sin reconfigurarlos. [Documentación Docker](https://docs.docker.com/engine/daemon/).

ChatterboxV3 requiere≈2,99GiB en archivos seleccionados, más imagenCPU/temporales.
A100GiB se esperan aproximadamente65GiB disponibles sin nuevas escrituras, cifra
que solo se confirmará tras crecer ext4 ymedir susreservas/metadatos. Quedaría margen
para esos archivos manteniendo elpreflight Qwen de más de10GiB libres, conlas rutas
actuales. No se cambia eseumbral. Resolver disco **no valida** RAM,CPU,dependencias
ni calidad deChatterbox: esa activación sigue pendiente.

## Ampliación en caliente: soporte verificado, no ejecutado

Kernel6.8.12-4-pve,PVE8.3; e2fsprogs1.47.0-2. Superbloque ext4 limpio,features
resize_inode,64bit,extent,metadata_csum; ningún error deI/O/ext4 relevante observado.
13107200bloques de4096bytes actuales. No se ejecutó e2fsck sobre elFS montado.

La API instalada `/PVE/API2/LXC.pm`, método resize_vm, contemplaCT running:
aumenta elvolumen, actualiza configuración yejecuta resize2fs en unnamespace temporal.
No llama areboot enesa ruta. Ext4 soporta crecer montado. No equivale a haber probado
laoperación en627 ni garantiza latencia cero durante escritura de metadatos.
[Implementación PVE](https://github.com/proxmox/pve-container/blob/master/src/PVE/API2/LXC.pm),
[resize2fs](https://man7.org/linux/man-pages/man8/resize2fs.8.html).

Importante: laAPI puede advertir unfallo delcrecimientoFS después de haber ampliado
LV/config. Una salida delcomando sin error no sustituye comprobar elfilesystem real.

## IaC: comprobaciones yprocedimiento propuesto

No se ha cambiado main.tf ni elinventario activo. La política actual exige
`disk_gb == 50` eignore_changes incluye disk. Se hicieron planes **solo enuna copia
privada**, conestado copiado, refresh=false ysinapply:

1. Inventario100 conpolíticaactual: precondición rechazada.
2. Política privada que admite50/100, conservando ignore_changes: **cero cambios**,
   aunque eldisco real siga a50. No prueba que creció.
3. Quitando ignore solo enla copia: update627/disk, sin recreación. ElcódigoBPG0.94
   puede pedir elresize, pero no conviene retirar laprotección global de discos.

Elpatrón propuesto conserva esa protección yadapta elprocedimientoD080:

1. **Tras autorización nueva**, recapturar capacidad,health,locks,ausencia deTTS,
   tamaño/volid,appID/StartedAt,OOM yhashes deotrosCT. Detener si cambian cifras,
   hay presión,errores oelpool no conserva lareserva acordada. Sin inferencias.
2. Verificar backupD082 de datos/SQLite/imágenes ycrear unbackup completo previo
   delCT, verificable fuera delSSD, mediante elprocedimiento compatible. No escribir
   unbackup grande en `local`: elrootPVE está al89% ysolo dispone≈7GiB libres.
   ElstorageHDD existente puede guardar unarchivo debackup sin crear discosLXC ni
   mover modelos; requiere supropia autorización de ejecución. No crear snapshots
   persistentes sin presupuestar suCOW. Conservar todos losbackups anteriores.
3. Preparar cambios mínimos IaC: recursos.disk_gb100 únicamente enVoicebox;
   precondición para627 que admita solo50/100 yconserve RAM/CPU; actualizar Notes
   ygenerados coordinadamente. Mantener datastorelocal-lvm,clone/disk ignorados,
   todos losbinds,referencias,modelos yguardas. Revisar plan dirigido; ningún otroCT,
   delete/create oreinicio es admisible. No aplicar unplan general.
4. Receta versionada yacotada enPVE: sirootfs esexactamente elLV aprobado50GiB y
   ext4 está correcto, ejecutar **una vez**, solo tras aprobación:

   ```sh
   # PROPUESTO; NO EJECUTADO EN ESTA AUDITORÍA
   pct resize 627 rootfs 100G
   ```

   Usar tamaño absoluto100G, no +50G. Si ya mide100GiB, verificar LV+FS+config y
   no volver a ampliar; cualquier otro tamaño omontaje inesperado detiene lareceta.
5. Comprobar **LV107374182400bytes**, rootfsconfig100G, blockcount ext4 compatible
   con100GiB ydf/disponible aumentado. MismoUUID yvolid,CTsinreboot,appsinrecrear,
   mismoagente/imagen,permisos ydatos. SiLV100 peroFS50, detenerseguimiento: no bajar
   LV ni afirmaréxito. Diagnosticar/recompletar crecimientoFS solo bajo alcance seguro.
6. Generar plan refresh-only **dirigido627** yrevisar que no muta recursos remotos;
   aplicarlo solo para adoptar elestado observado. Después plan normal dirigido,
   cero cambios. Nunca editar eltfstate real para inventar100GiB. Segundo pase de
   lareceta debe ser no-op. Registrar capacidad ymetadatos delpool antes/después.
7. Validar Voiceboxhealth,agente,UID/permisos,perfil/originales/historial/checkpoints,
   descargaWAV yaexistente,exporters,noOOM yotros17config iguales. No generar audio.

Comandos de reconciliación propuestos, **solo después de autorizar yverificar el
crecimiento físico**; todas las rutas deplanes/variables deben ser privadas:

```sh
# PROPUESTO, NO EJECUTADO. Reutilizar el fichero bootstrap privado aprobado.
terraform plan -refresh-only \
  -target='proxmox_virtual_environment_container.svc["infra-voicebox"]' \
  -var-file=/ruta/privada/bootstrap.tfvars.json \
  -out=/ruta/privada/d083-refresh.tfplan
terraform show -json /ruta/privada/d083-refresh.tfplan > /ruta/privada/d083-refresh.json
# Revisar: ninguna mutación remota; únicamente adoptar lo ya observado en CT627.
terraform apply /ruta/privada/d083-refresh.tfplan
terraform plan -detailed-exitcode \
  -target='proxmox_virtual_environment_container.svc["infra-voicebox"]' \
  -var-file=/ruta/privada/bootstrap.tfvars.json
# Resultado exigido: exit0, sincambios. Exit2 oerror: detener yrevisar.
```

Elbackup completo previo se puede guardar enelstorage existente `storage` mediante
vzdump de627 enmodo snapshot, mientras elrootfs siga siendo soloLVM-thin50GiB.
Esto genera unarchivo debackup yunsnapshot temporal, no unsegundo discoHDD; también
requiere autorización yvigilancia deCOW/I/O. Verificar restauración fuera deproducción
antes deconsiderarlo recuperable; no prometer unretorno a50 sinventana ni espacio
adicional para larestauración. No se ha lanzado ese backup durante esta auditoría.

Ninguno deesos pasos de ampliación/reconciliación ha sido aplicado ahora. Las únicas
escrituras son fuentes/documentación/evidencias locales ycopias de planes privadas.
[Esquema yproveedor0.94](https://github.com/bpg/terraform-provider-proxmox/blob/v0.94.0/proxmoxtf/resource/container/container.go).

## Rollback realista

**No hay rollback simétrico en caliente de100 a50GiB.** Proxmox no admite shrink.
No ejecutar lvreduce ni cambiar solo size=50G enconfig/estado; se arriesgarían datos.
Si elcrecimiento funcionó pero otro componente falla, conservar100GiB yrecuperar
solo código/configuración aceptados sin reducir eldisco. Si se exige volver
físicamente a50, restaurar unbackup completo verificado a unvolumen aislado de50 y
hacer uncambio controlado con downtime autorizado; preservar el100 hasta validar.
Elbackup deaplicación D082 por sísolo no es unbackup completo delrootfs.

## Alternativas HDD conservadas, no preferidas ni ejecutadas

StorageID `storage`, directory `/mnt/storage`, XFS en HDD `/dev/sdb`,≈1,50TB totales,
≈1,46TB libres; rootdir ya habilitado. Es distinto delSSD. La investigación previa
queda conservada en evidencias y `mp0.proposed.hcl`, marcado SUPERSEDED.

Unmp0 de100GiB daría capacidad para modelos manteniendo elrootfs50, pero movería
suslecturas alHDD yno resolvería las capascontainerd enSSD. Directory/raw no ofrece
snapshots comoLVM-thin. Elproveedor planeó delete/create alañadir mount_point enuna
copia privada: **no aplicar eseplan**. PVE soporta hotplug deunmp nuevo bajo
condiciones, distinto deesa rutaTerraform. Copiar todoelrootfs alHDD exige pararCT,
no aumenta por sísolo sus50GiB ydegrada elmedio deDocker/BD. Por ello se descarta
como opción preferida con la nueva decisión delpropietario.

## Estado final y evidencias

Candidato bilingüe preservado porhash; pruebas previas10Python+4UI y22contratos
estables conservadas. No descargas/instalaciones, no inferencias, no discosHDD,
no movimiento,limpieza,trim,resize,reinicios,recursos,commit nipush.
D081 sigue aceptado, conrootfs50GiB. Verificación final deidentidad/configuración
se registra junto aesta auditoría. Implementación100GiB **PENDIENTE DE AUTORIZACIÓN**.
Fase7.4 productiva permanece DONE / ACCEPTED; estaampliación es solo propuesta.


Evidencias de auditoría:
[pool ysuperbloque](evidence/2026-11-12-d083-voicebox-ssd-pool.json),
[capacidad yescenarios](evidence/2026-11-12-d083-voicebox-ssd-capacity.json),
[simulaciónIaC](evidence/2026-11-12-d083-voicebox-ssd-iac-simulation.json),
[distribución de disco](evidence/2026-11-12-d083-voicebox-disk.json),
[storages](evidence/2026-11-12-d083-voicebox-storage-host.json),
[permisos ynamespaceDocker](evidence/2026-11-12-d083-voicebox-storage-permissions.json),
[política de backups observada](evidence/2026-11-12-d083-voicebox-storage-backups.json),
[comparaciónHDD histórica](evidence/2026-11-12-d083-voicebox-hdd-offline-history.json),
[estado final](evidence/2026-11-12-d083-voicebox-storage-final.json).

Las comparacionesprivadasHDD ySSD conservan toda lainvestigación sin reservar discos.
ElstorageHDD carece de unjobvzdump programado observado ydeguardis_mountpoint en
sudeclaración; no se activan backups/configuración global desdeesta auditoría.
La simulaciónHDD mostró recreación; no confundirla conelupdate no destructivo del
resizeSSD simulado ni conunplan efectivamente aplicado.
