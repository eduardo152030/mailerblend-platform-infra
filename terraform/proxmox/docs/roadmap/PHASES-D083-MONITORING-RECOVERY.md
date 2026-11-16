# D083 — recuperación de monitorización tras reinicio

Seguimiento: 12 de noviembre de 2026, Europe/Madrid. Fases afectadas:
1. Monitoring Foundation; 2. Telegram Alerting & Blackbox Deduplication;
5. Alerting Optimization; 6. Grafana & Dashboards. Incidencia operativa, sin
reanudar rollout F4 ni modificar aceptación histórica. Recuperación central: DONE técnico; FIRING/RESOLVED aceptados.
Seguimiento cAdvisor618/623: TODO, sin estabilidad completa acreditada.

## Autorización y diagnóstico

El propietario solicita recuperar visibilidad de hosts y alertas tras reiniciar
PVE para ampliar memoria. Recuperación acotada de monitorización existente:
CT610 Prometheus/Alertmanager y CT616 Blackbox; lectura de Grafana611 y exporters.
Sin cambios de recursos, aplicaciones, DB, volúmenes ni commit/push.
SSH estricto explícito, known_hosts del propietario y BatchMode.

PVE y los LXC estaban activos. Prometheus recibió SIGTERM el 11nov17:30:40 UTC,
terminó con137 a17:30:51 UTC, OOMKilled=false; Alertmanager terminó correctamente
ese mismo minuto. PVE volvió con CT610/Docker a18:47 CET. Ambos servicios y
Blackbox616 seguían parados unas20horas después, con restart unless-stopped.
El SIGKILL final es compatible con agotar la ventana de parada, no prueba OOM.
No se demuestra quién originó las paradas ni el motivo exacto por el que Docker
conservó el estado detenido. Grafana seguía activo, pero sin backend Prometheus.
Los errores403 deTelegram hallados inicialmente eran históricos del2nov;
no se han confundido con el estado actual.

## Corrección ejecutada

[Recuperación versionada](../../scripts/recover-monitoring-after-reboot.py):
backup privado en cada CT `/root/monitoring-recovery-d083`, copia Compose
verificada por lectura; baseline de identidades, imágenes, mounts y políticas.
Solo reemplazo restart unless-stopped→always en Compose desplegado y recetaGit,
`docker update --restart=always` y arranque de los tres contenedores existentes.
No pull, recreación, cambio de targets, secretos, exporters, reglas permanentes
ni volúmenes. Imágenes/IDs/mounts preservados; segunda aplicación sin cambios de
StartedAt ni recreación. Comparación de mounts ordenada por destino: Docker no
asegura orden en inspect. Primer intento de comprobación idempotente falló por
ese orden; comprobación corregida y repetida correctamente, sin nueva mutación.

Arranques UTC12nov: Prometheus13:43:17, Alertmanager13:43:18,
Blackbox13:44:02. Políticasalways desplegadas en610/616 y preparadas enIaC.
No se ha reiniciado PVE/Docker para ensayar otro arranque real.

Rollback de política: restaurar Compose privado previo y `docker update
--restart=unless-stopped` sobre los nombres exactos correspondientes. No parar
servicios ni restaurar/borrar datos para revertir una política de arranque.
No se ha realizado restauración TSDB, porque no fue necesaria; configuración
recuperable y datos originales se conservaron en sus volúmenes existentes.

## Verificación

Prometheus/Alertmanager ready200, promtool válido (10ficheros), amtool válido.
Grafana DBok, datasourceOK y consultas desde proxy Grafana con18hosts,
18CPU LXC y18cAdvisor en comprobación puntual. Fleet yDetails provisionados.
[Resultado Grafana](evidence/2026-11-12-d083-grafana.json).

[Prueba versionada](../../scripts/test-monitoring-recovery.py) basada en
`lxc:cpu_usage:percent{ct_id="610"}`, umbral de ensayo>=0, for30s, sin carga.
Recorrido exporter→Prometheus→regla→Alertmanager→Telegram. FIRING yRESOLVED
confirmados expresamente por el propietario en esta conversación. Tres envíos
aceptados y cero fallos: pruebaFIRING, alerta realCRM y resolución de prueba.
La regla se resolvió con condición<0 y se retiró después, validando promtool
antes de cada SIGHUP; Prometheus conserva ID/StartedAt/RestartCount0.
No POST directo aAlertmanager ni mensaje directo al bot para simular la cadena.

[Observación](evidence/2026-11-12-d083-observation.json): muestras30s,
CPU18 ycollectors frescos/correctos. Hay timeouts intermitentes10s decAdvisor
618/623; no atribuirlos automáticamente al reinicio ni declarar estabilidad
completa si persisten. Consultas directas posteriores responden, sinrestarts. CT618 dio0,596/1,243/8,993/33,040s; CT6230,927/1,911/1,314/0,944s.
La observación180s/7muestras tuvo timeouts de618 alinicio y623 enmuestras3/7;
noPASS deestabilidadglobal. Timeout de33s no se soluciona elevando a25s el
timeout deljob30s: no se cambió lacadencia ni se ocultó la anomalía.
Node18,CPU18,Blackbox19 ycadenaTelegram sí recuperados; detalleDocker mantiene
un pendiente acotado de latencia en estosdosCT.

## Riesgos y siguientes pasos

`crm-api` enCT618 está realmente parado; ApplicationContainerMissing FIRING.
Se diagnostica y notifica, sin intervenir aplicaciones dentro de esta solicitud
de monitorización. Budibaseapp/DB siguen activos; esto no acredita salud deCRMAPI.

Prometheus yAlertmanager comparten hostPVE: no pueden notificar mientras todo
elhost está apagado. Propuesta pendiente, no desplegada: watchdog externo aPVE
para disponibilidad dePrometheus/Alertmanager ylatido periódico. No es suficiente
una regla local para cubrir la caída total del propio sistema de alertas.

Disco610≈81% utilizado/1,8GiB libre al inicio; sinlimpiezas ni cambios deretención.
No afirmar que cambiar restart garantice toda recuperación futura: reboot real
no ensayado yla causa interna deDocker no quedó demostrada.

## Cierre de esta recuperación

12nov14:50 CET (13:50 UTC): tres contenedores originales activos, sin cambios
de imagen/mounts, RestartCount0 y políticasalways. Node18/18, CPU18, Blackbox19/19;
cAdvisor17/18 enesta última lectura (618timeout), incidencia intermitente también623.
Reglas0errores, última recarga correcta, prueba retirada,3envíos/0fallosTelegram,
FIRING/RESOLVED recibidos. [Evidenciafinal](evidence/2026-11-12-d083-final.json).
Compilación Python, enlaceslocales ygit diff --check PASS; diffs propios revisados,
archivosajenos preservados, sincommit/push. Elhueco demétricas durante laparada
no se rellena porarrancarPrometheus; no se promete recuperar datos no recogidos.
Siguiente: seguimiento específico de latencia618/623, recuperaciónCRMAPI separada
y propuesta dewatchdogexterno. No se declara resuelta la latenciacAdvisor.
