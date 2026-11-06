# Fase 4 — lote Journal API/DB preparado

Estado: **DEPLOYED / TECHNICALLY VALIDATED** (D-019). 2026-11-02, Europe/Madrid.
El plan original queda como procedimiento; aprobación recibida para 626→625 y sockets.
Resultados reales en [JOURNAL-EXECUTION](JOURNAL-EXECUTION.md); este archivo conserva el procedimiento.
Tareas F4-10 (compatibilidad local) y F4-11 (lote). El propietario acepta técnicamente
CT 624 (D-017). Esa aceptación no autoriza otros LXC ni el discovery global.

## Alcance propuesto para aprobación

**Orden: API CT 626 primero; DB CT 625 después de aceptar el control del primero.**
Solo instalar Node Exporter y sustituir conservando el cAdvisor anterior. No tocar
aplicaciones, bases de datos, volúmenes, CRM/EVA, otros CT, recursos, kernel, LXCFS,
Docker daemon ni Prometheus/Alertmanager en producción. No ejecutar deploy-all,
deploy-cadvisor-all ni deploy-prom para este lote.

D-019 concedió aprobación específica para el bind de `/run/containerd/containerd.sock`
en **ambos CT**, ro y create_host_path=false. Existe en los dos y su montaje
ya se aplicó/verificó durante D-019. **Ro no restringe RPC**; el acceso es sensible. Se mantienen los
privilegios cAdvisor ya existentes y sus binds revisados, sin dispositivos/capabilities
nuevos. Node/writer son nobody, sin privilegios, con bind host ro. El permiso D-015
solo cubría CT 624. Si cambia la topología/socket o se requieren privilegios nuevos,
detenerse y consultar; no crear sockets ni rutas ausentes.

## Recursos y diagnóstico real

Snapshot **previo al despliegue**, aproximadamente 19:50 CET. Las cifras/cache de
esta sección son históricas; el resultado actual está en JOURNAL-EXECUTION. [Preflight](evidence/2026-11-02-journal-batch-preflight.json)
y [capacidad/imágenes](evidence/2026-11-02-journal-batch-capacity.json).

| CT | Asignado | RAM disponible muestreada | Disco disponible | Estado aplicación |
|---|---|---|---|---|
| 626 API | 2 CPU / 2048 MiB / 512 MiB swap | ~1817 MiB | 46,58 GB decimales | GET :3000/health HTTP 200 |
| 625 DB | 2 CPU / 2048 MiB / 512 MiB swap | ~1857 MiB | 46,51 GB decimales | pg_isready local código 0 |

PVE tiene ~8,86 GiB MemAvailable en esta captura. Almacenamiento libre para copias:
~1,46 TB en /mnt/storage del nodo y ~982 GB en el equipo de operación. Las imágenes
nuevas no están cacheadas; cada original ocupa ~33,8 MB antes de considerar formato
y overhead del archivo. En ese preflight no se descargaron ni archivaron imágenes; sí se hizo posteriormente
durante el despliegue autorizado. Ambos usan cpuset 1-2,
CPU.max sin cuota adicional en el cgroup padre y RAM padre limitada a 2 GiB.
**CPU asignada no significa CPU física exclusiva**; se comparte con otros CT.
Las vistas internas memory.max muestran max: la fuente de límites es el padre
`/sys/fs/cgroup/lxc/<CT>` en PVE, no ese max interno. CPU.stat era legible como nobody
y sus contadores correspondían al padre; la tasa de exporters ya se contrastó
durante D-019, con evidencia en JOURNAL-EXECUTION.

Ambos registran cero OOM/oom_kill y PSI de memoria actual 0. Hay swap residual
(~74 MiB DB / ~94 MiB API); no se limpia ni se atribuye su origen. Los contadores PSI
acumulados no son presión actual. Revalidar margen/PSI del nodo y CT antes de cada paso.

Cuotas por CT: Node **48 MiB / 0,20 CPU**, cAdvisor **128 MiB / 0,50 CPU**;
176 MiB y 0,70 CPU combinados, dentro de 2 GiB/2 CPU. Son techos, no consumo esperado.
El piloto observó ~9/~22 MiB; no se extrapola como garantía a API/DB.
Gate propuesto: >=512 MiB MemAvailable, >=1 GiB libre **además** del tamaño estimado
de archivos de imagen/config; PVE y copia externa con margen para ambas copias.
Abortar ante OOM nuevo, presión significativa, falta de espacio o cambio de asignación.

## Imágenes, IaC y preparación reproducible

Mismos digests aceptados de CT 624:

- Node 1.10.2: `prom/node-exporter@sha256:3ac34ce007accad95afed72149e0d2b927b7e42fd1c866149b945b84737c62c3`.
- cAdvisor 0.60.6: `ghcr.io/google/cadvisor@sha256:b8e7d1093144fd088f425ff003d75a4aa405de075db78dae3bc563730b1bd07a`.
- Original en ambos: cAdvisor 0.47.2, ID de imagen
  `sha256:e6c562b5e983f13624898b5b6a902c71999580dc362022fc327c309234c485d7`.

[Generador local](../../scripts/prepare-journal-exporters.py) produce bundles acotados:

```bash
python3 scripts/prepare-journal-exporters.py --ct 626 --output /tmp/journal-exporter-preparation/626
python3 scripts/prepare-journal-exporters.py --ct 625 --output /tmp/journal-exporter-preparation/625
```

Contienen pilot.py, bases/overlays, node-cgroup.sh específico de hostname/CT/2 CPU,
sample.py, observe.py y manifest.json con hashes. La generación repetida es idéntica;
rechaza otros CT y directorios con baseline/applied. Reutiliza el helper aceptado por
hash, **sin modificar los ocho inputs desplegados de CT 624**. En el nuevo writer se
rechazan también contadores malformados/negativos. No se publican tiempos idle.

El helper generado comprueba hostname/IP, 2 CPU/2 GiB, aplicaciones/configuración,
modelos solo-exporter, digests, pull_policy=never, mounts ro, cuotas y flags explícitos.
No elimina contenedores, no hace build/pull implícito y rechaza recreaciones/model drift.
Se renderizaron cuatro modelos Compose por stdin usando los Compose existentes de
625/626, sin escribir archivos remotos ni ejecutar up. Esa prueba fusionó bases y
overlays localmente; el helper ejecutará nuevamente el render real con los archivos
separados antes de aplicar. [Evidencia](evidence/2026-11-02-journal-batch-compose.json).

## Procedimiento tras aprobación, por cada CT

1. Revalidar recursos, sockets, estado/identidades de apps, cgroup padre, endpoint API
   y pg_isready DB; registrar línea base privada. Detenerse si hay regresiones o drift.
2. Crear run fechado 0700 en `/opt/exporter-phase4-pilot/` del CT y staging privado
   PVE; transferir bundle/manifest y verificar cada hash. node-cgroup.sh 0644 para su
   bind individual; resto de evidencias privadas 0600. Usar alias pve existente.
3. Con flags revisados, ejecutar `snapshot --execute --directory DIR` mediante
   `pct exec <CT> -- python3 DIR/pilot.py ...`. Captura configuración completa solo
   de exporters y hashes/configuración de aplicaciones, imágenes/IDs/estado; archiva
   original con docker image save, verifica tar/blobs/SHA y ensaya image load sin
   detener servicios. Copia las configuraciones existentes de /opt/common.
4. Crear bundle privado de ese run en PVE, copiar fuera del nodo y verificar SHA del
   bundle y del archivo de imagen incluido. Comprobar lectura íntegra y manifest.
   Solo tras verificaciones reales escribir external-backup-verified.json con
   offhost_verified=true y archives idéntico a baseline.json. No inventar ese registro.
   Registrar ubicaciones/hashes en evidencia. **Backups ya creados/verificados: ver evidencia de ejecución.**
5. Si las imágenes exactas no están cacheadas, descargarlas explícitamente por digest
   dentro del alcance aprobado, registrar RepoDigests/ID y verificar arquitectura.
   No actualizar imágenes de apps ni etiquetas mutables. Nunca pull durante apply.
6. Ejecutar apply con `--execute --directory DIR --allow-containerd-socket
   --use-lxc-cgroup-cpu`. Renombra/conserva original `cadvisor-pre-phase4-<CT>`;
   únicamente parada ordenada del exporter (-t -1 con timeout del cliente, sin SIGKILL).
   No se detiene API, PostgreSQL ni test-nginx. Readiness con timeout configurable
   READINESS_TIMEOUT (120 s por defecto), reintentos y verificación de métricas reales.
7. En PVE, ejecutar `python3 observe.py --probe sample.py --output PRIVATE.jsonl
   --seconds 600 --interval 30` con los archivos del bundle del CT correspondiente.
   El target está fijado en el código; el probe corre por pct exec solo allí.
   Contrastará CPU/RAM contra cgroups/Docker/PVE, frescura, cuatro identidades,
   límites, labels, OOM/PSI y la aplicación, sin generar carga sintética.
8. Segunda aplicación con los mismos flags y check; comparar ID, StartedAt, restart
   counts y hashes de las aplicaciones y exporters. Deben conservarse. Registrar
   evidencia antes de pasar del CT 626 al CT 625.
9. Ensayar rollback y reanudación de esos mismos candidatos, conservando ambas
   revisiones, y completar la observación final. Copiar configuración posterior y
   evidencias fuera del nodo, verificar hashes y actualizar roadmap.

No hay backup de datos de aplicación como parte de este cambio: no se modifican sus
volúmenes ni su configuración. Los hashes/IDs y disponibilidad son criterios de
preservación, **no** una prueba SQL integral ni un ensayo de restauración de Journal.
Si fuese necesario intervenir datos/app/DB, se sale de este alcance y hay que consultar.
No hay parada prevista de API/PostgreSQL; puede haber un hueco breve de métricas
cAdvisor durante su sustitución. Presupuestar 30–45 min por CT con backups, descarga,
ensayo y diez minutos finales; el tiempo depende de red/almacenamiento.

## Rollback por CT

Usar el mismo DIR de snapshot y helper correspondiente:

```text
pct exec <CT> -- python3 DIR/pilot.py rollback --execute --directory DIR
```

El helper detiene ordenadamente los candidatos, los conserva como *-held, devuelve
el nombre y arranca el mismo ID del cAdvisor original; Node queda ausente como en
la línea base. Valida identidades/apps y endpoint. Confirmar original running,
imagen/ID y /metrics; v0.47.2 recupera la cobertura anterior limitada, no Docker moderno.
No restaurar datos ni ejecutar rm/down/prune. Si no hay parada ordenada, detenerse.
Para volver al candidato se reutilizan DIR y applied.json, mismos flags y hashes:
apply debe reanudar IDs previos sin recrearlos. Si falta una imagen, image load del
archivo verificado; si faltan contenedores, parar y revisar el backup antes de reconstruir.

## CPU, pruebas y criterios de aceptación

[Contrato CPU y consultas](CPU-CONTRACT.md). [Pruebas/evidencia local](evidence/2026-11-02-journal-batch-validation.json).
Las reglas/targets locales siguen sin desplegarse en Prometheus. La activación
posterior del discovery necesita un alcance y aprobación separados.

Aceptar cada CT solo cuando:

1. CPU capacity=2 y RAM=2147483648; uso/tasas cgroup contrastados con padre PVE.
2. Las cuatro identidades Docker activas tienen CPU/RAM recientes y labels útiles,
   sin confundir los límites Docker con el techo heredado LXC.
3. >=600 s y 21 muestras válidas, sin OOM nuevos, PSI significativo ni regresión;
   memoria disponible >=256 MiB durante observación. Registrar swap/high sin ocultarlos.
4. API HTTP 200 y DB pg_isready=0; aplicaciones conservan ID/imagen/config/StartedAt.
5. Backups CT/PVE/externos y carga de imagen verificados; rollback real y reanudación
   documentados; segunda aplicación conserva identidades, sin recreación/recarga.
6. Ningún cambio en otros CT, apps, datos o discovery global. Revisar resultados antes
   de aceptar cada servicio y antes de cualquier nueva expansión.

**Lote completado:** exporters 626→625, descargas por digest y socket exacto en ambos,
con todos los gates técnicos superados. Resultados técnicamente aceptados D-020; no incluye
reglas/discovery global ni da por completada F4.
