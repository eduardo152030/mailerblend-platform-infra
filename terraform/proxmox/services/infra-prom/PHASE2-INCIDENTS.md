# Fase 2: diagnóstico previo de incidentes reales

Este documento conserva el diagnóstico previo. La intervención posteriormente
autorizada y sus resultados están en [PHASE2-EXECUTION.md](PHASE2-EXECUTION.md).
Las referencias a acciones no ejecutadas describen el momento del diagnóstico.

## Fase 1 desplegada y contrastada

El 2026-11-02 se ejecutó el procedimiento autorizado con READINESS_TIMEOUT=120,
READINESS_INTERVAL=2 y las herramientas oficiales compatibles declaradas en Compose.
La copia previa remota es `/opt/infra-prom/.rollback/pre-telegram-20261102T091442Z.tgz`:
legible, 6052 bytes, permisos 0600. La copia conserva configuración/secretos, no
históricos de volúmenes; no debe compartirse ni copiarse a Git.

El resultado del procedimiento fue código 0. Prometheus y Alertmanager estaban ya
con la configuración correspondiente: se conservaron ID y StartedAt, sin recreaciones
ni SIGHUP. Esto confirma el comportamiento idempotente de esta ejecución.

Las APIs confirmaron 11 targets Blackbox, todos recogidos correctamente, exactamente
los declarados en `blackbox.json`, con ambas variantes de Nucleotecnológico. Las 13
reglas tienen health=ok. svc01 genera una instancia PublicUrlDown y Nucleotecnológico
una instancia CollectEndpointDown. Los endpoints siguen fallando: deduplicar no
resuelve la disponibilidad de la aplicación.

Al empezar, Telegram tenía 75 intentos y 56 fallos acumulados, sin incremento de
fallos en diez minutos. Se ha enviado la prueba controlada
`Phase1BlackboxVerification20261102` y su resolución por la API de Alertmanager.
El contador pasó de 75 a 76 tras FIRING y a 77 tras RESOLVED; los fallos permanecieron
en 56. La última ventana de diez minutos no registra fallos nuevos. Esto confirma
la aceptación de ambos envíos por Telegram; la visualización en el móvil no se
ha solicitado de nuevo y se distingue de esa comprobación automática.

## Acceso utilizado

Se revisaron los alias de `~/.ssh/config`. `pve` permite acceder al nodo existente y
consultar los LXC mediante `pct exec`; no se crearon accesos ni se modificó SSH.
El alias `infra-composable-crm` existe, pero falla durante el intercambio del banner.
No hay un alias EVA explícito en el archivo de configuración inspeccionado; el
acceso por la consola existente de Proxmox permitió completar el diagnóstico.
Las opciones de seguridad de los alias se conservaron tal como estaban configuradas.

## EVA: disco, CT 622

Observaciones reales:

- Root ext4 de unos 39,26 GiB, con 5,38 GiB disponibles, aproximadamente 13,7%.
- Inodos disponibles: aproximadamente 82%; el problema es capacidad en bytes.
- Journal persistente: aproximadamente 4 GiB, sin límites explícitos en la
  configuración efectiva inspeccionada.
- Directorio Docker de contenedores: aproximadamente 1,5 GiB.
- Configuración efectiva de logging json-file sin opciones max-size/max-file en
  los nueve contenedores inspeccionados.
- Docker informa 23,04 GB de build cache reclamable y 19,1 GB de imágenes. Estas
  cifras pueden compartir capas: no deben sumarse ni interpretarse como espacio
  que se pueda recuperar íntegramente con seguridad.
- Docker usa el image store de containerd. La medición física de
  `/var/lib/containerd` es 24.524.083.200 bytes (24,5 GB / 22,84 GiB): esta es la
  mayor fuente de ocupación medida. No basta con inspeccionar `/var/lib/docker`.
- `/opt/infra-eva-assistant-bot` ocupa aproximadamente 2 GiB.
- Focalboard aparece unhealthy; la API y PostgreSQL aparecen healthy. Es un
  incidente de aplicación independiente que requiere diagnóstico antes de cambios.

La causa del Warning no es una falsa alarma de inodos ni un exporter caído. Hay
acumulación de artefactos de construcción y logs con retención no acotada. No se
ha atribuido todo el consumo a un solo directorio sin medirlo ni se ha borrado nada.
El inventario declara 12 GiB pero el filesystem real es de unos 40 GiB: no se ha
modificado el inventario ni ejecutado Terraform para corregir esa discrepancia.

Preparado en el Compose existente:

1. Logging json-file con max-size=20m y max-file=5 para los siete servicios del stack.
2. El servicio de mantenimiento existente pasa a ejecutar solo `docker system df`;
   se retiran sus operaciones automáticas de prune de imágenes, contenedores,
   redes y volúmenes. Sigue conservando nombre, imagen, mounts y recursos.
3. Imágenes, comandos de aplicación, dependencias, puertos, datos y recursos del
   resto de servicios se han contrastado con la configuración anterior y conservado.

Esto limita crecimiento futuro; **no libera el espacio ya ocupado** ni limita el
journal del sistema. La rotación requiere recrear los contenedores correspondientes
y puede retirar logs antiguos: antes de autorizar ese rollout hay que preservar los
logs necesarios y acordar su retención. No ejecutar una actualización global con
pull de imágenes latest. Plantear un piloto por servicio usando la imagen instalada,
validar y continuar por lotes; PostgreSQL debe tener ventana y backup propios.
Los exporters comunes no se han cambiado (calidad de métricas pertenece a otra fase).

Quedan para aprobación separada: exportar logs que deban conservarse, retención del
journal y política de caché de construcción basada en edad/tamaño. No se ha preparado
ni ejecutado un borrado indiscriminado de volúmenes, logs o cachés.

## CRM: indisponibilidad por presión de memoria, CT 618

Observaciones desde el nodo Proxmox, sin depender del userspace bloqueado:

- CT running; cgroup.freeze=0. No está suspendido.
- RAM máxima 4 GiB y uso observado aproximadamente 4,27 GB, por encima de
  memory.high y muy próximo al máximo.
- Swap máxima 512 MiB, prácticamente agotada.
- PSI de memoria: some aproximadamente 99,7%, full aproximadamente 90%.
- Contadores acumulados: oom=8 y oom_kill=5. No se asume que todos ocurrieran hoy.
- Node Exporter/cAdvisor y SSH aceptan TCP, pero no responden HTTP/banner en el
  tiempo disponible. Puertos de control cerrados rechazan conexiones normalmente.
- `pct exec` también agota un timeout de diez segundos.
- Los cgroups de budibase-app y budibase-worker consumen aproximadamente 2,24 GiB
  y 1,51 GiB respectivamente. Los exporters consumen aproximadamente 7 y 13 MiB.
- Ambos Budibase usan `budibase/budibase:latest`, sin límites individuales. Son dos
  imágenes completas, no la combinación apps/worker dedicada de un despliegue dividido.
- Cada uno tiene un volumen anónimo distinto en `/data`; el Compose no representa
  explícitamente esos montajes que declara la imagen. No deben perderse al recrear.

Causa inmediata confirmada: saturación del límite de memoria/swap y reclamación
sostenida del LXC. La duplicación de stacks completos Budibase es el principal
consumidor observado. La ausencia de respuesta de los exporters no debe tratarse
como prueba de que están mal instalados ni resolverse ampliando el scrape_timeout.

Referencias oficiales:

- Imagen única con todos los componentes:
  https://github.com/Budibase/budibase/blob/master/hosting/single/README.md
- Topología dividida oficial:
  https://github.com/Budibase/budibase/blob/master/hosting/docker-compose.yaml

Preparado: `scripts/validate-budibase-topology.py`, invocado antes de Docker por el
script existente `services/infra-composable-crm/scripts/up-budibase.sh`.
Bloquea la combinación de worker monolítico y recreación sin preservación explícita
de /data. No conecta al servidor, no cambia imágenes ni detiene contenedores.
Con la configuración actual su salida no cero es deliberada y está probada.
No sustituye las comprobaciones previas de los demás mecanismos de despliegue.

No se ha elegido una migración de imágenes a ciegas: antes hay que respaldar ambos
volúmenes anónimos, identificar qué datos utiliza cada stack, versiones efectivas y
compatibilidad, y decidir entre una única instancia completa o componentes dedicados.
Un cambio simple de latest a otra imagen puede cambiar puertos, almacenamiento y
formato de datos. La recuperación del userspace necesita una intervención aprobada;
no se han detenido procesos, reiniciado el CT o cambiado RAM/swap.

## Reproducir el diagnóstico, solo lectura

```bash
ssh pve 'pct status 618; pct status 622'
ssh pve 'pct exec 622 -- df -hT /; pct exec 622 -- df -i /'
ssh pve 'pct exec 622 -- docker system df; pct exec 622 -- journalctl --disk-usage'
ssh pve 'cat /sys/fs/cgroup/lxc/618/memory.current; cat /sys/fs/cgroup/lxc/618/memory.max'
ssh pve 'cat /sys/fs/cgroup/lxc/618/memory.swap.current; cat /sys/fs/cgroup/lxc/618/memory.pressure'
ssh pve 'cat /sys/fs/cgroup/lxc/618/memory.events'
```

No volcar `docker inspect` completo, variables de entorno, configuraciones SMTP ni
archivos de credenciales a los logs del diagnóstico.

## Pruebas y límites de esta preparación

```bash
python3 tests/monitoring/test_phase2_safety.py
bash -n services/infra-composable-crm/scripts/up-budibase.sh
```

Se validó el Compose EVA con `docker compose config --quiet` a través de la consola
existente de Proxmox, enviando el YAML por stdin. No se copiaron archivos ni se
crearon/reiniciaron contenedores para esa comprobación.
Las pruebas locales verifican retención, ausencia de limpieza destructiva y bloqueo
antes de invocar Docker en la topología CRM insegura.

No se ha desplegado esta preparación. Las pruebas no afirman que el disco se haya
recuperado ni que el CRM vuelva a responder. Esas verificaciones quedan pendientes
del plan de recuperación y la aprobación de la Fase 2.

## Rollback y separación de fases

La configuración original EVA se conserva en el directorio local ignorado y
restringido `.rollback/phase2-*/eva-compose.yml`. Hasta que se apruebe el despliegue,
revertir estos cambios es únicamente una operación sobre el repositorio.
El preflight CRM se revierte junto con su invocación en up-budibase.sh; no altera datos.
El rollback de producción de Fase 1 está documentado en DEDUPLICATION.md y no se
ha ejecutado. No mezclar la aprobación del Blackbox desplegado con la de las
correcciones de almacenamiento o de la topología CRM.

## Planes ampliados pendientes de aprobación

La recuperación prioritaria de CRM y sus artefactos están en
[RECOVERY.md](../infra-composable-crm/recovery/RECOVERY.md). La propuesta separada
de EVA y su estimación de espacio están en
[STORAGE-PLAN.md](../infra-eva-assistant-bot/recovery/STORAGE-PLAN.md).
No se han ejecutado backups de producción, paradas ni cambios de recursos para prepararlos.
