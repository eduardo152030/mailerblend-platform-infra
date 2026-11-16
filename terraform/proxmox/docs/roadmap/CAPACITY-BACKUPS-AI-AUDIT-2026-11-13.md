# Auditoría de cAdvisor, respaldos y hardware para IA local

> Vigencia: propuesta autorizada posteriormente por el propietario y ejecutada.
> [Resultado y evidencias](CAPACITY-APPROVED-EXECUTION-2026-11-13.md).
> Los estados pendientes de este documento describen el momento de la auditoría.


13 de noviembre de 2026, Europe/Madrid. Fase 4. Exporters & Monitoring Coverage y
Fase 7. IaC Reliability, Security & Disaster Recovery. Auditoría DONE; cambios
productivos y eliminación TODO, pendientes de autorización del alcance concreto.
No se reabre el rollout ni se altera Voicebox aceptado. Sin commit/push.

## Alcance y evidencia

Petición del propietario: investigar aplicación preventiva del cambio D088 al resto
de CT, revisar eliminación segura de 9618/9622 y obtener inventario técnico para IA.
Se ejecutaron lecturas SSH estrictas con known_hosts del propietario y BatchMode,
consultas Prometheus y scripts versionados, sin instalaciones ni cambios remotos.

- [Hardware, capacidad y clones](evidence/2026-11-13-capacity-host.json).
- cAdvisor [primera](evidence/2026-11-13-capacity-cadvisor-before.json) y
  [segunda lectura](evidence/2026-11-13-capacity-cadvisor-after.json).
- [Deltas durante 104,82 segundos](evidence/2026-11-13-capacity-cadvisor-delta.json).
- [Prometheus, últimos seis horas](evidence/2026-11-13-capacity-prometheus.json).

Los sellos originales de evidencia están en UTC. Inventario del host:
09:37 UTC / 10:37 CET. No son pruebas de carga ni observación larga de producción.

## cAdvisor: recomendación selectiva

18 exporters accesibles; 18 targets UP y ninguna alerta FIRING al consultar.
En las consultas de seis horas no aparecen evaluaciones up=0; no se convierte eso
en garantía de disponibilidad futura. No hay nuevos OOM ni reinicios entre lecturas.
Otros seis CT activos (101/103/104/105/107/109) no permiten inspeccionar un
contenedor llamado cadvisor con Docker/Python3 mediante esta receta; no afirmar
que estén cubiertos ni instalar nada automáticamente. 106/9618/9622 apagados.

| CT | Límite actual | Uso segunda lectura | Eventos max nuevos | Tiempo bloqueado PSI en intervalo | Propuesta, no aplicada |
|---|---:|---:|---:|---:|---|
|619 Pulpo|256 MiB|255,78 MiB|10.499|5,063%|Prioridad: probar 384 MiB|
|61211 svc01|128 MiB|127,80 MiB|4.556|1,977%|Prioridad: probar 384 MiB|
|620 Excraper|128 MiB|127,82 MiB|192|0,018%|Menor presión; probar 256 MiB antes de 384|
|614 Nucleoedge|128 MiB|124,45 MiB|0|0%|Conservar y vigilar|
|615 Mailerblend Edge|128 MiB|124,25 MiB|0|0%|Conservar y vigilar|
|622 EVA|128 MiB|124,05 MiB|0|0%|Conservar y vigilar|
|618 CRM|384 MiB|379,38 MiB|0|0%|Conservar corrección D088; vigilar slab|
|623 Gestoría|384 MiB|307,82 MiB|0|0%|Conservar corrección D088|
|627 Voicebox|Sin límite Docker explícito|278,73 MiB|0|0%|Estudiar límite propio con carga; no imponer 384 sin validar|
|610/611/613/616/617/621/624/625/626|128 MiB|38–81 MiB|0|0%|Conservar 128 MiB|

Uso cerca del techo no prueba falta de RAM si la caché es recuperable y no hay
presión. Los contadores max acumulados tampoco prueban fallo actual: por eso se
comparan deltas y PSI. El 0 de HostConfig.Memory en 627 significa sin límite
explícito del contenedor Docker, sujeto al cgroup del LXC; no significa consumo cero.

Propuesta de ejecución futura: 619→61211 y después 620, backup verificable de
configuración, ajuste coordinado de Compose y runtime sin recrear, CPU intacta,
observación de al menos 600s/21 por incidencia, métricas CPU/RAM/Docker/targets/apps,
PSI/OOM/restarts e idempotencia. Anomalía detiene la secuencia. No tocar reglas,
for, scrape_timeout ni ampliar RAM PVE para ocultar el límite de un exporter.
No se ha aplicado ningún cambio de límites en esta auditoría.

## Almacenamiento y eliminación segura

La raíz SSD está al 90%, con **7,01 GiB libres**. `local-lvm` es un thinpool separado:
400,09 GiB físicos, **123,79 GiB libres**, metadatos 2,80%. HDD `/mnt/storage`:
1396,55 GiB totales y **1311,08 GiB libres** (aprox. 1,28 TiB).
El espacio de raíz, thinpool y HDD no es intercambiable automáticamente.

9618 y 9622 son clones restaurados utilizados en los ensayos de recuperación de
Fase 3 ([tarea F3-02](phases/03-infrastructure-recovery.md)), no archivos de backup.
Ambos están apagados, onboot=0, sin IP de producción en el bridge y link_down=1,
sin snapshots adicionales. No hay jobs de backup de clúster configurados ni
reglas de replicación en la lectura. El storage HDD conserva keep-all=1.

| Candidato | Objeto real | Capacidad lógica | Bloques mapeados estimados | Efecto si se elimina |
|---|---|---:|---:|---|
|9618 crm-recovery-9618|local-lvm:vm-9618-disk-0|50 GiB|23,03 GiB|Libera thinpool, no raíz|
|9622 eva-recovery-9622|local-lvm:vm-9622-disk-0|40 GiB|31,86 GiB|Libera thinpool, no raíz|
|Backup VM100 de marzo2025|local:backup/vzdump-qemu-100-2025_03_23-23_03_29.vma.zst|34,60 GiB archivo|34,60 GiB aparentes|Trasladarlo/eliminar origen sí libera raíz|

Los clones suman 90 GiB virtuales y aproximadamente 54,88 GiB mapeados. No prometer
90 GiB físicos ni liberación exacta: se medirá el pool antes/después y cualquier
compartición de bloques. `qm list` no muestra máquinas virtuales actuales; eso
no demuestra que el backup100 carezca de valor ni autoriza destruir su única copia.
Además hay unos16 GiB de ISOs en `/var/lib/vz/template`; sin borrar imágenes.

Se localizaron los respaldos fuente de los clones en HDD:

- `/mnt/storage/mailerblend-recovery/20261102T100708Z/crm/vzdump-lxc-618-2026_11_02-11_09_28.tar.zst`, 4.342.436.833 bytes, con SHA256 y bundle en frío.
- `/mnt/storage/mailerblend-recovery/20261102T100708Z/eva/vzdump-lxc-622-2026_11_02-11_41_01.tar.zst`, 12.600.126.707 bytes, con SHA256 y copia cifrada `.gpg`.

Son respaldos de producción618/622 del2nov, usados para restaurar9618/9622; no son
backups actuales de esos clones ni protegen cambios posteriores. Los marcadores
históricos de restauración y F3-02 no sustituyen revalidación actual. En esta
auditoría se comprobó presencia/tamaño, no se recalcularon hashes de los archivos
grandes ni se repitió restauración. Se conservan todos esos archivos y evidencias,
además de backups Voicebox y rollback de exporters.

Plan concreto antes de eliminar clones:

1. Confirmar que solo se retiran 9618/9622 y que no tienen datos únicos a conservar.
2. Revalidar checksums/legibilidad de respaldos618/622, además de la copia externa
   que se vaya a conservar. Si no es recuperable, detener la eliminación.
3. Exportar configuraciones de los dos clones a un directorio privado en HDD,
   registrar inventario de volúmenes y estado de producción618/622.
4. Revalidar IDs/nombres/estado stopped y ausencia de mounts compartidos justo
   antes de ejecutar `pct destroy 9618` y después `pct destroy 9622`.
   No usar comodines, `lvremove`, force, ni opciones para discos ajenos.
5. Comprobar ausencia exclusiva de esos dos objetos, pool libre y aplicaciones
   originales618/622 intactas. Guardar evidencia; segunda revisión sin cambios.

La recuperación de un clon borrado requiere restaurarlo desde su respaldo y
reaplicar aislamiento; no hay undo instantáneo de destroy. Se entrega propuesta,
no se ha ejecutado. La aprobación histórica para recuperación no autoriza borrado.

Para liberar raíz, opción propuesta independiente: copiar el backup100 a un
nombre nuevo en HDD, comparar tamaño y SHA256, comprobar archivo comprimido y
legibilidad del backup; solo después de confirmación retirar el origen exacto.
Conservar una copia verificada evita perder una VM histórica. No se movió ni
eliminó este archivo. [Manifiesto](evidence/2026-11-13-capacity-cleanup-plan.json).

## Inventario técnico para IA local

| Componente | Lectura real |
|---|---|
|GPU|Una Intel HD Graphics530, PCI8086:1912, controlador i915. No GPU dedicada adicional detectada|
|VRAM dedicada|Sin banco dedicado: iGPU usa RAM compartida; no contabilizar RAM compartida como VRAM física|
|RAM|32 GiB instalados, 2×16 GiB SODIMM DDR4, velocidad configurada2133 MT/s; Linux utilizable31,23 GiB|
|CPU|Intel Core i5-6500@3,20GHz, 1socket, 4núcleos/4hilos, máximo3,60GHz, AVX2/FMA|
|SSD|Crucial_CT525MX300SSD1 SATA, 525GB nominales ≈489GiB; raíz y thinpool anteriores|
|HDD|WDC WD15JDRW-11C7VS1 USB, 1,5TB nominales ≈1,36TiB; espacio libre anterior|
|SO|Proxmox VE8.3.0, DebianGNU/Linux12 bookworm, kernel6.8.12-4-pve, x86_64|

Referencia primaria para memoria integrada: [Intel](https://www.intel.com/content/www/us/en/support/articles/000057824/graphics.html).
No confundir aperture/BAR PCI con VRAM. No hay NVIDIA detectada ni nvidia-smi
instalado; no se instala software ni se presupone aceleración GPU compatible.
MemAvailable ≈21GiB en lectura inicial, variable y compartida por servicios;
no es presupuesto exclusivo de IA. La RAM ya asignada a CT627 tampoco es reserva
física adicional. No se ejecutaron benchmarks ni inferencias; no se prometen
modelos/tokens por segundo ni se recomienda compra sin evaluar carga objetivo.

Comandos para repetir inventario en el host como root (solo lectura):

```bash
pveversion
cat /etc/os-release
uname -m
lscpu
free -h
sudo dmidecode -t 17
lspci -nnk | grep -A3 -Ei 'VGA|3D controller|Display controller'
lsblk -d -o NAME,MODEL,SIZE,ROTA,TRAN
df -hT / /mnt/storage
pvesm status
lvs -o lv_name,lv_size,pool_lv,data_percent,metadata_percent
# Solo si hay NVIDIA y está instalada la herramienta:
command -v nvidia-smi && nvidia-smi --query-gpu=name,memory.total --format=csv
```

`ROTA=0` identifica disco no rotacional reportado; `ROTA=1`, rotacional. En este
host los modelos corroboran SSD/HDD. dmidecode completo muestra seriales:
para compartir resultados usar la receta sanitizada en lugar del volcado bruto.

Scripts repetibles desde el repositorio:
[hardware](../../scripts/audit-capacity-20261113/host-readonly.py) y
[cAdvisor](../../scripts/audit-capacity-20261113/cadvisor-readonly.py), pasados porstdin
mediante SSH con `UserKnownHostsFile=$HOME/.ssh/known_hosts`,
`StrictHostKeyChecking=yes`, `BatchMode=yes`. No requiere instalar dependencias.
La opción JSON de pvesmstatus no existe en esta versión; se corrigió a pveshget
/nodes/pve/storage y se repitió la captura con éxito.

## Cierre

Auditoría y preparación DONE; ajuste de límites y limpieza TODO. Fases4/7 conservan
pendientes globales. Siguiente: autorización separada para límites619/61211/620,
retirada de clones y traslado del backup100; revalidar antes de cada intervención.
Compilación de scripts, enlaces locales y git diff --check PASS.
Sin borrados, despliegues, reinicios, cambios de recursos ni commit/push.
