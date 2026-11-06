# Piloto de exporters: únicamente CT 624

Estado técnico y medidas: [PILOT-624](../../../docs/roadmap/PILOT-624.md).
Autorización D-014, socket containerd D-015; no hay permiso para otros CT ni discovery.
No ejecutar deploy-cadvisor-all.sh, make deploy-all ni el Compose heredado.

## Archivos declarativos

- Base Node/cAdvisor: `../node-exporter/docker-compose.phase4.yml` y
  `../cadvisor/docker-compose.phase4.yml`.
- Cuotas de este piloto: node-limits.yml (48 MiB / 0,20 CPU) y
  cadvisor-limits.yml (128 MiB / 0,50 CPU); no cambian recursos Proxmox.
- cadvisor-containerd.yml: bind del socket existente ro, sin crear su ruta. Ro no
  restringe RPC. Solo está autorizado en CT 624.
- node-cgroup.yml + node-cgroup.sh: CPU real mediante textfile; no privilegios nuevos,
  UID nobody, lectura del cgroup ya montado y escritura solo en /tmp del contenedor.
  collector.cpu se desactiva para no publicar tiempo del núcleo físico compartido.
- Collector actualizado cada 5 s, con éxito y timestamp explícitos; no emite idle
  inventado. Formato y guardas probados con fixtures sin Docker.

## Preparación antes de aplicar

Usar un directorio privado fechado bajo `/opt/exporter-phase4-pilot/` dentro del CT.
El helper es `scripts/exporter-pilot-624.py`; copiarlo como pilot.py y las bases como
node.yml/cadvisor.yml junto con estos overlays. node-cgroup.sh debe ser legible por
nobody (0644) mediante su bind específico ro; el directorio permanece 0700.
El helper rechaza cualquier otro hostname/IP, modelo de aplicación, imagen mutable,
mount host escribible o incremento de privilegios no contemplado.

Primera ejecución: `snapshot --execute --directory DIR`, antes de cambiar exporters.
Captura IDs, configuración, imágenes y aplicaciones; guarda la imagen original por ID,
recorre/verifica su archivo y ensaya docker image load sin reiniciar servicios.
Conservar bundle en PVE y copia fuera del nodo, verificar SHA completo y SHA del
archivo de imagen incluido. Solo entonces guardar `external-backup-verified.json`
con offhost_verified=true y los hashes reales de baseline.json. No fabricar ese registro.
Preparar las imágenes por los digests de `../phase4-images.json`; no usar latest ni pull
implícito. Confirmar espacio, MemAvailable y margen del nodo/CT antes de cada operación.

No repetir snapshot sobre un baseline completo: permanece como punto anterior.
Reutilizar el directorio del piloto actual para los siguientes comandos, sin crear un
proyecto vacío que pueda adoptar o recrear exporters existentes.

## Aplicación actual e idempotencia

Desde el equipo de operación, utilizando el alias existente, el run aprobado es:

```bash
PILOT_DIR=/opt/exporter-phase4-pilot/pilot-624-20261102T161242+0100
ssh -o BatchMode=yes pve "pct exec 624 -- python3 $PILOT_DIR/pilot.py apply --execute --directory $PILOT_DIR --allow-containerd-socket --use-lxc-cgroup-cpu"
ssh -o BatchMode=yes pve "pct exec 624 -- python3 $PILOT_DIR/pilot.py check --execute --directory $PILOT_DIR --allow-containerd-socket --use-lxc-cgroup-cpu"
```

No ejecutarlos por rutina fuera del alcance autorizado. Son aplicables al modelo
actual revisado; un hash distinto se rechaza. La segunda ejecución conserva ID y
StartedAt. Los proyectos distinguen la revisión Node cgroup y cAdvisor containerd.
Los candidatos anteriores siguen detenidos, no eliminados. Las acciones explícitas
revise-node/revise-cadvisor preservan una revisión y requieren el estado previsto;
no son una autorización para actualizaciones futuras arbitrarias.

## Rollback del piloto

Para revertir este piloto dentro del alcance autorizado (el ensayo de rollback ya
estaba autorizado por D-014):

```bash
ssh -o BatchMode=yes pve "pct exec 624 -- python3 $PILOT_DIR/pilot.py rollback --execute --directory $PILOT_DIR"
```

El helper para ordenadamente candidatos y los renombra a *-held; detiene revisiones
rechazadas por su identidad conocida. Restaura el cAdvisor original por el mismo ID
sin recrearlo y deja Node ausente, tal como estaba en el baseline. Verifica aplicaciones
y respuesta web. No fuerza SIGKILL. Si falla una parada o una identidad no coincide,
se detiene; no usar rm -f para continuar.

Comprobar ID/imagen original, estado running y /metrics en .124:8085; esperar readiness
y contrastar con el baseline. El original 0.47.2 tenía cobertura Docker limitada: no
confundir restaurar ese punto con obtener las métricas modernas. Si falla su arranque,
conservar ambas revisiones y diagnosticar antes de otra intervención, sin tocar apps.
Nunca ejecutar down -v, borrar contenedores, volúmenes o datos, reiniciar Docker/LXC
ni restaurar backups de aplicaciones para revertir estos exporters.

## Observación y aceptación

El muestreador `scripts/sample-exporter-pilot-624.py` es de solo lectura y omite Env.
El observador `scripts/observe-exporter-pilot-624.py` se ejecuta en PVE con target
hardcoded 624; comprueba cgroups reales, Docker API, métricas, frescura, OOM/PSI,
identidades y web durante al menos 600 s. Guardar JSONL privado fechado y un resumen
sin secretos. No interpretar un punto posterior separado como muestreo continuo.

Ver [criterios y evidencias](../../../docs/roadmap/PILOT-624.md).
No adaptar alertas ni activar el discovery global automáticamente: el nuevo CPU
usa lxc_cpu_* y requiere revisión/compatibilidad antes del siguiente lote.
