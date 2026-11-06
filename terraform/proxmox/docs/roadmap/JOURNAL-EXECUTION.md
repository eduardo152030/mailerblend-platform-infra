# Fase 4 — ejecución Journal API/DB

Autorización D-019, 2026-11-02 (Europe/Madrid). Procedimiento:
[JOURNAL-625-626](JOURNAL-625-626.md). Alcance exclusivo exporters CT 626→625;
CT 625 solo empezó después de PASS técnico e independiente de CT 626.

## Resultado técnico final

**Ambos CT PASS.** Aceptación técnica formal del propietario recibida D-020; exporters DONE — Accepted.
La cadena CPU con Prometheus/Telegram sigue pendiente de P0.

| CT | Observación | Delta CPU Node / cgroup padre, segundos | Pico RAM Node / cAdvisor | RAM LXC disponible mínima |
|---|---|---|---|---|
| 626 | PASS; 20:07:16–20:17:16 CET, 21 muestras / 600.960 s | 6.283826 / 6.275685 | 8.98 / 20.52 MiB | 1742.14 MiB |
| 625 | PASS; 20:18:10–20:28:10 CET, 21 muestras / 601.019 s | 8.139872 / 8.056124 | 9.02 / 20.96 MiB | 1783.11 MiB |

En ambos: 2 CPU / 2147483648 bytes RAM; CPU cgroup textfile, sin contador físico
nativo; cuatro contenedores Docker activos con CPU/RAM e identidades contrastadas.
OOM/oom_kill/high=0 antes y después; PSI de memoria avg10/60 muestreado máximo 0%.
Cero reinicios automáticos. Cuotas Node 48 MiB / 0,20 CPU y cAdvisor 128 MiB / 0,50 CPU.
Máxima CPU media entre muestras: Node ~0,39%, cAdvisor ~0,78% de una CPU, dentro de cuotas.
Swap residual API ~85,14→84,60 MiB; DB ~64,82→64,54 MiB. No se limpió ni amplió.
Memory.current máximo ~812 MiB API / ~772 MiB DB incluye caché/kernel, no solo RSS.
Los desfases máximos del contador CPU fueron ~0,224 s API / ~0,356 s DB,
compatibles con el writer de 5 s y lecturas no simultáneas.

Evidencias: [API 626](evidence/2026-11-02-journal626-execution.json),
[DB 625](evidence/2026-11-02-journal625-execution.json),
[inspección final de modelos, binds e identidades](evidence/2026-11-02-journal-final-runtime.json).

## Backups verificados

Run: `journal-20261102T190629Z`. Por CT, bundles en
`/mnt/storage/mailerblend-recovery/phase4/<run>/<CT>/` y
`~/.local/share/mailerblend-recovery/phase4/<run>/<CT>/` fuera del nodo.
Cada exporters-before.tar: 33832960 bytes; contiene imagen/config original y baseline.
El bundle posterior excluye el tar de imagen ya preservado y conserva applied/proof/code.
Los hashes completos, anidados y de entradas coinciden; carga de imagen y rollback
real verificados. Originales detenidos conservados como cadvisor-pre-phase4-626/625.

- CT 626: previo `ab31b752d274b45f9ac776003ae45ac1e809eebff5e31083ee9e3a94396040b2`; posterior `5a4eda04567bdd1615131c068f313ab5b84592963a8f4f7a81867ea45738df78`.
- CT 625: previo `4ce7eb0109ef53832cabdc42e4d3d7e046513cabf3fd4c9966d85a07e6332353`; posterior `08ece2bec61425f2901e9ac0c84182cc126bb0ad60085ef13243ed63c97279bf`.

## Comprobaciones del plano global y pruebas locales

[APIs finales](evidence/2026-11-02-journal-global-after.json): Prometheus/Alertmanager
ready HTTP 200, reglas actuales health=ok; Journal API y Web HTTP 200. Siguen
14 Node + 14 cAdvisor + 11 Blackbox, sin Journal ni job Grafana nuevo. No se recargó
ni modificó configuración global. Contadores de fallos Telegram sin incremento
respecto al punto inicial; **no se envió nueva prueba de entrega**. La prueba
D-021 exige ahora FIRING/RESOLVED en P0 y cada CT, más validación global final;
aún no se ejecutaron esas pruebas nuevas.

[Validación local y cierre](evidence/2026-11-02-journal-execution-validation.json):
**93 tests Python PASS**, 28 escenarios CPU promtool y suite previa PASS; configuración,
reglas, scripts y enlaces locales validados. La idempotencia real de ambos CT ya se
comprobó, no se presenta el mock como su sustituto.

## Operaciones y garantías

- Preflight real de asignación 2 CPU / 2 GiB, cgroups padre, recursos del nodo/CT,
  presión y margen de almacenamiento. Ninguna ampliación.
- Bundles declarativos transferidos y verificados por SHA. Directorios privados 0700,
  archivos de evidencia/backup 0600 y script del bind Node 0644.
- Configuración e imagen de cada cAdvisor original archivadas; tar/blobs/SHA y carga
  Docker comprobados antes de modificar exporters. Copia PVE y fuera del nodo,
  SHA del bundle y SHA anidado de la imagen contrastados. Node no existía previamente.
- Pull explícito de Node 1.10.2 y cAdvisor 0.60.6 por los digests aprobados; arquitectura
  amd64 y RepoDigests verificados. Apply usa pull never, sin build ni actualización implícita.
- Node/writer como nobody; CPU desde cgroup, capacidad 2, RAM desde LXCFS. No se expone
  node_cpu_seconds_total físico incorrecto. cAdvisor usa solo el socket adicional
  containerd aprobado, ro/sin crear ruta; conserva privilegios existentes.
- Rollback real por CT: originales mismos ID/imagen running y /metrics HTTP 200,
  Node ausente como en baseline; aplicaciones/identidades intactas. Reanudación de
  mismos candidatos; segunda aplicación conserva ID/StartedAt/restart counts.
- Observador externo contrasta CPU/RAM con Docker/cgroups/PVE, identidades, labels,
  frescura, aplicaciones, límites y OOM. Revalidación local independiente de las
  muestras y checksums de inputs/archivos antes de publicar los resúmenes.
- Configuración posterior archivada/verificada fuera del nodo. No se borraron
  contenedores, datos, volúmenes ni imágenes originales o candidatas.

No hubo modificaciones de aplicaciones, bases de datos, Proxmox, kernel, LXCFS,
Docker daemon, CT 624, CRM/EVA ni otros LXC. El espacio adicional usado corresponde
únicamente a imágenes, bundles y evidencias del cambio autorizado.

## Alcance de las pruebas de aplicación

API: GET :3000/health HTTP 200 y mismo cuerpo; PostgreSQL: pg_isready código 0.
Se comprobaron ID, imagen, configuración y StartedAt de las aplicaciones y test-nginx.
No se efectuaron login, pruebas de negocio ni comprobaciones de integridad SQL
completa. No se extiende la dispensa UAT histórica de F3.

Los reinicios manuales de exporters durante el rollback/reanudación eran deliberados;
la idempotencia se verifica después de reanudar. No confundirlos con reinicios
involuntarios o recreaciones de aplicaciones.

## Automatización y referencias

- [Ejecutor secuencial](../../scripts/rollout-journal-exporters.py): scope 626/625,
  gate PASS de API antes de DB, backup obligatorio y checkpoints privados; rechaza
  repetición ciega y otros CT. No hace rollback destructivo automático ante fallo.
- [Archivo posterior](../../scripts/archive-journal-exporters.py) y
  [revalidación/resumen](../../scripts/report-journal-exporters.py).
- [Rollout restante](PROGRESSIVE-ROLLOUT.md): R1–R7 preparados, sin ejecución autorizada.

Los resúmenes públicos no contienen Env, contraseñas ni datos de aplicaciones. Los
backups completos de configuración de exporters y logs operativos privados están
fuera de Git. Los manifests públicos acreditan las entradas desplegadas por hash.

## Límites y siguientes puertas

Tres Journal validados técnicamente no equivalen a F4 global completa. F4 exige
17 Node y 17 cAdvisor corregidos, incluyendo CRM/EVA, integración Grafana/sondas/reglas
y validación independiente de Telegram. El contrato CPU está aceptado y probado
localmente, **sin recarga de Prometheus en este lote**.

La RAM publicada de Docker incluye caché y no representa RSS; CPU de las tablas es
media entre muestras, no pico instantáneo. Memory.current incluye caché/kernel.
La swap residual se conserva; no se limpia ni se atribuye su origen sin línea base.
Los sockets ro permiten RPC: autorización actual solo 624/625/626, no otros CT.
Machine_* y límites Docker no sustituyen la capacidad del LXC.

El propietario aceptó técnicamente CT 626/625 (D-020). No equivale a demostrar
la cadena CPU corregida aún no integrada; ver INCREMENTAL-INTEGRATION.
Persisten healthchecks heredados, digest EVA y Nucleotecnológico. Ninguna de esas
incidencias se declara resuelta por este lote.
