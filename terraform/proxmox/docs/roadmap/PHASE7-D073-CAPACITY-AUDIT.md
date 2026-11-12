# Fase 7.4 — D-073: auditoría de capacidad Proxmox y CT627

Estado: **DONE — auditoría de solo lectura**. Fase 7.4 y clonación larga continúan
**IN PROGRESS / BLOCKED**, sin nueva aceptación ni permiso de despliegue.
11nov2026, Europe/Madrid. Primera memoria:15:42:46–15:42:57 CET
(14:42:46–14:42:57 UTC); cada evidencia conserva su marcaUTC. AutorizaciónD073:
medir, proponer y detenerse. **No se eliminó ni archivó nada, no se liberó caché,
no se inició Qwen ni otro motor y no se modificó producción**. La petición inicial
de recuperar disco no sustituye la prohibición explícita de borrados posterior.

## Resultado y recomendación

Hay margen físico de memoria en la ventana observada: **15,504GiB físicos y
9,070 GiB disponibles** en el primer snapshot. No confundir límitesLXC con RAM
reservada. **La presión actual se localiza casi íntegramente en cAdvisor de CT618,
limitado a128MiB**, no en una inferenciaQwen activa: sin Qwen, durante60,031s,
PSIfullhost sube hasta5,67%, con8,832GiB como mínimo disponibles. Stall acumulado
host 1,188891s; cAdvisor de CT6181,189870s; CT627 0,000029s. Son medidas de intervalos
muy próximos, no contadores que deban sumarse entre padre e hijo.

Esto demuestra una fuente de presión independiente de Qwen en D073. **No reconstruye
por sí solo la causa exacta del pico D072**, porque faltaron series dePSI por cgroup
durante aquel ensayo. La combinación plausible es carga adicional de627, caché/IO
más presión de un cgroup con límite local; falta evidencia para asignar porcentajes
al episodio pasado. No concluir escasez global deRAM ni culpar únicamente a627.

Disco: **7,056GiB disponibles**, avisoHostDiskFilling **FIRING**, sin fallos de
liveness. Docker/containerd17,482GiB y backups13,700GiB dominan el consumo.
CandidatosA+B identificados **hasta11,946GiB**, condicionados a revisión yretención;
ningún byte recuperado enesta intervención. No incluye retirar modelos, perfiles,
originales, historial ni imágenes de rollback. No garantizar recuperar el estado
exacto del disco inicial: faltaría conservar sus datos actuales y una política de
retención aprobada; no se propone revertir producción a un snapshot antiguo.

**Recomendación:** revisar mediante alcance separado el límite de cAdvisor de CT618,
autorizar después limpiezaA acotada y valorar copiasB fueraCT con restore verificado.
No aumentar RAM. No otra inferencia ni compra de GPU por este cierre. Otra prueba
corta C/INT8 sería planteable por memoria física, pero aún no está validada ni
autorizada operativamente tras revisar presión, espacio y configuración experimental.

## Memoria física y consumo global

GiB=2^30B; snapshot a14:42:57UTC. Datos de `/proc/meminfo`, no valores virtualizados
por LXCFS. RAM física instalada nominal16GiB; MemTotal visible15,504GiB.

| Concepto | GiB | Interpretación |
|---|---:|---|
| MemTotal | 15.504 | Capacidad visible al kernel |
| MemAvailable | 9.070 | Estimación kernel utilizable sin exigir swap adicional |
| MemFree | 1.366 | Páginas actualmente libres |
| Total−Available | 6.434 | Uso efectivo estimado, definición explícita |
| Total−Free | 14.137 | Ocupación incluye caché recuperable |
| Cached | 4.716 | Caché de archivos; no es toda irrecuperable |
| Buffers | 0.374 | Buffers de bloque |
| SReclaimable | 3.013 | Slab potencialmente recuperable |
| Cached+Buffers+SReclaimable−Shmem | 8.030 | Aproximación de caché recuperable, no garantía instantánea |
| AnonPages | 4.877 | Anónima residente global |
| SUnreclaim | 0.589 | Slab no recuperable |
| Swap total | 16.000 | Swap no equivale aRAM física |
| Swap utilizada | 5.253 | Páginas desplazadas, no tasa de intercambio |
| Swap libre | 10.747 | Capacidad restante |

Los24 LXC activos suman límites de **55,609GiB**,3,59veces MemTotal: sobreasignación
potencial, **sin reserva física garantizada**. Si todos alcanzaran simultáneamente
sus límites, no cabrían. Su consumo cgroup observado suma12.673GiB,
con caché ykernel incluidos; no se debe sumar otra vez esa caché a meminfo.
Tres configuraciones paradas106/9618/9622 no consumen comoLXC activos enesta tabla.
Hay27 configuraciones,24cgroupsLXC activos; además de los18 gestionados por elproyecto
existen otrosLXC del propietario que también comparten el host.

`Committed_AS`40.172GiB, `CommitLimit`23.752GiB,
overcommit_memory=0: compromiso virtual/heurística, no memoria residente ni otra
reserva física que pueda sumarse a los límites anteriores.

## Consumo por LXC

Snapshot no atómico pero próximo. Cgroupv2 en PVE, una fila porCT, sin doble contar
padres/hijos. Anon/file/kernel son componentes de current y pueden diferir ligeramente
por actualización de contadores; kernel incluye caché de metadatos. Todos enGiB.

| CT y servicio | Límite RAM | Current | Anon | File/cache | Kernel | Swap |
|---|---:|---:|---:|---:|---:|---:|
| 627 infra-voicebox | 7.000 | 3.556 | 0.539 | 2.615 | 0.401 | 0.060 |
| 618 infra-composable-crm | 6.000 | 2.071 | 1.499 | 0.190 | 0.365 | 0.500 |
| 619 infra-pulpo | 2.000 | 0.779 | 0.215 | 0.168 | 0.394 | 0.240 |
| 623 infra-gestoria | 4.000 | 0.678 | 0.126 | 0.232 | 0.319 | 0.209 |
| 610 infra-prom | 2.000 | 0.523 | 0.326 | 0.122 | 0.074 | 0.131 |
| 622 infra-eva-assistant-bot | 2.000 | 0.435 | 0.173 | 0.122 | 0.138 | 0.279 |
| 614 infra-nucleoedge | 2.000 | 0.404 | 0.146 | 0.113 | 0.145 | 0.094 |
| 61211 svc01 | 6.500 | 0.378 | 0.104 | 0.118 | 0.153 | 0.239 |
| 611 infra-grafana | 1.023 | 0.376 | 0.212 | 0.096 | 0.067 | 0.114 |
| 615 infra-mailerblend-edge | 2.000 | 0.355 | 0.124 | 0.110 | 0.120 | 0.080 |
| 620 infra-excraper | 2.000 | 0.351 | 0.124 | 0.091 | 0.134 | 0.128 |
| 625 infra-journal-db | 2.000 | 0.336 | 0.085 | 0.146 | 0.104 | 0.090 |
| 103 aws-workshop | 4.930 | 0.302 | 0.145 | 0.061 | 0.091 | 0.785 |
| 101 docmost | 1.000 | 0.296 | 0.178 | 0.061 | 0.055 | 0.504 |
| 617 infra-orbit | 0.500 | 0.288 | 0.112 | 0.082 | 0.094 | 0.096 |
| 626 infra-journal-api | 2.000 | 0.244 | 0.079 | 0.070 | 0.094 | 0.137 |
| 624 infra-journal-web | 0.500 | 0.223 | 0.069 | 0.063 | 0.090 | 0.071 |
| 107 drawio | 1.055 | 0.189 | 0.083 | 0.026 | 0.077 | 0.297 |
| 621 infra-project-gestion | 2.000 | 0.185 | 0.075 | 0.066 | 0.043 | 0.059 |
| 616 infra-blackbox | 0.500 | 0.184 | 0.079 | 0.068 | 0.037 | 0.057 |
| 109 edge-router | 1.055 | 0.157 | 0.031 | 0.049 | 0.076 | 0.074 |
| 613 infra-hola | 0.500 | 0.147 | 0.056 | 0.059 | 0.032 | 0.049 |
| 104 nucleo | 1.000 | 0.132 | 0.022 | 0.092 | 0.018 | 0.038 |
| 105 n8n-server | 2.047 | 0.085 | 0.029 | 0.033 | 0.020 | 0.048 |

CT627 es la mayor carga contabilizada en reposo por **2,615GiB de file/cache**, con
solo0,539GiB anónimos. No hayQwen/OpenVoice residentes. Trece contenedoresDocker
parados no consumen CPU/RAM de inferencia. Borrar sus objetos libera pocosMiB de
disco, no variosGiB deRAM. No forzar drop_caches, swapoff ni detener otros servicios.
La auditoría de metadatos puede aumentar caché/slab: no interpretar ese crecimiento
como una nueva carga de modelo ni fuga sin medir anon/procesos.

## Host fuera de LXC, presión y OOM

PSS de procesos fueraLXC: **0.346GiB**, anónima
0.246GiB ySwapPss
0.820GiB. PSS distribuye páginas
compartidas; no sumar RSS de procesos sin corregir compartición.
Residual `(MemTotal−MemFree)−ΣcurrentLXC`: **1.464GiB**,
que incluye kernel/caché/charges fuera de esas filas, no solo aplicacionesPVE.
No se detecta aquí un proceso residente del host de variosGiB que explique todo.
SwapLXC agregado4,379GiB frente a5,253GiB globales; snapshots/PSS no ofrecen una
identidad contable exacta de todas las páginas swap.

Primera ventana10s: PSIfullavg10host0,25%, sin pgscan_direct/kswapd niOOM nuevos.
En observación posterior60s31muestras, hostdisponible≥8,832GiB, PSIfullavg10
0,03–5,67%. Swap-in15079páginas≈58,90MiB,swap-out71páginas≈0,28MiB,23053majorfaults;
pgscan_direct/kswapd yallocstall_normal globales sin incremento. Estos ceros no
niegan la reclamación **local** de cgroup que sí se observa.

cAdvisor de CT618: uso133,08–134,22MB frente a134.217.728B de memory.max; +4918eventos
`max` en60s,0 OOM nuevos. En otra ventana10s: +38max,+2414pgscan,+2232pgsteal,
+2456refault_file,+147majorfaults. SwapCT618 casi512MiB/512MiB; cAdvisor tiene
su propio límite RAM 128 MiB yswap permitido128MiB. PadreCT618RAM6GiB queda lejos
de su límite. Es coherente con reclaim/IO por límite local aun con RAM física disponible.
Identificación read-only delDocker confirma nombre `/cadvisor`, reinicios0.
No se ha cambiado su límite ni su servicio; CT618 está fuera de la autorización.

OOM históricos: `/proc/vmstat oom_kill=6` y CT618memory.events oom/oom_kill1/1
acumulados; no se fechan como recientes. Kerneljournal retenido desde10novUTC:
0 coincidencias;0 incrementosOOM en ventanas observadas. CT627OOM0.
No afirmar que nunca huboOOM ni que el journal disponible cubre toda la historia.

**Limitación de monitorización:** los18 `node_pressure_memory_stalled_seconds_total`
observados rondan1.834.323s y coinciden con PSIglobal del host, frente a~6s acumulados
del cgroup627. No son18 fuentes independientes de PSI deLXC; usar cgroupv2 para
atribución. No modificar exporters/CPUcontratos aceptados enesta auditoría.

## Disco CT627 por categorías

`df -B1`: capacidadFS52.521.566.208B=48,915GiB, usados42.243.751.936B=39,343GiB,
disponibles7.576.682.496B=7,056GiB. Disco nominal50GiB; diferencia total−usado−
disponible≈2,516GiB no está disponible a usuarios normales por contabilidad/reserva
FS. No se ha cambiado reserva ext4 ni tamaño. `du -x` raíz42.207.768.576B; pequeña
diferencia condf por metadatos/actividad y contabilidad. `du` no atraviesa otrosFS.

Tabla de áreas principales, **sin sumar de nuevo los desgloses posteriores**:

| Categoría | Bytes asignados | GiB |
|---|---:|---:|
| SO/base restante, excluidas filas siguientes | 1.955.459.072 | 1,821 |
| Docker+containerd, imágenes/caché/runtime | 18.771.075.072 | 17,482 |
| /opt completo, sobre todo backups | 14.957.502.464 | 13,930 |
| /srv completo, modelos/datos/pilotos | 5.947.146.240 | 5,539 |
| /var/log | 97.767.424 | 0,091 |
| APTlistas/cache y/tmp,/var/tmp | 478.818.304 | 0,446 |

| Desglose dentro de las áreas anteriores | Bytes asignados | GiB / observación |
|---|---:|---|
| Backups /opt/voicebox/backups | 14.709.608.448 | 13,700 |
| Fuente/recetas /opt/voicebox sin backups | 213.192.704 | 0,199 |
| Containerd snapshots overlay | 16.405.360.640 | 15,279 |
| Containerd blobs/content | 2.346.217.472 | 2,185 |
| Docker metadata/runtime | 16.453.632 | 0,015 |
| HuggingFace productivo completo | 2.845.691.904 | 2,650; contiene Base+Kokoro |
| QwenBase0.6B, archivos delcache | 2.516.152.320 | 2,343; protegido |
| QwenCustomVoice0.6B, cachepilotoD066 | 2.498.437.120 | 2,327; modelo, no retirar |
| Kokoro archivos delcache | 329.342.976 | 0,307; protegido |
| OpenVoice/Melo modelos | 339.501.056 | 0,316; parado pero protegido |
| Piper modelos | 76.775.424 | 0,072; protegido |
| Datos productivos Voicebox completos | 84.340.736 | 0,079; incluyenPiper/perfil/historial |
| Grabaciones originales privadas | 5.361.664 | 0,005; protegido |
| Audios productivos generations | 1.298.432 | 1,24MiB; protegido |
| Caché de datos Voicebox | 1.433.600 | 1,37MiB; puede contener prompts, no borrar |
| Trabajos/muestras OpenVoice | 6.193.152 | 5,91MiB; conservar muestras |
| PilotoD072 completo | 135.782.400 | 0,126; incluye referencia privada protegida |
| /tmp y/var/tmp | 61.440 | Insignificante; no limpieza ejecutada |
| LogsDocker, suma archivos de log | 723637 | DentroDocker; no sumar otra vez |
| Docker namedvolumes | 0 | 0volúmenes; los datos son bindmounts |

HF usa symlinks snapshot→blobs: no sumar tamaño lógico siguiendo cada enlace,
ni borrarblobs manualmente. `du` del directorio incluye metadatos/refs; recuento de
archivos model_files puede variar unosKiB respecto al árbol completo. Las imágenes
incluyen dependenciasPyTorch, no son solo pesos HF. DiscosDocker/BuildKit comparten
capas: **18,64GB de imágenes +11,2GB de cache no son29,84GB recuperables**.
Los13 contenedores parados representan~5,70MB de writable layers, no GiB.

### Imágenes Docker, información del Engine

Size incluye contabilidad del Engine/containerd; Unique=Size−SharedSize es estimación
del Docker actual, no promesa de espacio ext4 liberado. No sumar filasSize completas.

| Imagen | Size GiB | Unique GiB | Contenedores referenciándola |
|---|---:|---:|---:|
| `local/qwen-c:d072` | 0.820 | 0.676 | 1 |
| `local/voicebox:openvoice-d071` | 4.992 | 1.209 | 0 |
| `local/voicebox-openvoice:d071` | 2.929 | 2.786 | 1 |
| `local/voicebox:8af7efe62fab-personal-d069` | 4.982 | 1.198 | 1 |
| `local/voicebox:8af7efe62fab-piper-d068-r2` | 4.981 | 1.198 | 1 |
| `local/voicebox:8af7efe62fab-piper-d068` | 4.981 | 1.200 | 1 |
| `local/voicebox:8af7efe62fab-bf16-sdpa-d066` | 4.826 | 1.131 | 7 |
| `local/voicebox:8af7efe62fab-cpu-d063` | 4.826 | 1.131 | 0 |
| `python:3.10-slim-bookworm` | 0.190 | 0.046 | 0 |
| `ghcr.io/google/cadvisor@sha256:b8e7d1093144fd088f425ff003d75a4aa405de075db78dae3bc563730b1bd07a` | 0.099 | 0.099 | 1 |
| `nginx:alpine` | 0.074 | 0.074 | 1 |

ProducciónD069 yrollbackR2/originalD063 se conservan. OpenVoice rechazado yQwenC
no validado están parados. `test-nginx` sigue activo desde eltemplate; no se declara
inútil ni se para por su nombre. Confirmar dependencias antes de proponer retirarlo.

## Recuperación propuesta A/B/C/D — sin ejecutar

**A. Claramente temporales, futura autorización necesaria.**

| Recurso | Bytes candidatos | GiB potencial |
|---|---:|---:|
| BuildKit no compartido, no en uso, metadataEngine | 4485183669 | 4.177 |
| APTlistas+cache | 478756864 | 0.446 |
| D072 solo build/ ybuild.tar.gz públicos | 134524928 | 0.125 |
| A total identificado | 5098465461 | 4.748 |

Exclusiones expresas deD072: private/,jobs/,referencia/transcripción/logs del ensayo.
CacheBuildKit: IDs exactos/tamaños/Shared/InUse en evidencia candidatos; verificar
otra vez antes de retirar, sin pruneglobal ni eliminar capas a mano. La reconstrucción
podría tardar más después, pero no requiere retirar imágenes operativas/rollback.
Si se recuperase todoA, libres pasarían aproximadamente7,06→11,80GiB; estimación,
no ejecución ni garantía deGC inmediata. Temporales vacíos del sistema no aportan.

**B. Antiguos archivables, condicionado a copia/restore y autorización.**
Catorce directorios de backups expandidos tienen un `.tar.gz` homónimo presente;
**no se ha demostrado igualdad entre cada pareja**. Su tamaño físico suma
7.198GiB. Conservar archivoscomprimidos ylatestbackup, yantes
de retirar una expansión comparar inventario/hashes/enlaces/SQLite, comprobar copia
fuera PVE y restauración. Algunos contienen modelos/voz: tratar como backup sensible,
no eliminar modelos productivos ni grabaciones independientes.

| Copia expandida candidata a archivo externo/revisión | GiB |
|---|---:|
| `d068-preserved-final` | 0.420 |
| `d064-before-catalog` | 0.308 |
| `d067-final` | 0.312 |
| `d068-final` | 0.419 |
| `d067-before` | 0.311 |
| `d068-before` | 0.312 |
| `d068-before-piper` | 0.383 |
| `d063-after-tts` | 0.307 |
| `d069-before` | 0.427 |
| `d067-before-recreate` | 0.311 |
| `d064-before-memory3072` | 0.310 |
| `d069-final` | 2.762 |
| `d066-before-qwen` | 0.310 |
| `d063-final-2048` | 0.307 |

A+B suman **11.946GiB potenciales**, no autorizados.
No sumar a esto los `.tar.gz` retenidos ni el total14,7GB debackups. Techoaproximado
libre19,00GiB si todoA+B resulta realmente retirables yGC libera lo esperado.

OtrosB: imágenes candidatasOpenVoiceapp/worker yQwenC podrían exportarse/verificarse
fueraCT antes de estudiar su retirada. Sus Unique delEngine suman~4,67GiB, pero
comparten referenciasBuildKit/capas: **no se añaden al totalA+B ni se prometen**.
Trece objetosDocker parados son revisión de metadatos/montajes, no liberar modelos
ni hacer `down -v`. Muestras, logs de prueba y pequeñas copiasdata se conservan;
no valen una retirada precipitada por el escaso ahorro.

**C. Necesarios para restauración o continuidad; protegidos.** ImagenD069 actual,
rollbackR2 yoriginalD063 con locks/recetas; backups comprimidos hasta retenciónacordada;
D071-before actual, D070-cancel, D069-acceptance; SQLite/data/profiles/generations,
private-originals,HF/Kokoro/Piper/Qwen/OpenVoice yreferenciaICL privada. Catálogo y
recibos de aceptación no sustituyen el WAV original ni unbackup íntegro.
Copia privada fuera PVE D07176.193.323B eimagenD0691.279.021.236B verificadas porSHA256
en D073; informes de restoreprevios presentes. No nuevo restore enproducción ni
retención universal validada para todos losbackups. Modelos no eliminables porD073.

**D. Requieren autorización antes de eliminar.** TodoA yB; cualquier imagen/objeto
Docker, backup, cache, logs, archivoexpandidos oservicioactivo. Es una categoría de
permiso, no otra bolsa debytes. C queda excluido de cualquier limpieza propuesta
sin nueva política explícita. Lista cerrada revisable, backup/restauración aplicable,
referencias cruzadas y verificación antes/después; no comandos destructivos ejecutados.

## Viabilidad Qwen según D065–D072

| Evidencia | Qué demuestra | Qué no demuestra |
|---|---|---|
| D065 | CPUoficialFP32 original; BF16 viable a niveloperador, mínimo pesos~2,339GiB TalkerBF16+codecFP32 | No modelo completo ni minuto |
| D066 | CustomVoiceBF16 carga3,81s; corteCT3,54GiB,0 OOM | No clonaciónBase niWAV |
| D067 | CustomVoiceBF16 con6GiB:600s sinWAV;CT4,22GiB/RSS3,03GiB | MásRAM no resolvió velocidad |
| D068 | Progreso real hacia códec, CT4,97GiB, cortePSI/swap | No minuto ni audio terminado |
| D069 | BaseBF16/SDPA:6,40s/106,86s,CT5,18GiB,HWM4,68GiB, vozaceptada | No minutoestable |
| D070 | ~20min largo sinWAV; cancelAPI no matahilo; reinicioVoicebox recupera | No nuevo benchmarkcompleto |
| D071 | OpenVoice corto técnicamente produceWAV | Vozrechazada; no solución principal |
| D072 | BaseC INT8 carga5,738s;RSS3,697GiB/CT5,094GiB,0 OOM; cortehostPSI | NoWAV,RTF ni clonaciónusable |

**Memoria:** margen puntual para el pico D072 observado, sin ampliar627 ni host.
No garantiza el pico delcódec o minuto, etapas no completadas. D069HWM yD072RSS
muestreado tienen distinta metodología/texto: no vender una reducción porcentual
normalizada ni prometer ahorro completo INT8. CT627 sigue3CPU/7GiB/swap512MiB.
No conviene reducir procesos ajenos sin evidencia ni detenerlos para hacer caber
Qwen. Voicebox queda~sin modelo; OpenVoice/Qwenworkerparados. El procesoAPI y
monitorización son necesarios; test-nginx tiene consumo pequeño yroles porrevisar.

**Configuraciones inferiores enmemoria, solo hipótesis de siguienteexperimento:**
modelo Base0.6Búnico, hilos2, límiteestricto ycodificaciónICLprecalculada verificable;
segmentación secuencial puede reducir buffers de audio pero necesita validar
naturalidad/contexto. `--max-duration` acota generación, no recorta por sí solo elKV
inicial2048slots encontrado encódigo. KV inicial Talker224MiB para28capas/1024KVdim;
no hay knob validado aquí para reducirlo sinparche.

En commitCef339be, `tk_release_bf16` ofrece `QWEN_FREE_BF16=1` cuando prefillcuantizado
`QWEN_PREFILL_QUANT=1` y no se usa matmatBF16; comprueba capas completasINT8/Q4 y
rechazaQ6. Libera fusedgate_upBF16 y aplicaMADV_DONTNEED a proyeccionesmmap.
Podría evitar conservar representacionesduplicadas, pero no medir ahorro ni afirmar
compatibilidad óptimaAVX2 por inspección. El propio upstream clasificaFREE_BF16
como **palanca experimental fuera delregistro, no para despliegue**. MADV_DONTNEED puede reducirRSS sin liberar inmediatamente toda la caché física
contabilizada en el cgroup; no confundir ambos ahorros. No activada.
INT4 reduce ciertas matrices, no códecFP32, yrequiere verificarBase0.6B ycalidad;
xvector-only pierde condicionamientoICL yno es equivalente para fidelidadpersonal.
[Fuente fijada y límitesexperimentales](https://github.com/gabriele-mastrapasqua/qwen3-tts/blob/ef339be58a778b062e1c14382347964552eae007/docs/feature-flags.md),
[códigoTalker](https://github.com/gabriele-mastrapasqua/qwen3-tts/blob/ef339be58a778b062e1c14382347964552eae007/qwen_tts_talker.c).

**CPU:** i5-6500,4cores físicos/4threads,AVX2/FMA sinVNNI/BF16nativo/AMX. CT3vCPU
no son cores exclusivos; D075 precisa cpusetLXC0–2/cpu.max=max ycuotaDocker3CPU. D069RTFtotal16,70 enmuestra corta, D070largo bloqueado,
D072CPUobservada1,85cores sinWAV: hay cuello de cálculo/despacho/latencia plausible,
no probar saturación100% delhost ni extrapolar unminuto linealmente. PrefillBF16→
FP32+OpenBLAS ydequantINT8/FMA conservan trabajo considerable.

**GPU:** inventarioactual solo IntelHDGraphics530; no GPU CUDA discreta detectada.
No presupongo soporteiGPUIntel para estosbackends. Elbackend oficial muestra
CUDA/BF16 yFlashAttention2 en sus ejemplos; unaGPU compatible local oworkerGPU
remoto podría resultar más razonable si se exige narración en tiempos cortos,
pero no se ha medido VRAM, tiempo ni coste aquí. [Backend oficial](https://github.com/QwenLM/Qwen3-TTS#quickstart).
No recomendar compra, ampliaciónRAM ni modelo de GPU concreto sin benchmarkBase0.6B
con referencia real; remoto requiere permiso específico para enviar voz/textos,
servicio confiable ycondiciones de privacidad. Nada enviado fuera para inferencia.

## Estado final verificado y límites de la auditoría

Voiceboxhealthy, mismaimagenD069/ID/StartedAt/restarts queD072; ningúnreinicio.
APIperfiles conserva únicamenteEduardo — Mi VozUUID1fd00418; referencia8840f5e1 y
originalSHA256idénticos, permisos0600. SQLitequick_checkok; sin escrituras de datos.
Base/Kokoro/Piper descargados yno cargados porGET/models/status; módulosKokoro0.9.4
/Piper1.8.0 yhashmodelPiper verificados. WAVsdiagnósticosD072 legibles, últimoPASS
realKokoro2,58s/8,745s yPiper2,113s/2,029s. **D073 no realiza una generación nueva:**
funcionalidadreciente verificada por evidenciaD072 y disponibilidad actual de sus
artefactos, no una nuevaUAT/inferencia fingida. No modificarhistorial/API para probar.

59 targets UP; unwarningHostDiskFilling627FIRING esperado ysin resolver, porloque no
se declara monitorización completamente libredealertas. Losotros17LXCgestionados
sin cambios de configuración; los27hashesPVE coinciden conbaselineD072 yentre
snapshotsD073. No acciones sobre otrosLXC, recursos, DockerCompose ni pipeline.
No archivosremotos de auditoría desplegados: código enviado porstdin, resultados
privados fueradePVE; documentos/evidencias/receta de auditoría localesversionables.
No commit/push. SintaxisPython, enlaceslocales ygitdiff--check comprobados.

## Evidencias y siguiente paso

- [Memoria y tablaLXC](evidence/2026-11-11-d073-host.json).
- [Disco yDocker](evidence/2026-11-11-d073-storage.json).
- [ObservaciónPSI60s](evidence/2026-11-11-d073-pressure-observation.json).
- [Candidatos eidentificadores](evidence/2026-11-11-d073-candidates.json).
- [Preservación yreadiness](evidence/2026-11-11-d073-verification.json).

Scripts reproduciblesde lectura en `services/infra-voicebox/audit-d073/`; no comandos
prune/delete/restart ni carga de modelos. PropuestasA/B y revisiónCT618 no ejecutadas.
**Detenerse para revisión del propietario.** Siguiente: decidir alcance concreto de
recuperación deespacio y, separadamente, diagnóstico/corrección autorizada de presión
localCT618 antes de evaluar otra pruebaQwen. No extender D073 como permiso de cambios.
