# Inventario del host Proxmox VE para IA local

Fecha: 13 de noviembre de 2026 (Europe/Madrid). Inicio de captura UTC: 2026-11-13T10:19:54.974600+00:00.
Lecturas como root en el host `pve`, por SSH estricto. Sin instalaciones, benchmarks, inferencias ni cambios operativos. Medidas sucesivas, no instantánea atómica.

## 1. Resumen ejecutivo

| Concepto | Resultado |
|---|---|
| CPU | Intel Core i5-6500, 4 núcleos/4 hilos; AVX/AVX2/FMA/F16C sí; AVX-512 no |
| RAM | 32 GiB instalados; utilizable 31.23 GiB; máximo SMBIOS 32 GB |
| Libre física sin caché (MemFree) | 1.17 GiB |
| Disponible estimada por Linux (MemAvailable) | 22.49 GiB; incluye memoria recuperable |
| Comprometida guests (Σ maxmem, incluidos apagados) | 69.66 GiB |
| ARC actual / máximo | 960 bytes / 15.62 GiB; mínimo 1 GiB; sin pools ZFS activos |
| RAM tipo/velocidad/canales | 2×16 GB DDR4 SODIMM; 2133 MT/s declarados y configurados; DIMM1 ChannelB y DIMM3 ChannelA |
| Swap | 16.00 GiB total; 2.47 GiB usada |
| GPU | Intel HD Graphics 530 integrada; ninguna dedicada detectada |

## 2. Presupuesto de RAM para IA

Reserva de planificación propuesta para host: 4 GiB, no medición de consumo fijo ni autorización de cambios. Presupuesto estricto = max(0, RAM utilizable − compromisos − reserva).

- (a) Todos los guests: max(0, 31.23 − 69.66 − 4) = **0 GiB**; déficit contable 42.43 GiB.
- Solo guests actualmente en marcha: compromisos 68.61 GiB; también 0 GiB sin sobrecompromiso.
- (b) Si se apagan y dejan de reservar los que tienen onboot=0: se excluyen 12.14 GiB; max(0, 31.23 − 57.52 − 4) = **0.00 GiB**. Apagarlos conserva la configuración: este escenario exige mantenerlos fuera de la planificación concurrente.
- Margen oportunista actual: MemAvailable − reserva = 18.49 GiB. No garantiza admisión sin sobrecompromiso: los CT pueden crecer hasta sus límites.
- (c) Limitar ARC no aporta RAM apreciable: tamaño actual 960 bytes, sin pools. El techo 15.62 GiB no es consumo real. No se modifica.

## 3. Ancho de banda de memoria teórico

**2 × 2133 MT/s × 8 bytes = 34.128 GB/s** decimales (31.78 GiB/s). SMBIOS informa un módulo igual por canal A/B, compatible con dual channel simétrico; no prueba directamente el modo efectivo del controlador. Si solo operase un canal: 17.064 GB/s. Sin benchmark; el ancho de banda sostenido es desconocido.

| Slot | Ocupado | Tamaño | Tipo | Velocidad declarada/configurada | Banco |
|---|---|---|---|---|---|
| DIMM1 | Sí | 16 GB | DDR4 | 2133/2133 MT/s | ChannelB |
| DIMM3 | Sí | 16 GB | DDR4 | 2133/2133 MT/s | ChannelA |

## 4. Almacenamiento

| Storage/pool | Discos / medio | Tipo | Contenido permitido | Total | Libre | SMART |
|---|---|---|---|---|---|---|
| local-lvm | sda SATA / SSD | lvmthin | rootdir,images | 400.09 GiB | 178.64 GiB | PASSED |
| storage | sdb USB / HDD | dir | snippets,vztmpl,rootdir,images,backup | 1396.55 GiB | 1276.49 GiB | PASSED |
| local | sda SATA / SSD | dir | backup,iso,vztmpl | 63.94 GiB | 41.60 GiB | PASSED |

Thin pool pve/data: tamaño físico 400.09 GiB, volúmenes virtuales 768.00 GiB (191.96 %). Datos ocupados 55.35 %, metadata 2.34 %. El porcentaje virtual >100 % expresa sobreaprovisionamiento; no equivale a ocupación física. Snapshots/bloques compartidos impiden equiparar suma virtual y uso real.
El VG pve no tiene espacio sin asignar (VFree=0); no sumar el libre de local y local-lvm como espacio intercambiable. No hay pools ZFS.

## 5. Recomendación

Guardar los 20–40 GB de GGUF en un volumen del SSD `local-lvm`, ligado al CT de llama-server. Proponer también ambos rootfs en ese pool: ofrece unos 178.64 GiB físicos libres y evita la latencia del HDD USB. Dimensionar cuotas y reserva antes de provisionar; los límites virtuales ya exceden el pool. Esta es una propuesta, no un despliegue.
`local` tiene unos 41.60 GiB libres y comparte SSD con el host: 40 GB de modelos consumirían casi todo su margen. Evitarlo para ese objetivo. Reservar HDD `storage` para copias/modelos secundarios si se acepta carga inicial más lenta. No se recomienda crear los CT hasta resolver el presupuesto concurrente de RAM.

## 6. VMs/CTs existentes

| ID | Tipo/nombre | Estado | onboot | RAM asignada / maxmem | RAM usada API | Cores | Storage/discos |
|---|---|---|---|---|---|---|---|
| 101 | lxc docmost | running | 0 (omitido) | 1024 MiB / 1.00 GiB | 0.47 GiB | 2 | rootfs=local-lvm:vm-101-disk-0,size=20G |
| 103 | lxc aws-workshop | running | 0 (omitido) | 5048 MiB / 4.93 GiB | 0.60 GiB | 3 | rootfs=local-lvm:vm-103-disk-0,size=50G |
| 104 | lxc nucleo | running | 0 (omitido) | 1024 MiB / 1.00 GiB | 0.06 GiB | 1 | rootfs=local-lvm:vm-104-disk-0,size=10G |
| 105 | lxc n8n-server | running | 0 (omitido) | 2096 MiB / 2.05 GiB | 0.07 GiB | 2 | rootfs=local-lvm:vm-105-disk-0,size=8G |
| 106 | lxc CT106 | stopped | 0 (omitido) | 1080 MiB / 1.05 GiB | 0.00 GiB | 3 | rootfs=local-lvm:base-106-disk-0,size=50G |
| 107 | lxc drawio | running | 0 (omitido) | 1080 MiB / 1.05 GiB | 0.41 GiB | 3 | rootfs=local-lvm:vm-107-disk-0,size=50G |
| 109 | lxc edge-router | running | 0 (omitido) | 1080 MiB / 1.05 GiB | 0.16 GiB | 3 | rootfs=local-lvm:vm-109-disk-0,size=50G |
| 610 | lxc infra-prom | running | 1 | 2048 MiB / 2.00 GiB | 0.39 GiB | 2 | rootfs=local-lvm:vm-610-disk-0,size=10G |
| 611 | lxc infra-grafana | running | 1 | 1048 MiB / 1.02 GiB | 0.31 GiB | 1 | rootfs=local-lvm:vm-611-disk-0,size=10G |
| 613 | lxc infra-hola | running | 1 | 512 MiB / 0.50 GiB | 0.12 GiB | 1 | rootfs=local-lvm:vm-613-disk-0,size=10G |
| 614 | lxc infra-nucleoedge | running | 1 | 2048 MiB / 2.00 GiB | 0.33 GiB | 2 | rootfs=local-lvm:vm-614-disk-0,size=10G |
| 615 | lxc infra-mailerblend-edge | running | 1 | 2048 MiB / 2.00 GiB | 0.29 GiB | 2 | rootfs=local-lvm:vm-615-disk-0,size=10G |
| 616 | lxc infra-blackbox | running | 1 | 512 MiB / 0.50 GiB | 0.14 GiB | 1 | rootfs=local-lvm:vm-616-disk-0,size=10G |
| 617 | lxc infra-orbit | running | 1 | 512 MiB / 0.50 GiB | 0.23 GiB | 1 | rootfs=local-lvm:vm-617-disk-0,size=10G |
| 618 | lxc infra-composable-crm | running | 1 | 6144 MiB / 6.00 GiB | 1.90 GiB | 2 | rootfs=local-lvm:vm-618-disk-0,size=50G |
| 619 | lxc infra-pulpo | running | 1 | 2048 MiB / 2.00 GiB | 0.72 GiB | 2 | rootfs=local-lvm:vm-619-disk-0,size=10G |
| 620 | lxc infra-excraper | running | 1 | 2048 MiB / 2.00 GiB | 0.33 GiB | 2 | rootfs=local-lvm:vm-620-disk-0,size=10G |
| 621 | lxc infra-project-gestion | running | 1 | 2048 MiB / 2.00 GiB | 0.15 GiB | 2 | rootfs=local-lvm:vm-621-disk-0,size=10G |
| 622 | lxc infra-eva-assistant-bot | running | 1 | 2048 MiB / 2.00 GiB | 0.46 GiB | 2 | rootfs=local-lvm:vm-622-disk-0,size=40G |
| 623 | lxc infra-gestoria | running | 1 | 4096 MiB / 4.00 GiB | 0.60 GiB | 2 | rootfs=local-lvm:vm-623-disk-0,size=50G |
| 624 | lxc infra-journal-web | running | 1 | 512 MiB / 0.50 GiB | 0.19 GiB | 1 | rootfs=local-lvm:vm-624-disk-0,size=50G |
| 625 | lxc infra-journal-db | running | 1 | 2048 MiB / 2.00 GiB | 0.25 GiB | 2 | rootfs=local-lvm:vm-625-disk-0,size=50G |
| 626 | lxc infra-journal-api | running | 1 | 2048 MiB / 2.00 GiB | 0.24 GiB | 2 | rootfs=local-lvm:vm-626-disk-0,size=50G |
| 627 | lxc infra-voicebox | running | 1 | 20480 MiB / 20.00 GiB | 0.75 GiB | 3 | rootfs=local-lvm:vm-627-disk-0,size=100G |
| 61211 | lxc svc01 | running | 1 | 6656 MiB / 6.50 GiB | 0.34 GiB | 3 | rootfs=local-lvm:vm-61211-disk-0,size=40G |

RAM usada procede de la API PVE; para LXC depende de su contabilidad de memoria y caché, no equivale a RSS exclusivo. maxmem es límite configurado, no reserva física.

## 7. Avisos

- RAM comprometida muy superior a la física; MemAvailable alto no elimina este riesgo.
- Swap en uso (~2.47 GiB); no prueba por sí sola presión presente. No se ha vaciado.
- Thin pool sobre el umbral virtual del 80 % (191.96 %), aunque su ocupación física es 55.35 %.
- SSD: SMART PASSED, 47 771 horas, un bloque NAND reasignado y un evento. Atributo 202 etiquetado Percent_Lifetime_Remain: normalizado 77, raw 23; interpretación exacta del fabricante no verificada, no afirmar 23 % restante. Atributo 173: normalizado 77, raw 359. HDD: PASSED, 14 638 horas y cero sectores reasignados/pendientes.
- No hay pools ZFS: módulo y ARC residual presentes; ausencia de zfs.conf no justifica advertir consumo de 15.62 GiB.
- Enlace eno1 a 100 Mb/s: limita transferencias externas. lscpu informa vulnerabilidades sin microcódigo; revisión fuera de este alcance.
- top observa procesos zombie; diagnóstico de su origen queda fuera de este inventario. Carga puntual no predice latencia de inferencia.

## 8. Herramientas no disponibles

Ninguna de las herramientas invocadas falta. nvme no se requiere: no se detecta NVMe.
Estado ksmtuned: active.

## Anexo de lecturas filtradas

### pve

```text
proxmox-ve: 8.3.0 (running kernel: 6.8.12-4-pve)
pve-manager: 8.3.0 (running version: 8.3.0/c1689ccb1065a83b)
proxmox-kernel-helper: 8.1.0
proxmox-kernel-6.8: 6.8.12-4
proxmox-kernel-6.8.12-4-pve-signed: 6.8.12-4
```

### kernel

```text
6.8.12-4-pve
```

### hostname

```text
pve
```

### cpu

```text
Architecture:                         x86_64
CPU op-mode(s):                       32-bit, 64-bit
Address sizes:                        39 bits physical, 48 bits virtual
Byte Order:                           Little Endian
CPU(s):                               4
On-line CPU(s) list:                  0-3
Vendor ID:                            GenuineIntel
BIOS Vendor ID:                       Intel(R) Corporation
Model name:                           Intel(R) Core(TM) i5-6500 CPU @ 3.20GHz
BIOS Model name:                      Intel(R) Core(TM) i5-6500 CPU @ 3.20GHz To Be Filled By O.E.M. CPU @ 3.2GHz
BIOS CPU family:                      205
CPU family:                           6
Model:                                94
Thread(s) per core:                   1
Core(s) per socket:                   4
Socket(s):                            1
Stepping:                             3
CPU(s) scaling MHz:                   93%
CPU max MHz:                          3600.0000
CPU min MHz:                          800.0000
BogoMIPS:                             6399.96
Flags:                                fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb pti ibrs ibpb stibp tpr_shadow flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm mpx rdseed adx smap clflushopt intel_pt xsaveopt xsavec xgetbv1 xsaves dtherm ida arat pln pts hwp hwp_notify hwp_act_window hwp_epp vnmi
Virtualization:                       VT-x
L1d cache:                            128 KiB (4 instances)
L1i cache:                            128 KiB (4 instances)
L2 cache:                             1 MiB (4 instances)
L3 cache:                             6 MiB (1 instance)
NUMA node(s):                         1
NUMA node0 CPU(s):                    0-3
Vulnerability Gather data sampling:   Vulnerable: No microcode
Vulnerability Itlb multihit:          KVM: Mitigation: VMX disabled
Vulnerability L1tf:                   Mitigation; PTE Inversion; VMX conditional cache flushes, SMT disabled
Vulnerability Mds:                    Vulnerable: Clear CPU buffers attempted, no microcode; SMT disabled
Vulnerability Meltdown:               Mitigation; PTI
Vulnerability Mmio stale data:        Vulnerable: Clear CPU buffers attempted, no microcode; SMT disabled
Vulnerability Reg file data sampling: Not affected
Vulnerability Retbleed:               Mitigation; IBRS
Vulnerability Spec rstack overflow:   Not affected
Vulnerability Spec store bypass:      Vulnerable
Vulnerability Spectre v1:             Mitigation; usercopy/swapgs barriers and __user pointer sanitization
Vulnerability Spectre v2:             Mitigation; IBRS; IBPB conditional; STIBP disabled; RSB filling; PBRSB-eIBRS Not affected; BHI Not affected
Vulnerability Srbds:                  Vulnerable: No microcode
Vulnerability Tsx async abort:        Vulnerable: Clear CPU buffers attempted, no microcode; SMT disabled
```

### governor

```text
performance
```

### free

```text
total        used        free      shared  buff/cache   available
Mem:            31Gi       8.7Gi       1.2Gi       188Mi        21Gi        22Gi
Swap:           15Gi       2.5Gi        13Gi
```

### meminfo

```text
MemTotal:       32747112 kB
MemFree:         1228744 kB
MemAvailable:   23577452 kB
Buffers:         1040860 kB
Cached:         17749900 kB
SwapCached:       182468 kB
Active:          7072208 kB
Inactive:       18629520 kB
Active(anon):    4367508 kB
Inactive(anon):  2737244 kB
Active(file):    2704700 kB
Inactive(file): 15892276 kB
Unevictable:       30664 kB
Mlocked:           30540 kB
SwapTotal:      16777212 kB
SwapFree:       14185980 kB
Zswap:                 0 kB
Zswapped:              0 kB
Dirty:              4624 kB
Writeback:             0 kB
AnonPages:       6814480 kB
Mapped:          2736112 kB
Shmem:            193508 kB
KReclaimable:    4215996 kB
Slab:            5161512 kB
SReclaimable:    4215996 kB
SUnreclaim:       945516 kB
KernelStack:       71472 kB
PageTables:       190864 kB
SecPageTables:         0 kB
NFS_Unstable:          0 kB
Bounce:                0 kB
WritebackTmp:          0 kB
CommitLimit:    33150768 kB
Committed_AS:   40122016 kB
VmallocTotal:   34359738367 kB
VmallocUsed:      179784 kB
VmallocChunk:          0 kB
Percpu:            22000 kB
HardwareCorrupted:     0 kB
AnonHugePages:     12288 kB
ShmemHugePages:        0 kB
ShmemPmdMapped:        0 kB
FileHugePages:   2086912 kB
FilePmdMapped:         0 kB
Unaccepted:            0 kB
HugePages_Total:       0
HugePages_Free:        0
HugePages_Rsvd:        0
HugePages_Surp:        0
Hugepagesize:       2048 kB
Hugetlb:               0 kB
DirectMap4k:      673384 kB
DirectMap2M:    23320576 kB
DirectMap1G:     9437184 kB
```

### swap

```text
NAME      TYPE      SIZE USED PRIO
/dev/dm-0 partition  16G 2.5G   -2
```

### ksm

```text
0
```

### ksmtuned

```text
active
```

### arcstats

```text
c_min                           4    1047907584
c_max                           4    16766521344
size                            4    960
```

### zfs_conf

```text

```

### node

```text
{
  "memory": {
    "free": 20364951552,
    "total": 33533042688,
    "used": 13168091136
  },
  "cpu": 0,
  "loadavg": [
    "0.84",
    "1.19",
    "1.95"
  ],
  "swap": {
    "free": 14526181376,
    "total": 17179865088,
    "used": 2653683712
  }
}
```

### qm_list

```text

```

### pct_list

```text
VMID       Status     Lock         Name
101        running                 docmost
103        running                 aws-workshop
104        running                 nucleo
105        running                 n8n-server
106        stopped                 CT106
107        running                 drawio
109        running                 edge-router
610        running                 infra-prom
611        running                 infra-grafana
613        running                 infra-hola
614        running                 infra-nucleoedge
615        running                 infra-mailerblend-edge
616        running                 infra-blackbox
617        running                 infra-orbit
618        running                 infra-composable-crm
619        running                 infra-pulpo
620        running                 infra-excraper
621        running                 infra-project-gestion
622        running                 infra-eva-assistant-bot
623        running                 infra-gestoria
624        running                 infra-journal-web
625        running                 infra-journal-db
626        running                 infra-journal-api
627        running                 infra-voicebox
61211      running                 svc01
```

### storage_status

```text
Name             Type     Status           Total            Used       Available        %
local             dir     active        67043328        23419020        43624308   34.93%
local-lvm     lvmthin     active       419520512       232204603       187315908   55.35%
storage           dir     active      1464390028       125897068      1338492960    8.60%
```

### storage_cfg

```text
dir: local
	path /var/lib/vz
	content iso,vztmpl,backup
lvmthin: local-lvm
	thinpool data
	vgname pve
	content images,rootdir
dir: storage
	path /mnt/storage
	content images,snippets,vztmpl,rootdir,backup
	shared 0
```

### disks

```text
{
  "blockdevices": [
    {
      "name": "sda",
      "size": 525112713216,
      "type": "disk",
      "rota": false,
      "tran": "sata",
      "model": "Crucial_CT525MX300SSD1",
      "serial": "…9492",
      "fstype": null,
      "mountpoints": [
        null
      ],
      "children": [
        {
          "name": "sda1",
          "size": 1031168,
          "type": "part",
          "rota": false,
          "tran": null,
          "model": null,
          "serial": null,
          "fstype": null,
          "mountpoints": [
            null
          ]
        },
        {
          "name": "sda2",
          "size": 1073741824,
          "type": "part",
          "rota": false,
          "tran": null,
          "model": null,
          "serial": null,
          "fstype": "vfat",
          "mountpoints": [
            "/boot/efi"
          ]
        },
        {
          "name": "sda3",
          "size": 524037905920,
          "type": "part",
          "rota": false,
          "tran": null,
          "model": null,
          "serial": null,
          "fstype": "LVM2_member",
          "mountpoints": [
            null
          ],
          "children": [
            {
              "name": "pve-swap",
              "size": 17179869184,
              "type": "lvm",
              "rota": false,
              "tran": null,
              "model": null,
              "serial": null,
              "fstype": "swap",
              "mountpoints": [
                "[SWAP]"
              ]
            },
            {
              "name": "pve-root",
              "size": 68719476736,
              "type": "lvm",
              "rota": false,
              "tran": null,
              "model": null,
              "serial": null,
              "fstype": "xfs",
              "mountpoints": [
                "/"
              ]
            },
            {
              "name": "pve-data_tmeta",
              "size": 4273995776,
              "type": "lvm",
              "rota": false,
              "tran": null,
              "model": null,
              "serial": null,
              "fstype": null,
              "mountpoints": [
                null
              ],
              "children": [
                {
                  "name": "pve-data-tpool",
                  "size": 429589004288,
                  "type": "lvm",
                  "rota": false,
                  "tran": null,
                  "model": null,
                  "serial": null,
                  "fstype": null,
                  "mountpoints": [
                    null
                  ],
                  "children": [
                    {
                      "name": "pve-data",
                      "size": 429589004288,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": null,
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--101--disk--0",
                      "size": 21474836480,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--105--disk--0",
                      "size": 8589934592,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--103--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--107--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--109--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--104--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--613--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--610--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--61211--disk--0",
                      "size": 42949672960,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--611--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--614--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--615--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--616--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--617--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--618--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--619--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--620--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--621--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--622--disk--0",
                      "size": 42949672960,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--623--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--624--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--626--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--625--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--627--disk--0",
                      "size": 107374182400,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "name": "pve-data_tdata",
              "size": 429589004288,
              "type": "lvm",
              "rota": false,
              "tran": null,
              "model": null,
              "serial": null,
              "fstype": null,
              "mountpoints": [
                null
              ],
              "children": [
                {
                  "name": "pve-data-tpool",
                  "size": 429589004288,
                  "type": "lvm",
                  "rota": false,
                  "tran": null,
                  "model": null,
                  "serial": null,
                  "fstype": null,
                  "mountpoints": [
                    null
                  ],
                  "children": [
                    {
                      "name": "pve-data",
                      "size": 429589004288,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": null,
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--101--disk--0",
                      "size": 21474836480,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--105--disk--0",
                      "size": 8589934592,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--103--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--107--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--109--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--104--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--613--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--610--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--61211--disk--0",
                      "size": 42949672960,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--611--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--614--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--615--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--616--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--617--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--618--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--619--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--620--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--621--disk--0",
                      "size": 10737418240,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--622--disk--0",
                      "size": 42949672960,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--623--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--624--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--626--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--625--disk--0",
                      "size": 53687091200,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    },
                    {
                      "name": "pve-vm--627--disk--0",
                      "size": 107374182400,
                      "type": "lvm",
                      "rota": false,
                      "tran": null,
                      "model": null,
                      "serial": null,
                      "fstype": "ext4",
                      "mountpoints": [
                        null
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "sdb",
      "size": 1500267937792,
      "type": "disk",
      "rota": true,
      "tran": "usb",
      "model": "WDC WD15JDRW-11C7VS1",
      "serial": "…9V49",
      "fstype": "xfs",
      "mountpoints": [
        "/mnt/storage"
      ]
    }
  ]
}
```

### smart

```text
{
  "/dev/sda": "SMART overall-health self-assessment test result: PASSED\n  9 Power_On_Hours          0x0032   100   100   000    Old_age   Always       -       47771\n196 Reallocated_Event_Count 0x0032   100   100   000    Old_age   Always       -       1\n198 Offline_Uncorrectable   0x0030   100   100   000    Old_age   Offline      -       0\n  5 Reallocate_NAND_Blk_Cnt 0x0032   100   100   010    Old_age   Always       -       1\n173 Ave_Block-Erase_Count   0x0032   077   077   000    Old_age   Always       -       359\n202 Percent_Lifetime_Remain 0x0030   077   077   001    Old_age   Offline      -       23",
  "/dev/sdb": "SMART overall-health self-assessment test result: PASSED\n  5 Reallocated_Sector_Ct   0x0033   200   200   140    Pre-fail  Always       -       0\n  9 Power_On_Hours          0x0032   080   080   000    Old_age   Always       -       14638\n196 Reallocated_Event_Count 0x0032   200   200   000    Old_age   Always       -       0\n197 Current_Pending_Sector  0x0032   200   200   000    Old_age   Always       -       0\n198 Offline_Uncorrectable   0x0030   100   253   000    Old_age   Offline      -       0"
}
```

### pvs

```text
PV         VG  Fmt  Attr PSize    PFree
  /dev/sda3  pve lvm2 a--  <488.05g    0
```

### vgs

```text
VG  #PV #LV #SN Attr   VSize    VFree
  pve   1  28   0 wz--n- <488.05g    0
```

### lvs

```text
LV              VG  LSize    Data%  Meta%  Pool
  base-106-disk-0 pve   50.00g               data
  data            pve <400.09g 55.35  2.34
  [data_tdata]    pve <400.09g
  [data_tmeta]    pve    3.98g
  [lvol0_pmspare] pve    3.98g
  root            pve   64.00g
  swap            pve   16.00g
  vm-101-disk-0   pve   20.00g 31.93         data
  vm-103-disk-0   pve   50.00g 40.30         data
  vm-104-disk-0   pve   10.00g 18.69         data
  vm-105-disk-0   pve    8.00g 61.29         data
  vm-107-disk-0   pve   50.00g 13.55         data
  vm-109-disk-0   pve   50.00g 9.64          data
  vm-610-disk-0   pve   10.00g 93.22         data
  vm-611-disk-0   pve   10.00g 47.14         data
  vm-61211-disk-0 pve   40.00g 15.02         data
  vm-613-disk-0   pve   10.00g 21.71         data
  vm-614-disk-0   pve   10.00g 51.43         data
  vm-615-disk-0   pve   10.00g 38.25         data
  vm-616-disk-0   pve   10.00g 22.04         data
  vm-617-disk-0   pve   10.00g 53.16         data
  vm-618-disk-0   pve   50.00g 47.60         data
  vm-619-disk-0   pve   10.00g 55.83         data
  vm-620-disk-0   pve   10.00g 54.83         data
  vm-621-disk-0   pve   10.00g 23.66         data
  vm-622-disk-0   pve   40.00g 63.17         data
  vm-623-disk-0   pve   50.00g 15.87         data
  vm-624-disk-0   pve   50.00g 8.98          data
  vm-625-disk-0   pve   50.00g 8.80          data
  vm-626-disk-0   pve   50.00g 8.37          data
  vm-627-disk-0   pve  100.00g 49.46         data
```

### zpool

```text
no pools available
```

### zpool_status

```text

```

### zfs

```text

```

### df

```text
Filesystem           Type      Size  Used Avail Use% Mounted on
/dev/mapper/pve-root xfs        64G   23G   42G  35% /
efivarfs             efivarfs  150K   85K   61K  59% /sys/firmware/efi/efivars
/dev/sda2            vfat     1022M   12M 1011M   2% /boot/efi
/dev/sdb             xfs       1.4T  121G  1.3T   9% /mnt/storage
/dev/fuse            fuse      128M   44K  128M   1% /etc/pve
```

### directories

```text
{
  "/srv": "0\t/srv",
  "/var/lib/vz": "16G\t/var/lib/vz",
  "/mnt/storage": "111G\t/mnt/storage",
  "/mnt/vzsnap0": "0\t/mnt/vzsnap0"
}
```

### gpu

```text
00:02.0 VGA compatible controller [0300]: Intel Corporation HD Graphics 530 [8086:1912] (rev 06)
```

### network

```text
lo               UNKNOWN        127.0.0.1/8 ::1/128
eno1             UP
vmbr0            UP             192.168.1.100/24 fe80::1262:e5ff:fe19:13cd/64
veth610i0@if2    UP
fwbr610i0        UP
fwpr610p0@fwln610i0 UP
fwln610i0@fwpr610p0 UP
veth611i0@if2    UP
fwbr611i0        UP
fwpr611p0@fwln611i0 UP
fwln611i0@fwpr611p0 UP
veth613i0@if2    UP
fwbr613i0        UP
fwpr613p0@fwln613i0 UP
fwln613i0@fwpr613p0 UP
veth614i0@if2    UP
fwbr614i0        UP
fwpr614p0@fwln614i0 UP
fwln614i0@fwpr614p0 UP
veth615i0@if2    UP
fwbr615i0        UP
fwpr615p0@fwln615i0 UP
fwln615i0@fwpr615p0 UP
veth616i0@if2    UP
fwbr616i0        UP
fwpr616p0@fwln616i0 UP
fwln616i0@fwpr616p0 UP
veth617i0@if2    UP
fwbr617i0        UP
fwpr617p0@fwln617i0 UP
fwln617i0@fwpr617p0 UP
veth618i0@if2    UP
fwbr618i0        UP
fwpr618p0@fwln618i0 UP
fwln618i0@fwpr618p0 UP
veth619i0@if2    UP
fwbr619i0        UP
fwpr619p0@fwln619i0 UP
fwln619i0@fwpr619p0 UP
veth620i0@if2    UP
fwbr620i0        UP
fwpr620p0@fwln620i0 UP
fwln620i0@fwpr620p0 UP
veth621i0@if2    UP
fwbr621i0        UP
fwpr621p0@fwln621i0 UP
fwln621i0@fwpr621p0 UP
veth622i0@if2    UP
fwbr622i0        UP
fwpr622p0@fwln622i0 UP
fwln622i0@fwpr622p0 UP
veth623i0@if2    UP
fwbr623i0        UP
fwpr623p0@fwln623i0 UP
fwln623i0@fwpr623p0 UP
veth624i0@if2    UP
fwbr624i0        UP
fwpr624p0@fwln624i0 UP
fwln624i0@fwpr624p0 UP
veth625i0@if2    UP
fwbr625i0        UP
fwpr625p0@fwln625i0 UP
fwln625i0@fwpr625p0 UP
veth626i0@if2    UP
fwbr626i0        UP
fwpr626p0@fwln626i0 UP
fwln626i0@fwpr626p0 UP
veth627i0@if2    UP
fwbr627i0        UP
fwpr627p0@fwln627i0 UP
fwln627i0@fwpr627p0 UP
veth61211i0@if2  UP
fwbr61211i0      UP
fwpr61211p0@fwln61211i0 UP
fwln61211i0@fwpr61211p0 UP
veth109i0@if2    UP
fwbr109i0        UP
fwpr109p0@fwln109i0 UP
fwln109i0@fwpr109p0 UP
veth107i0@if2    UP
fwbr107i0        UP
fwpr107p0@fwln107i0 UP
fwln107i0@fwpr107p0 UP
veth105i0@if2    UP
fwbr105i0        UP
fwpr105p0@fwln105i0 UP
fwln105i0@fwpr105p0 UP
veth104i0@if2    UP
fwbr104i0        UP
fwpr104p0@fwln104i0 UP
fwln104i0@fwpr104p0 UP
veth103i0@if2    UP
fwbr103i0        UP
fwpr103p0@fwln103i0 UP
fwln103i0@fwpr103p0 UP
veth101i0@if2    UP
fwbr101i0        UP
fwpr101p0@fwln101i0 UP
fwln101i0@fwpr101p0 UP
```

### bridges

```text
iface vmbr0 inet static
	address 192.168.1.100/24
	gateway 192.168.1.254
	bridge-ports eno1
	bridge-stp off
	bridge-fd 0

source /etc/network/interfaces.d/*
```

### links

```text
{
  "eno1": "Speed: 100Mb/s"
}
```

### uptime

```text
11:19:56 up 1 day, 16:32,  0 user,  load average: 0.46, 1.15, 1.95
```

### top

```text
top - 11:20:56 up 1 day, 16:33,  0 user,  load average: 1.16, 1.26, 1.94
Tasks: 1441 total,   4 running, 1231 sleeping,   0 stopped, 206 zombie
%Cpu(s):  6.7 us, 20.0 sy,  0.0 ni, 73.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :  31979.6 total,   1243.7 free,   8905.0 used,  22473.6 buff/cache
MiB Swap:  16384.0 total,  13853.2 free,   2530.8 used.  23074.6 avail Mem

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
2207318 root      20   0   27140  20168   9984 R  63.2   0.1   0:00.12 python
2207303 root      20   0   14136   6728   3784 R  15.8   0.0   0:00.06 top
2207337 root      20   0    8732   2944   2176 S  10.5   0.0   0:00.02 pg_isre+
  21133 root      20   0 1341452  56636  18048 S   5.3   0.2   0:16.10 node
  21880 999       20   0   39368   3584   2304 S   5.3   0.0   9:35.52 redis-s+
2070936 root      20   0       0      0      0 R   5.3   0.0   0:01.08 kworker+
3693974 root      20   0 1233840  11932   7296 S   5.3   0.0   0:16.59 contain+
      1 root      20   0  170732  13740   8876 S   0.0   0.0   0:17.62 systemd
      2 root      20   0       0      0      0 S   0.0   0.0   0:00.07 kthreadd
      3 root      20   0       0      0      0 S   0.0   0.0   0:00.00 pool_wo+
      4 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker+
      5 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker+
      6 root       0 -20       0      0      0 I   0.0   0.0   0:00.00 kworker+
```

### processes

```text
PID USER     COMMAND           RSS %CPU %MEM
  72765 root     pt_main_thread  370452 0.1  1.1
1865510 999      uvicorn         327216 0.2  0.9
  22294 root     node            279952 0.0  0.8
  54646 1001     java            279048 0.1  0.8
  22312 root     node            240456 0.0  0.7
  29232 root     node            228712 0.0  0.6
  29063 root     node            217928 0.0  0.6
  99034 101000   node            213232 0.0  0.6
   4246 472      grafana         206000 0.9  0.6
 974467 nobody   prometheus      205160 0.7  0.6
```

### Configuración seleccionada de guests

```json
[
  {
    "vmid": 621,
    "config": {
      "cores": "2",
      "memory": "2048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-621-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 107,
    "config": {
      "cores": "3",
      "memory": "1080",
      "rootfs": "local-lvm:vm-107-disk-0,size=50G",
      "swap": "512"
    }
  },
  {
    "vmid": 615,
    "config": {
      "cores": "2",
      "memory": "2048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-615-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 614,
    "config": {
      "cores": "2",
      "memory": "2048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-614-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 623,
    "config": {
      "cores": "2",
      "memory": "4096",
      "onboot": "1",
      "rootfs": "local-lvm:vm-623-disk-0,size=50G",
      "swap": "512"
    }
  },
  {
    "vmid": 610,
    "config": {
      "cores": "2",
      "memory": "2048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-610-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 103,
    "config": {
      "cores": "3",
      "memory": "5048",
      "rootfs": "local-lvm:vm-103-disk-0,size=50G",
      "swap": "804"
    }
  },
  {
    "vmid": 619,
    "config": {
      "cores": "2",
      "memory": "2048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-619-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 61211,
    "config": {
      "cores": "3",
      "memory": "6656",
      "onboot": "1",
      "rootfs": "local-lvm:vm-61211-disk-0,size=40G",
      "swap": "512"
    }
  },
  {
    "vmid": 618,
    "config": {
      "cores": "2",
      "memory": "6144",
      "onboot": "1",
      "rootfs": "local-lvm:vm-618-disk-0,size=50G",
      "swap": "512"
    }
  },
  {
    "vmid": 616,
    "config": {
      "cores": "1",
      "memory": "512",
      "onboot": "1",
      "rootfs": "local-lvm:vm-616-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 101,
    "config": {
      "cores": "2",
      "memory": "1024",
      "rootfs": "local-lvm:vm-101-disk-0,size=20G",
      "swap": "1024"
    }
  },
  {
    "vmid": 627,
    "config": {
      "cores": "3",
      "memory": "20480",
      "onboot": "1",
      "rootfs": "local-lvm:vm-627-disk-0,size=100G",
      "swap": "2048"
    }
  },
  {
    "vmid": 611,
    "config": {
      "cores": "1",
      "memory": "1048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-611-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 106,
    "config": {
      "cores": "3",
      "memory": "1080",
      "rootfs": "local-lvm:base-106-disk-0,size=50G",
      "swap": "512"
    }
  },
  {
    "vmid": 624,
    "config": {
      "cores": "1",
      "memory": "512",
      "onboot": "1",
      "rootfs": "local-lvm:vm-624-disk-0,size=50G",
      "swap": "512"
    }
  },
  {
    "vmid": 625,
    "config": {
      "cores": "2",
      "memory": "2048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-625-disk-0,size=50G",
      "swap": "512"
    }
  },
  {
    "vmid": 109,
    "config": {
      "cores": "3",
      "memory": "1080",
      "rootfs": "local-lvm:vm-109-disk-0,size=50G",
      "swap": "512"
    }
  },
  {
    "vmid": 613,
    "config": {
      "cores": "1",
      "memory": "512",
      "onboot": "1",
      "rootfs": "local-lvm:vm-613-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 620,
    "config": {
      "cores": "2",
      "memory": "2048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-620-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 622,
    "config": {
      "cores": "2",
      "memory": "2048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-622-disk-0,size=40G",
      "swap": "512"
    }
  },
  {
    "vmid": 104,
    "config": {
      "cores": "1",
      "memory": "1024",
      "rootfs": "local-lvm:vm-104-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 105,
    "config": {
      "cores": "2",
      "memory": "2096",
      "rootfs": "local-lvm:vm-105-disk-0,size=8G",
      "swap": "1048"
    }
  },
  {
    "vmid": 617,
    "config": {
      "cores": "1",
      "memory": "512",
      "onboot": "1",
      "rootfs": "local-lvm:vm-617-disk-0,size=10G",
      "swap": "512"
    }
  },
  {
    "vmid": 626,
    "config": {
      "cores": "2",
      "memory": "2048",
      "onboot": "1",
      "rootfs": "local-lvm:vm-626-disk-0,size=50G",
      "swap": "512"
    }
  }
]
```
