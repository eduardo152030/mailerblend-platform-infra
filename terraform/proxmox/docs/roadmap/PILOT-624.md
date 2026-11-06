# Fase 4 — piloto CT 624 ejecutado

**Resultado técnico: PASS, limitado a Journal Web (CT 624). Fase 4 global: IN PROGRESS.**
Fecha: 2026-11-02, Europe/Madrid. Autorización del piloto D-014; socket containerd
aprobado expresamente en D-015; implementación de CPU real D-016.
El propietario acepta técnicamente estos resultados (D-017). Cualquier otro lote
y sus accesos requieren aprobación separada.

## Alcance y estado final

Node Exporter y cAdvisor activos exclusivamente en CT 624, con imágenes fijadas.
Journal Web y test-nginx conservan ID, imagen, configuración y StartedAt; HTTP 200
y hash de la respuesta iguales a la línea base. No se tocaron bases de datos,
CRM/EVA, kernel, configuración LXC/Proxmox, Docker daemon ni discovery global.
Se mantienen 1 CPU, 512 MiB RAM, 512 MiB swap y disco existente de unos 50 GiB.
El filesystem tenía ~46 GB disponibles; no hubo ampliación ni limpieza.

La validación cubre disponibilidad HTTP y preservación de los procesos/configuración,
no pruebas de usuario o todos los flujos funcionales del frontend. La dispensa UAT
de F3 no se extiende ni se usa como evidencia de este piloto.

## Imágenes y consumo

- Node Exporter **1.10.2**:
  `prom/node-exporter@sha256:3ac34ce007accad95afed72149e0d2b927b7e42fd1c866149b945b84737c62c3`.
- cAdvisor **0.60.6**:
  `ghcr.io/google/cadvisor@sha256:b8e7d1093144fd088f425ff003d75a4aa405de075db78dae3bc563730b1bd07a`.
  Manifest amd64: `sha256:bd7c00644d65e6c9fc2c151cab70d2e86d7fe3e0182cfb9863120ec2e017cf01`.
- Original cAdvisor **0.47.2**, imagen `sha256:e6c562b5e983f13624898b5b6a902c71999580dc362022fc327c309234c485d7`,
  conservado detenido como `cadvisor-pre-phase4-624`. No se utilizó latest.
- Docker Engine 29.0.2 existente; no se actualizó ni reconfiguró.

| Exporter | Pico RAM muestreado* | Límite RAM | Máxima media CPU entre muestras* | Cuota CPU | Reinicios automáticos |
|---|---|---|---|---|---|
| node_exporter | 8.78 MiB | 48 MiB | 0.358% | 0.20 CPU | 0 |
| cadvisor | 22.02 MiB | 128 MiB | 0.207% | 0.50 CPU | 0 |

*RAM de Docker incluye memoria/caché del cgroup; no es RSS. CPU es promedio entre
muestras, no un pico instantáneo. Los límites protegen las aplicaciones y no amplían
recursos del CT. Node y el writer textfile funcionan como **nobody (UID 65534)**.

RAM disponible LXC mínima muestreada: **271.93 MiB**.
Memory.current máximo: 482.26 MiB, que incluye caché/kernel;
no interpretarlo como memoria anónima no recuperable. La lectura posterior mostró
~85 MiB anon, ~244 MiB file y ~129 MiB kernel. Swap residual observada:
**49.72 MiB**, igual al inicio y final de la ventana;
no se ha puesto a cero ni se atribuye su origen sin línea base anterior de swap.

## Hallazgos que cambiaron el candidato

### CPU: procfs correcto para capacidad no bastaba para uso

La ruta /host/proc corrigió MemTotal y número de CPU, pero la CPU temporal seguía
siendo la del núcleo físico asignado y compartido. En 20,104 s, Node sumó 3,050 s
frente a 1,306 s del cgroup real. Se rechazó esa variante; [evidencia inicial](evidence/2026-11-02-pilot624-cpu-initial.json).
No se modificó LXCFS global ni sus opciones. El proceso observado continúa siendo
`/usr/bin/lxcfs /var/lib/lxcfs`; no se afirma que una opción concreta resuelva el caso
sin un ensayo independiente.

La solución del piloto usa **el mismo Node Exporter** y un collector textfile sin
privilegios adicionales. Lee /host/sys/fs/cgroup/cpu.stat (vista real del LXC ya
montada ro), escribe atómicamente solo en /tmp del propio contenedor cada cinco
segundos y publica:

- `lxc_cpu_usage_seconds_total`, `lxc_cpu_user_seconds_total`, `lxc_cpu_system_seconds_total`.
- `lxc_cpu_capacity_cores`, `lxc_cpu_collector_success`, `lxc_cpu_collector_timestamp_seconds`.
- Etiquetas `ct_id="624"`, `resource_scope="lxc"`, `cpu_source="cgroup_v2"`.

Se desactiva collector.cpu: **no se publica node_cpu_seconds_total incorrecto ni se
inventan tiempos idle**. Se mantienen las métricas RAM/filesystem de Node desde LXCFS.
El writer falla cerrado si faltan contadores; el control de calidad exige éxito,
antigüedad <=15 s y ausencia de error del collector textfile.

Capacidad contrastada con Proxmox/LXCFS: **1 CPU y 536.870.912 bytes de RAM**.
CPU consumida durante la ventana: Node **6.274854 s**;
cgroup Proxmox **6.265953 s**.
Mayor desfase absoluto observado entre el contador publicado y el cgroup:
**0.257 s**, compatible con actualización cada cinco segundos.
La diferencia máxima de MemAvailable frente a /proc fue 3.98 MiB
entre lecturas no simultáneas, sobre la misma capacidad de 512 MiB.

### cAdvisor: API containerd necesaria

El primer candidato arrancaba healthy pero no registraba Docker: faltaba
`/run/containerd/containerd.sock`. Se ejecutó rollback y se solicitó la aprobación
prevista por la condición de seguridad. Tras D-015 se añadió únicamente ese bind ro,
con create_host_path=false. Ro no restringe los métodos RPC; es una superficie sensible.
No se añadió /dev/kmsg, seccomp unconfined, capabilities o privilegios nuevos del CT.

Con ese acceso se obtienen CPU/RAM para los **cuatro contenedores activos**, incluyendo
las dos aplicaciones y los exporters, con ID e imagen correctos. Compose project/service
identifican la web de Journal; el ID del contenedor distingue cada instancia.
Los originales/candidatos detenidos se conservan, sin exigir que aparezcan como activos.

## Contraste numérico Docker / cgroup / cAdvisor

Punto final de control: **2026-11-02T19:11:41.069093+01:00**. Valores de RAM en bytes y CPU en
segundos acumulados. Capturas no simultáneas y cAdvisor con housekeeping de 30 s:
no exigir igualdad byte a byte en procesos cuyo heap cambia durante la lectura.

| Contenedor | RAM cAdvisor / Docker / cgroup | CPU cAdvisor / Docker / cgroup |
|---|---|---|
| node_exporter | 8290304 / 7254016 / 8257536 | 3.436484 / 3.445127 / 3.480987 |
| cadvisor | 23674880 / 22118400 / 22183936 | 8.421799 / 8.431711 / 8.447069 |
| infra-journal-web-web-1 | 2097152 / 2097152 / 2097152 | 3.678208 / 3.678208 / 3.678347 |
| test-nginx | 606208 / 606208 / 606208 | 0.061853 / 0.061853 / 0.061853 |

Los límites de memoria de los exporters coinciden con 48/128 MiB. En las aplicaciones
sin límite Docker explícito, container_spec_memory_limit_bytes es 0: significa sin
límite propio, **no** ausencia del límite heredado de 512 MiB del LXC. No usar machine_*
de cAdvisor como capacidad del LXC: algunos datos de máquina/kernel siguen compartidos.

## Observación, idempotencia y aceptación técnica

Ventana periódica: **2026-11-02T17:06:09.759983+01:00 → 2026-11-02T17:16:09.746164+01:00**;
**21 muestras**, bucle de observación de **600.943 s**.
Hubo además un control posterior independiente a las **2026-11-02T19:11:41.069093+01:00**.
No se presenta el intervalo sin muestreo entre ambos como monitorización continua.
El control posterior conserva ID/StartedAt, contadores OOM y todos los gates.

| Criterio solicitado | Resultado |
|---|---|
| Node refleja recursos LXC | PASS: RAM/capacidad LXCFS y CPU real desde cgroup, sin contador físico engañoso |
| cAdvisor descubre Docker individual | PASS: cuatro activos, CPU/RAM e identidad/labels |
| Contraste con Docker/cgroups/Proxmox | PASS: valores, límites y fuente del CT comprobados |
| >=10 min estables | PASS: ventana de 600,943 s, 21 muestras, más control posterior |
| Sin nuevos OOM / presión significativa | PASS: oom/oom_kill/oom_group_kill=0; PSI avg muestreado máximo 0.00% |
| Journal Web operativo | PASS: HTTP 200, mismo cuerpo, aplicaciones sin cambios |
| Idempotencia | PASS: segunda aplicación final y check código 0, mismos ID/StartedAt |
| Rollback documentado/verificable | PASS: backup de imagen/config, carga verificada y ensayo real de restauración del original; originales preservados |

El contador memory.high se conserva: 1093 al inicio de la ventana,
1094 en el control posterior. No es un OOM; no se oculta ese incremento.
La presión durante preparación/carga tuvo muestras pequeñas (some avg60 ~0,11%);
la ventana final muestreada registró PSI avg=0 y ningún OOM.

## Backups y rollback

Run: `pilot-624-20261102T161242+0100`.

- CT: `/opt/exporter-phase4-pilot/pilot-624-20261102T161242+0100` (0700; metadata privada).
- PVE: `/mnt/storage/mailerblend-recovery/phase4/pilot-624-20261102T161242+0100`.
- Copia independiente: `~/.local/share/mailerblend-recovery/phase4/pilot-624-20261102T161242+0100/exporters-before.tar`.
- SHA-256 del bundle previo: `79b66ecf4f8cb8c83752d76a1eb6d3d39894367b3be5b269f589887cac687a07`.
- Imagen original archivada/verificada y cargada antes de modificar exporters; bundle
  externo contrastado por SHA y por el hash del archivo de imagen que contiene.
- Originales y candidatos rechazados conservados detenidos, sin rm ni borrado de datos.
- El ensayo de rollback recuperó el contenedor original con el mismo ID/imagen y
  mantuvo intacta la web. Después se reanudaron los candidatos ya existentes, sin
  eliminarlos ni reconstruirlos. La versión 0.47.2 conserva sus limitaciones de API:
  rollback devuelve la cobertura anterior, no una corrección de esas limitaciones.

El [runbook de ejecución](../../services/common/pilot-624/README.md) documenta la
aplicación y reversión acotadas. No ejecutar el Compose genérico heredado ni el script
all: pueden adoptar/arrancar contenedores renombrados o eliminarlos.

## Helper y pruebas

[exporter-pilot-624.py](../../scripts/exporter-pilot-624.py) exige hostname/IP CT 624,
capacidad suficiente, backup externo y modelos de un único exporter con imágenes
inmutables. Conserva los originales, compara aplicaciones y bloquea cambios implícitos.
Usa proyectos separados para revisiones: renombrar un contenedor no elimina sus
labels Compose y --no-recreate puede volver a adoptarlo. Los fingerprints incluyen
el contenido del script textfile y comparan mounts por contenido, no por orden.
No hay fallback a SIGKILL ni cambios de aplicaciones.

Pruebas locales: **81 tests** de monitoring correctos (incluidos guardas del helper,
proyectos por revisión, timestamps Prometheus y el collector cgroup), sintaxis shell
correcta y validación real por los controles del piloto. El parser distingue el valor
del timestamp opcional en cAdvisor; no convierte milisegundos Unix en RAM/CPU.

## Riesgos y siguiente paso

1. **No activar discovery/rollout todavía.** El contrato CPU usa lxc_cpu_*; las reglas
   actuales basadas en node_cpu_seconds_total deben adaptarse/probarse antes de recoger
   estos targets globalmente. Mantener umbrales/for vigentes no implica usar la fuente
   incorrecta. La actualización de dashboards también debe reconocer el contrato.
2. El socket containerd es sensible y su aprobación se limita a CT 624. Su política
   y los recursos deben revisarse explícitamente para cualquier lote posterior.
3. Los límites heredados y machine_* no se interpretan como límites propios Docker.
   Queda pendiente cobertura/alertas continua; este piloto fue observado directamente,
   no incorporado al Prometheus global.
4. Conservados swap residual, backups y contenedores: no hay limpieza automática.
5. Persisten healthchecks CRM/Focalboard, digest EVA y Nucleotecnológico, fuera de alcance.

**Recomendación:** revisar este resultado y el nuevo contrato CPU; preparar la
compatibilidad de reglas/validadores y un lote Journal API/DB (CT 626/625) con
preflight y rollback equivalentes. Ese lote requiere aprobación; no se ejecuta
ahora. CRM/EVA se mantienen fuera de los primeros lotes y de esta intervención.

Evidencias: [resumen](evidence/2026-11-02-pilot624-summary.json),
[muestras](evidence/2026-11-02-pilot624-metric-samples.json),
[inputs y backups](evidence/2026-11-02-pilot624-artifacts.json),
[pruebas locales](evidence/2026-11-02-pilot624-local-validation.json).

Actualización de seguimiento: [contrato CPU preparado](CPU-CONTRACT.md) y
[lote siguiente pendiente de aprobación](JOURNAL-625-626.md); sin cambios adicionales en CT 624.
