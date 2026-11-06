# Alertas de infraestructura por Telegram

Preparación local. No desplegar hasta disponer de aprobación explícita.
No se necesita modificar Terraform, Grafana ni instalar otra plataforma.

## Secretos locales

El archivo real debe crearse en:

`/home/jainer/work/mailerblend-platform-infra/terraform/proxmox/services/infra-prom/.env`

Desde `terraform/proxmox`, ejecutar una sola vez si todavía no existe:

```bash
(umask 077; cp -n services/infra-prom/.env.example services/infra-prom/.env)
chmod 600 services/infra-prom/.env
```

Abrir ese archivo en el editor e introducir los valores, sin comillas ni `export`:

```dotenv
TELEGRAM_BOT_TOKEN=valor_introducido_solo_en_el_editor
TELEGRAM_CHAT_ID=identificador_numerico
```

No pegar el token en el terminal, URLs del navegador, capturas, chat o argumentos.
No ejecutar `set -x`, `cat .env`, `docker inspect` para buscarlo ni mostrar configuraciones
que contengan secretos. El archivo `.env` no se carga como variables del contenedor.

Verificar sin mostrar contenido:

```bash
git check-ignore services/infra-prom/.env
git ls-files -- services/infra-prom/.env
```

El primer comando debe mostrar la ruta; el segundo no debe mostrar nada.
La preparación y el despliegue rechazan un `.env` rastreado o con permisos abiertos.
Los archivos `.runtime/` y `.rollback/` también están ignorados.

## Obtener chat_id sin exponer el token

1. Abrir https://t.me/Codestacks_Bot y pulsar **Iniciar** o enviar `/start`.
2. Enviar un mensaje nuevo, por ejemplo `Configurar alertas`.
3. Introducir únicamente el token en `.env` por el momento y ejecutar:

```bash
python3 scripts/prepare-telegram.py --chat-id
```

El script comprueba la identidad del bot mediante `getMe` y consulta `getUpdates`.
No envía mensajes, no confirma ni elimina actualizaciones mediante un offset y no
imprime el token o las respuestas completas. Muestra solo IDs y tipos de chat.
Seleccionar el chat correcto y escribir su ID en `TELEGRAM_CHAT_ID` mediante el editor.
Para un grupo, añadir el bot y enviar un comando dirigido a él; el ID suele ser negativo.
No usar un bot compartido con otro consumidor de actualizaciones. Si existe un webhook
o no aparecen mensajes, verificar su integración antes de modificarla; este script no
elimina webhooks. Un bot nuevo dedicado a alertas evita ese conflicto.

## Preparación y validación

```bash
python3 scripts/prepare-telegram.py
./scripts/validate-monitoring.sh
```

Se requieren Python 3 y los binarios oficiales `promtool` 3.12.0 y `amtool` 0.33.0,
las mismas versiones que las imágenes fijadas. Se pueden indicar rutas mediante
`PROMTOOL` y `AMTOOL`. No se introduce una dependencia de Python adicional.

Durante la preparación se han descargado y usado en esta máquina:

```bash
export PROMTOOL=/tmp/mailerblend-monitoring-tools/prometheus-3.12.0.linux-amd64/promtool
export AMTOOL=/tmp/mailerblend-monitoring-tools/alertmanager-0.33.0.linux-amd64/amtool
```

Estas rutas son temporales. En otro equipo, obtener las mismas versiones de los
releases oficiales de Prometheus y Alertmanager y comprobar sus sumas publicadas.

El token se escribe en `.runtime/telegram_bot_token` y se monta solo lectura en
`/run/secrets/telegram_bot_token`. La configuración utiliza `bot_token_file` nativo.
El directorio local/remoto es 0700; el archivo montado es legible por el usuario
sin privilegios del contenedor. La configuración renderizada contiene el chat_id,
pero nunca el token. El `.env` no se copia al servidor.

El archivo versionado `config/alertmanager/alertmanager.yml` es la fuente de la
configuración: contiene un marcador de chat_id que el preparador sustituye. No debe
montarse directamente. Compose monta `.runtime/alertmanager.yml`.

## Desplegar únicamente tras aprobación

Desde `terraform/proxmox`, con las variables PROMTOOL/AMTOOL anteriores o herramientas en PATH:

```bash
./services/infra-prom/deploy-prom.sh
```

Para otro destino:

```bash
PROM_HOST=192.168.1.110 ./services/infra-prom/deploy-prom.sh
```

También `scripts/deploy-service.sh infra-prom <IP>` delega en este procedimiento.
No usar `make deploy-all` para esta migración: incluye cambios Terraform y otros servicios.
SSH y rsync usan explícitamente `$HOME/.ssh/known_hosts`, con
`StrictHostKeyChecking=yes` y `BatchMode=yes`, incluso si la configuración global
selecciona otro archivo. No se modifica la configuración SSH global. Verificar la huella del servidor
por un canal fiable y configurar known_hosts antes del despliegue. No desactivarla.

El procedimiento valida localmente, guarda una copia remota restringida, sincroniza
configuración, comprueba Compose y herramientas oficiales con las imágenes fijadas,
aplica Compose y espera readiness con reintentos. Compara ID y hora de arranque con
el estado previo: los contenedores creados o reiniciados no reciben SIGHUP. Los que
siguen ejecutándose solo se recargan si cambió el contenido de su configuración;
se comprueba la confirmación de recarga en las métricas y readiness de nuevo.
Compose no detecta cambios dentro de archivos bind-mounted. La sincronización usa
checksums y `--inplace` para mantener el inode de archivos montados individualmente.
Un despliegue repetido sin cambios no fuerza recreaciones ni envía señales.

El timeout por comprobación es configurable (por defecto 90 segundos) y el intervalo
de reintento es de 2 segundos. Por ejemplo:

```bash
READINESS_TIMEOUT=120 READINESS_INTERVAL=2 ./services/infra-prom/deploy-prom.sh
```

Un fallo termina con código distinto de cero y muestra el estado limitado de ambos
contenedores y sus últimas 80 líneas de logs con token y URLs ocultos. El error no
activa reinicios automáticos adicionales ni un rollback silencioso.

Conserva los volúmenes nombrados
y el proyecto Compose existente en `/opt/infra-prom`; no ejecuta `down -v`.
Antes de la primera ejecución confirmar que esa ruta y proyecto son los activos.
El backup remoto incluye configuración, no los volúmenes de históricos.

Pruebas locales del flujo de arranque/recarga, sin Docker ni acceso a servidores:

```bash
bash -n services/infra-prom/deploy-prom.sh scripts/apply-monitoring.sh
python3 tests/monitoring/test_deployment.py
```

## Comprobar en producción, después del despliegue autorizado

```bash
curl -fsS http://192.168.1.110:9090/-/ready
curl -fsS http://192.168.1.110:9093/-/ready
curl -fsS http://192.168.1.110:9090/api/v1/targets
curl -fsS http://192.168.1.110:9090/api/v1/rules
curl -fsS http://192.168.1.110:9090/api/v1/alerts
curl -fsS http://192.168.1.110:9093/api/v2/alerts
```

Tras al menos cinco minutos, comprobar en Prometheus:

```promql
count_over_time(up[5m])
rate(node_cpu_seconds_total{mode="idle"}[5m])
node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}
up == 0
probe_success == 0
increase(alertmanager_notifications_failed_total{integration="telegram"}[10m])
```

Esperar aproximadamente diez muestras por target sano en cinco minutos. Confirmar
scraping/evaluación de 30s, reglas con health=ok y alertas recibidas por Alertmanager.
Una métrica de entregas vacía antes de la primera notificación no demuestra éxito.
Revisar logs de forma controlada, sin compartir URLs ni datos sensibles.

### Prueba controlada: ejecutar solo en la etapa B autorizada

Enviar mediante POST a `/api/v2/alerts` una alerta `TelegramDeliveryTest` con labels
`severity=info`, `service=monitoring-test`, `instance=manual-test` y `job=manual-test`,
annotations `summary` y `description`, `startsAt` actual y `endsAt` 15 minutos después.
Esperar group_wait de 30 segundos y confirmar recepción FIRING en el chat correcto.
Enviar de nuevo exactamente los mismos labels y startsAt, con endsAt en el pasado.
Esperar hasta el siguiente group_interval (5 minutos) y confirmar RESOLVED.
No declarar validada la entrega hasta que el destinatario confirme ambos mensajes.
Comprobar ausencia de errores de entrega. Esta prueba no detiene servicios reales.

## Comportamiento y límites

- FIRING y RESOLVED, severidad, alerta, servicio/instancia, job, descripción,
  fechas explícitamente en UTC y fingerprint del incidente.
- Agrupación por alerta, servicio e instancia; espera 30s, cambios cada 5m y
  repetición a las 4h. Hasta cinco detalles por mensaje; los demás están en Alertmanager.
- CPU >90% durante 10m; memoria disponible <10% durante 5m; disco libre <15%
  durante 10m; Node Exporter/exporters inaccesibles durante 2m; sondas fallidas 2m.
- Reglas Docker sin series verificadas desactivadas; cAdvisor sigue vigilado por `up`.
- Se ignora la URL ficticia EDGE_FQDN_PLACEHOLDER sin borrar targets remotos.
- Los JSON Blackbox remotos antiguos no se eliminan. Con la Fase 1, discovery lee
  únicamente el catálogo `blackbox.json`; las variantes conservadas se agregan
  por incidente lógico. Ver DEDUPLICATION.md antes de desplegar esta migración.
- Los fallos de `.118`, exporters ausentes y visibilidad cAdvisor no se reparan con
  Telegram. Las métricas Node Exporter existen, pero queda validar el aislamiento de
  recursos LXC antes de interpretar sus umbrales como límites del contenedor.
- Sin Internet o con Telegram caído, no se garantiza entrega. Este cambio deja
  Telegram como receptor único; readiness no prueba la recepción de notificaciones.
- El aumento de frecuencia es 120x respecto a una hora: vigilar disco y memoria.

## Rollback

Antes de editar se guardó la configuración local original bajo `.rollback/<fecha>/`,
con permisos restringidos. Contiene la configuración SMTP antigua: no versionarla.
El despliegue guarda además `/opt/infra-prom/.rollback/pre-telegram-<fecha>.tgz`.

Después de autorización de rollback, extraer la copia elegida en un directorio
restringido, revisar diferencias y restaurar Compose, configuración y mecanismos de
secretos anteriores. Validar con las versiones correspondientes, aplicar Compose y
recargar Prometheus/Alertmanager. No restaurar datos de volúmenes ni eliminarlos para
revertir esta configuración. No volver a activar credenciales revocadas. Verificar
readiness, targets, reglas y el canal restaurado. La copia local no representa los
archivos adicionales que pudieran existir solamente en el servidor.

`perm.env` y otras credenciales SMTP ya estaban rastreadas antes de esta migración.
El nuevo procedimiento no las copia ni usa. No se ha reescrito el historial Git ni
rotado credenciales; retirar/rotar esas credenciales antiguas es una tarea separada.

## Fase 1: deduplicación preparada

Ver [DEDUPLICATION.md](DEDUPLICATION.md) para las equivalencias comprobadas,
las variantes conservadas, las pruebas y el rollback de esta fase. El catálogo
Blackbox pasa a ser `config/targets/blackbox.json`; los JSON remotos antiguos
se conservan pero dejan de leerse tras aplicar esta configuración.

## Ejecución autorizada y preparación de incidentes

La Fase 1 se ejecutó y validó el 2026-11-02, sin recreaciones ni recargas
innecesarias. El resultado y los cambios locales de Fase 2 pendientes de aprobación
están en [PHASE2-INCIDENTS.md](PHASE2-INCIDENTS.md). No desplegar los cambios EVA/CRM
como parte de una actualización de Prometheus.
