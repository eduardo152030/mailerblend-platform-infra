# Fase 4 — auditoría técnica y candidatos locales

Documento histórico de la auditoría inicial, 2026-11-02, Europe/Madrid.
**En esa auditoría no hubo despliegues.** Posteriormente se autorizó y ejecutó
exclusivamente el piloto CT 624: ver [PILOT-624](PILOT-624.md). Las cifras de este
documento describen la línea base; el seguimiento actual está en CURRENT-STATUS.

**Auditoría inicial sin despliegues, reinicios, limpieza ni cambios de producción.** Las consultas utilizan APIs HTTP y los accesos existentes de Proxmox,
con scripts por stdin; no se modificó SSH global ni se instalaron archivos remotos.

## Resultado y causas

### Node Exporter: fuente incorrecta confirmada

Los 14 exporters existentes publican 4 CPU y 16.646.774.784 bytes de RAM, coincidentes
con el nodo físico. Los CT tienen asignaciones diferentes. Proxmox usa LXCFS
6.0.0-pve2: `/proc` leído directamente dentro del LXC ya muestra los límites correctos,
pero el `/proc` del contenedor Docker del exporter no usa esos archivos virtualizados.

Comprobación dentro del exporter CRM: `/proc/meminfo` muestra 16.256.616 KiB;
`/host/proc/meminfo` muestra 6.291.456 KiB y `/host/proc/stat` contiene dos CPU. En EVA,
`/host/proc` muestra 2.097.152 KiB y dos CPU. La opción existente `--path.rootfs=/host`
no cambia por sí sola la ruta procfs de esos collectors.

Candidato: [Node Compose](../../services/common/node-exporter/docker-compose.phase4.yml)
con `--path.procfs=/host/proc`, `--path.sysfs=/host/sys`, rootfs ro/rslave y filtros de
filesystem. **No se ejecutó el exporter con esos flags en producción.** El lock
[phase4-images.json](../../services/common/phase4-images.json) conserva los digests
instalados de cada servicio: conviven 1.10.2, 1.11.0 y 1.11.1; no se propone un downgrade
implícito. Para los tres Journal ausentes se propone la imagen 1.10.2 de la base
existente, cuya descarga/instalación necesita aprobación. `pull_policy: never` obliga
a preparar/verificar explícitamente la imagen antes de iniciar.

El cambio no convierte todas las métricas de kernel compartido en recursos exclusivos
LXC. El piloto debe contrastar límites, disponibilidad de RAM, tasas CPU y filesystem
con Proxmox/cgroups/LXCFS, no solo que /metrics responda.

### cAdvisor: healthy no equivale a contenedores visibles

Hay 17 cAdvisor instalados, todos v0.47.2; Prometheus solo recoge 14. Todos los endpoints
inspeccionados ofrecen una única serie raíz de memoria, sin CPU/RAM identificadas por
contenedor Docker. No se observaron errores de API en el tail acotado de logs; no se
presenta ese tail vacío como prueba de compatibilidad.

La incompatibilidad del cliente antiguo sí está establecida: Docker 29.0.2/29.1.3,
probe del CT 610 a `/v1.41/info` → HTTP 400, mínimo permitido 1.44. El código oficial
[v0.47.2](https://github.com/google/cadvisor/blob/v0.47.2/go.mod) usa el cliente Docker
20.10; [su inicialización](https://github.com/google/cadvisor/blob/v0.47.2/container/docker/client.go)
negocia desde ese cliente. Es un bloqueo concreto; no demuestra que sea el único
problema de nested cgroup/containerd.

Candidato [cAdvisor Compose](../../services/common/cadvisor/docker-compose.phase4.yml):
0.60.6 en GHCR, fijado por digest de manifest comprobado, cliente Moby moderno,
cgroup namespace del LXC, estado Docker/containerd ro, socket específico ro y solo
labels Compose permitidas. Se retiran collectors process/perf del candidato; no se
cambian kernel, Docker daemon, Proxmox ni la API mínima. Se mantiene privileged como
requisito a revisar en el piloto, sin añadir seccomp unconfined ni permisos al CT.
El socket ro **no** restringe por sí solo los métodos de la API Docker.

Referencias primarias: [release 0.60.6](https://github.com/google/cadvisor/releases/tag/v0.60.6),
[cliente actual](https://github.com/google/cadvisor/blob/v0.60.6/go.mod),
[montajes oficiales](https://github.com/google/cadvisor/blob/v0.60.6/README.md),
[flags](https://github.com/google/cadvisor/blob/v0.60.6/docs/runtime_options.md).
Binario oficial amd64 descargado solo en el equipo local, SHA-256 contrastado con el
digest del asset de GitHub y ejecutado únicamente con `--version` y los flags candidatos:
[resultado](evidence/2026-11-02-cadvisor-cli.json). No se arrancó un servidor ni se
probó la imagen dentro de LXC. La corrección de visibilidad queda pendiente del piloto.

### Cobertura, Journal y Grafana

[La matriz](phases/COVERAGE-MATRIX.md) muestra los 17 servicios individualmente.
Los tres Journal tienen Docker/cAdvisor y sus aplicaciones, pero no Node Exporter y
no aparecen en discovery actual. El generador no se había ejecutado para ese inventario.
Grafana responde en /api/health y /metrics con HTTP 200; existía grafana.json, pero
Prometheus no tenía job que lo leyera. No es necesario cambiar la configuración de
Grafana para este scraping, y no se han dado por resueltos sus dashboards.

Preparación local mediante [gen-prom-targets.py](../../scripts/gen-prom-targets.py):
17 Node, 17 cAdvisor, 1 Grafana y [3 Journal](../../services/infra-prom/config/targets/blackbox-journal.json).
Valida identidades duplicadas antes de escribir, usa rutas desde el repositorio y
produce resultados deterministas. IPs/VMIDs se derivan del inventario, no se repiten
en los [contratos](../../services/infra-prom/config/journal-probes.yml).

| Sonda nueva | Contrato real consultado | Equivalencia/cobertura |
|---|---|---|
| Journal web :8090/ | GET 200; módulo http_2xx_strict | Comprueba entrega de la web; no su integración con API |
| Journal API :3000/health | GET 200; módulo http_2xx_strict | Comprueba ese health endpoint; no todos los flujos ni una restauración SQL |
| Journal DB :5432 | Conexión TCP exitosa; módulo tcp_connect efectivo presente | Comprueba transporte; no autenticación, consultas o integridad de datos |

Son endpoints y capas distintos: no son duplicados equivalentes. No se retira ninguna
sonda aceptada; las 11 originales permanecen intactas, con sus dos variantes de
Nucleotecnológico. Prometheus candidato lee dos nombres explícitos, no un wildcard:
11 base + 3 Journal = 14. Las reglas InternalEndpointDown existentes cubrirían los
dos HTTP; el TCP no entra en esa regla y no tiene una alerta nueva en esta entrega.
Esa política y la vigilancia de series ausentes se revisarán en F5; no llamar a un fallo
TCP “aplicación caída” ni eliminar una comprobación por estar sana otra capa.

`vmid`/`collector_scope` son etiquetas nuevas locales. Pueden cambiar fingerprints
tras el despliegue. `up` conserva su significado de disponibilidad del collector.
La fuente del nodo físico PVE y contratos de aplicación adicionales siguen abiertos;
no se simula que la cobertura sea completa por declarar 17 targets.

## Entrega local y límites operativos

Se añaden templates **opt-in** `docker-compose.phase4.yml`; los Compose por defecto
anteriores no se sustituyen ni se ha cambiado un servicio remoto. `deploy-common.sh`
no selecciona estos candidatos automáticamente. El script heredado
`deploy-cadvisor-all.sh` usa rm -f y una versión divergente: **no usarlo para el piloto**.
No existe todavía un rollout F4 probado; preparar ese transporte con snapshots,
readiness, preservación y no-recreate forma parte del piloto aprobado, antes de aplicar.

El archivo Prometheus local sí contiene el job/targets candidatos: no ejecutar
`deploy-prom.sh`, `prom-reconcile` o `make deploy-all` durante esta revisión.
Especialmente, no cargar targets Node Journal antes de instalar sus exporters.
No reiniciar aplicaciones ni reducir los 6 GiB temporales de CRM para esta fase.

## Pruebas y criterios pendientes

- **54 tests** de monitoring correctos, incluidos 11 nuevos de F4: cobertura y
  determinismo, inventario duplicado, preservación de imágenes/sondas, TCP y rechazo
  de evidencia que solo ofrece HTTP 200 o datos globales.
- `promtool` 3.12.0: configuración candidata, 13 reglas y fixtures correctos.
- Compose candidato de Node/cAdvisor parseado con la herramienta existente, por
  stdin y `config --quiet`; no se ejecutó up/pull ni se escribieron archivos remotos.
- Syntax Python y diff revisados. Las herramientas actuales de validación siguen
  requiriendo instalación: eliminar la dependencia de /tmp continúa en F7.
- [Validador real](../../scripts/validate-phase4-evidence.py): devuelve **código 1**
  ante la producción actual, con 75 carencias de cobertura/calidad. Es el resultado
  esperado, no un despliegue fallido ni una prueba de fase completada.
- [Estabilidad](evidence/2026-11-02-stability.json): CRM/EVA conservan ID, imagen y
  StartedAt; contadores OOM=0 y valores PSI avg=0 en las muestras. Builder/ready CRM y API/UI EVA
  responden 200. No se realizó UAT, SQL de escritura ni prueba Telegram nueva.

Los [criterios completos de aceptación](phases/04-exporters-coverage.md) exigen datos
por contenedor, fuentes CPU/RAM correctas, 17/17, al menos diez minutos estables,
idempotencia, contratos por capa y aceptación tras despliegue autorizado. Un pase
futuro del validador automático cubrirá solo parte de esos criterios, no cerrará F4
por sí solo.

Resultados de validación: [resumen local](evidence/2026-11-02-local-validation.json)
y [última consulta API](evidence/2026-11-02-final-api-check.json). Esta última sigue
mostrando 14+14 scrapes, 11 sondas y solo CollectEndpointDown de Nucleotecnológico:
los candidatos no se han cargado accidentalmente.

## Siguiente paso propuesto — requiere aprobación

1. Revisar estos candidatos y concretar piloto en **Journal web CT 624**: tiene menor
   asignación y permite probar el caso de Node ausente sin tocar CRM/EVA. Revisar margen
   antes de iniciar; no ampliar recursos automáticamente.
2. Antes de solicitar aprobación de ejecución del piloto: preparar la captura de
   configuración/IDs/digests del cAdvisor original, verificar
   imágenes y espacio, preparar el helper de despliegue conservador con rollback y
   probar sus guardas. No eliminar el exporter original; no tocar aplicaciones.
3. Tras aprobación explícita, instalar Node y probar cAdvisor candidato solo en ese CT. Validar namespaces,
   métricas individuales frente a Docker/cgroup, consumo, etiquetas y segundo apply.
4. Con resultados aceptados, pedir/aplicar el alcance de rollout por lotes, Journal
   primero; CRM/EVA al final con su línea base y criterios de parada. No asumir que
   aprobar un piloto autoriza automáticamente el rollout completo.
5. Solo entonces recargar discovery/job Grafana/Journal mediante el procedimiento
   acotado de Prometheus y validar 17+17, 14 sondas y ausencia de regresiones.

Rollback futuro: detener limpiamente el candidato, conservarlo y devolver nombre/
configuración al exporter original detenido; retirar únicamente nuevos targets/jobs
si fuera necesario y validar el catálogo previo. No revertir recuperación CRM/EVA,
secretos Telegram, bases de datos o volúmenes. La implementación exacta y sus pruebas
deben estar revisadas antes de solicitar autorización de ejecución del piloto.

## Reproducir diagnóstico sin modificar producción

```bash
python3 scripts/audit-monitoring-runtime.py --output /tmp/phase4-runtime.json
python3 scripts/validate-phase4-evidence.py \
  --runtime-audit /tmp/phase4-runtime.json \
  --prometheus-url http://192.168.1.110:9090
python3 -m unittest discover -s tests/monitoring -p 'test_*.py'
```

El segundo comando falla deliberadamente hasta cumplir los criterios automáticos.
Para regenerar sin editar los candidatos del árbol, usar
`python3 scripts/gen-prom-targets.py --output-dir /tmp/phase4-targets`.
