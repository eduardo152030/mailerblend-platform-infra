# Fase 2 — ejecución autorizada del 2026-11-02

**Estado central: Fase 3 — DONE — Accepted with UAT Waiver.**
Aceptación formal registrada el 2026-11-02 (Europe/Madrid) en
[DECISIONS](../../docs/roadmap/DECISIONS.md), decisión D-011.

El propietario acepta los resultados técnicos/automatizados y las restauraciones
reales aisladas verificadas. CRM y EVA están operativos según las comprobaciones
realizadas. **La prueba manual adicional de login y flujos de negocio no se ejecutó
y fue dispensada por el propietario. La dispensa no demuestra que todos los flujos
funcionales hayan sido probados.** Los resultados siguientes son evidencias de la
intervención; los pendientes heredados siguen abiertos en el roadmap.

## CRM CT 618

- Causa: dos monolitos Budibase, memoria/swap agotadas, PSI elevado y cinco OOM kill
  acumulados antes de intervenir. No era un fallo de instalación de exporters.
- Inventario e IaC: memoria de 4096 a 6144 MiB, swap de 512 MiB conservada. Se revisó
  y aplicó un plan Terraform dirigido exclusivamente al cambio de RAM. Un override
  optativo conserva las etiquetas remotas y evita incluir su deriva en ese plan.
- El proveedor reinició el CT al aplicar RAM; no se presenta como cambio en caliente.
  Después se pudo realizar la parada ordenada requerida para el backup frío.
- Budibase sigue en **3.27.4**, con el mismo digest aprobado. CouchDB, Redis,
  PostgreSQL, secretos y montajes no se migraron ni actualizaron.
- El app original se conserva como `budibase-app-pre-recovery`, detenido. El
  duplicado `budibase-worker` también permanece detenido. Ningún contenedor o volumen
  original se eliminó. Sus dos volúmenes /data siguen existiendo.
- El nuevo app pertenece a `budibase-recovery` y usa exactamente el /data original
  del app. Las dependencias siguen siendo CouchDB/Redis externos y MinIO integrado.
- Segunda aplicación sin cambios: mismos ID y StartedAt. Plan dirigido de Terraform
  posterior sin cambios (usando `recovery/memory.tfvars.json`).

### Backups y prueba de recuperación CRM

En PVE, directorio privado `/mnt/storage/mailerblend-recovery/20261102T100708Z/crm`:

- Backup frío nativo `vzdump-lxc-618-2026_11_02-11_09_28.tar.zst`, aproximadamente
  4,04 GB comprimidos; contiene rootfs, imágenes, configuración y datos.
- Bundle adicional de los cinco volúmenes y configuración, aproximadamente 119 MB.
  Verificado y extraído en staging sin sobrescribir destinos.
- Ambas copias tienen una segunda copia cifrada fuera del nodo, con descifrado y
  SHA-256 contrastados con el original. Los JSON privados `*.verified.json` guardan
  las evidencias. No basta con comprobar únicamente el archivo cifrado.
- Restauración real del CT completo en **9618**, sin IP publicada, enlace de red
  desactivado y sin salida a producción. Comparados contenido, tamaño, UID/GID y
  modo de los cinco volúmenes con la copia fría.
- Ensayo del overlay conservando los originales para rollback.

Pruebas aisladas y repetidas en producción: UI/builder HTTP 200, estado Budibase
passing/version 3.27.4, CouchDB 4 bases/69 documentos, PostgreSQL 27 tablas públicas,
lectura y escritura temporal con rollback, API `/health` y `/ready` 200, consulta
API autenticada 200, MinIO 2 buckets/106 objetos y lectura de objeto de muestra.
Estas comprobaciones no equivalen a recorrer manualmente todas las aplicaciones,
permisos y automatizaciones; la aceptación final se ha formalizado con la dispensa de UAT descrita arriba.

### Observaciones de salud heredadas

El healthcheck Docker del monolito comprueba un Redis interno con autenticación
incompatible (`WRONGPASS`), aunque el estado real de Budibase con Redis externo es
passing. El healthcheck del API CRM invoca `wget`, ausente de su imagen, mientras
`/ready` y la API autenticada funcionan. No se han ocultado esos avisos ni cambiado
las imágenes para corregirlos dentro de esta recuperación.

## EVA CT 622

Ejecución completada. Objetivo de 25% superado: Prometheus mide **34,15% libre**,
coherente con `df`: 14.396.366.848 bytes disponibles sobre 42.158.374.912 bytes.
Los nueve servicios/exporters originales siguen representados y los siete
contenedores de aplicación originales se conservan detenidos con sufijo
`-pre-storage-recovery`; los reemplazos usan las mismas imágenes y datos.

Backup frío nativo:
`/mnt/storage/mailerblend-recovery/20261102T100708Z/eva/vzdump-lxc-622-2026_11_02-11_41_01.tar.zst`,
12.600.126.707 bytes comprimidos. Incluye datos PostgreSQL, imágenes activas/rollback,
configuración, uploads, persona, journal y logs Docker. Se eligió la alternativa
fría completa del plan para mantener coherencia entre DB y archivos.

Restauración aislada **9622**, sin red externa: 2.274 archivos de datos/configuración,
journal y logs contrastados por SHA-256, tamaño, UID/GID y modo antes de arrancar.
API y Focalboard HTTP 200, 3 bases PostgreSQL/34 tablas públicas, escritura temporal
revertida, 26 archivos uploads y 2 persona. Se conservan las imágenes originales.
Focalboard usa PostgreSQL, no SQLite. Su healthcheck heredado invoca `curl`, que no
existe en la imagen instalada; la web responde correctamente.

La copia externa cifrada se completó y verificó descifrándola: SHA-256 idéntico al
backup nativo. El ciphertext ocupa 12.603.203.210 bytes. Un corte SSH inicial se
resolvió con transferencia reanudable; ninguna limpieza comenzó con copia incompleta.
El rollout se ensayó completo en el clon; para el cron aislado se recuperaron los
paquetes de su contenedor original sin cambiar la imagen ni abrir egress.
Después se aplicó en producción, donde se comprobó previamente el acceso a los dos
repositorios Alpine del bootstrap. Cron listo con curl instalado, no solo Running.
Una segunda aplicación tanto en clon como producción mantuvo los ID y StartedAt
de los siete contenedores: sin recreaciones ni reinicios. Los siete originales
permanecen detenidos; los siete reemplazos tienen RestartCount=0 y logging verificado.

## Seguridad, operación y rollback

- Backups y metadatos con secretos permanecen fuera de Git, directorios 0700 y
  archivos 0600. Las copias externas están bajo
  `~/.local/share/mailerblend-recovery/20261102T100708Z/`; la clave privada está en
  `keys/backup.key` dentro de ese directorio. Conservarla de forma segura: sin ella
  no se pueden recuperar los archivos cifrados. No publicar su contenido.
- Clones de ensayo con onboot=0 y red bloqueada; no usar sus direcciones loopback
  como configuración de producción. Se conservan para revisión, sin borrarlos.
- Excepciones de parada forzada autorizadas posteriormente por el propietario:
  únicamente el mantenimiento dormido y el cron sin tareas activas, comprobando
  procesos y ausencia de montajes de datos; para el cron, API previamente parada.
  Scheduler y sync terminan ordenadamente con su manejador SIGINT, sin SIGKILL.
- Ningún borrado de volúmenes, imágenes activas, contenedores originales o blobs de
  containerd; ninguna actualización de imágenes ni ampliación de disco.
- No reducir automáticamente los 6 GiB de CRM: requiere observar carga y revisar
  otro plan acotado. Un cambio del proveedor podría reiniciarlo de nuevo.
- Rollback de configuración: detener limpiamente el reemplazo, renombrarlo a un
  nombre libre, devolver el nombre original al contenedor conservado y arrancarlo
  sobre los mismos datos. Nunca dos motores sobre un mismo directorio de DB.
- Si se necesita recuperar datos, restaurar el conjunto coherente en otro CT aislado;
  no sobrescribir bases vivas ni perder escrituras posteriores sin una decisión
  explícita. Revertir retención no devuelve historia retirada: consultar el archivo
  verificado. La caché se reconstruye, con coste de tiempo/red.

## Cambios reproducibles y pruebas

Artefactos principales: overlay Budibase y volúmenes explícitos, inventario CRM,
override de etiquetas para plan dirigido, helpers de backup/cifrado/restauración,
checks funcionales, modelo EVA con logging acotado e imágenes instaladas fijadas,
helper de reemplazo que preserva originales, rollout gradual y drop-in journald.
No se aplicó el inventario general ni se desplegaron servicios ajenos a esta fase.

Pruebas locales: 11 de backup/recuperación CRM, 7 de seguridad de Fase 2 y 6 del
modelo/rollout EVA. Incluyen corrupción, restauración, rechazo de sobrescrituras,
protección de secretos, deriva de entorno y timeout de readiness antes de parar la
DB. `bash -n` sobre los helpers de operación. Validación real de Compose con el
entorno privado existente y sin mostrarlo.

La aceptación exige además las métricas reales, alertas y mediciones finales
registradas a continuación; un HTTP 200 aislado no certifica todos los flujos de
negocio del propietario.

## Mediciones finales y aceptación automática

Mediciones del 2026-11-02, aproximadamente 14:10 UTC:

| Comprobación | Resultado |
|---|---|
| CRM CT 618 | Operativo; Budibase 3.27.4 passing, UI/API y datos comprobados |
| CRM RAM / swap | 2.485.825.536 bytes (~2,32 GiB) / 25.554.944 bytes (~24,4 MiB); límite 6 GiB |
| EVA RAM / swap | 1.213.767.680 bytes (~1,13 GiB) / 0 bytes; límite 2 GiB conservado |
| OOM | 0 eventos nuevos desde el reinicio de ambos CT; contadores actuales oom/oom_kill=0 |
| PSI memoria | some/full avg10, avg60 y avg300 = 0 en ambos CT |
| EVA almacenamiento | ~14,4 GB disponibles, ~34,15%; objetivo >=25% cumplido |
| Journal | 384 MiB; servicio activo, sin avisos de claves desconocidas; política 1 GiB / 30 días |
| Exporters | Los cuatro up=1 durante al menos 10 min: min_over_time=1 y 20 muestras por target |
| Prometheus / Alertmanager | Ambos readiness HTTP 200; 13 reglas health=ok |
| Alertas CRM/EVA | Ninguna activa en Prometheus ni Alertmanager |
| Telegram | 94 intentos, 56 fallos históricos, incremento de fallos en 10 min = 0 |
| Clones 9618 y 9622 | Detenidos, onboot=0, red aislada; conservados sin borrar |
| IaC local | 24 tests y bash -n correctos; sintaxis Python comprobada |

La memoria fluctúa y la swap residual CRM no implica presión actual: no se ejecutó
swapoff ni se redujo memoria para forzar artificialmente un contador a cero.
El nodo mantiene swap histórica; no se ha cambiado la configuración de otros CT.

### Espacio recuperado, sin doble contabilidad

- Antes de limpiar (después del backup/rearranque): 6.519.439.360 bytes libres.
- Después de BuildKit: 10.493.468.672 bytes libres; aumento real ~3,97 GB.
- Después de journal: 14.402.670.592 bytes libres; aumento adicional ~3,91 GB.
- Limpieza caché+journal: **~7,88 GB** recuperados (~7,34 GiB). Tras el rollout y su
  crecimiento normal quedan ~14,40 GB libres. No se prometen 19 GB de cache liberada:
  los tamaños lógicos y capas compartidas no equivalen a bytes físicos recuperables.
- La primera medición del diagnóstico era ~5,77 GB libres. Su diferencia con los
  6,52 GB previos a la limpieza ocurrió durante el backup/rearranque y no se atribuye
  a los comandos de limpieza.
- Los logs Docker históricos siguen en los originales detenidos; **no se contabiliza
  su tamaño como ahorro**. Los siete nuevos contenedores tienen json-file 20m x 5.
- No hubo system prune, volume prune, image prune ni borrados manuales en containerd.
  No se actualizó ninguna imagen ni se amplió el disco.

Se han recuperado la recogida de métricas CRM (`HostOutOfService`/`ExporterDown`)
y la condición de espacio EVA (`HostDiskFilling`). No se han relajado sus umbrales.
La consulta final solo presenta `CollectEndpointDown` de Nucleotecnológico, fuera
del alcance de esta intervención. La calidad/aislamiento de CPU y RAM de Node
Exporter y la visibilidad individual de cAdvisor siguen siendo la fase posterior;
up=1 acredita scraping, no certifica esa calidad de métricas.

Telegram ya estaba validado de extremo a extremo por el propietario. En esta
intervención se conserva su configuración y se comprueban contadores reales sin
nuevos errores; no se presenta como una nueva confirmación visual del móvil.

## Pendientes explícitos tras la aceptación

1. Corregir los tres healthchecks heredados: Budibase y API CRM, y Focalboard EVA.
   Sus endpoints reales han pasado las comprobaciones; Docker sigue mostrando
   unhealthy por las causas documentadas. No declarar que todos los healthchecks
   están sanos ni ocultarlos eliminando sus comprobaciones.
2. Digest EVA: el entrypoint heredado escribe una línea de formato crontab en
   `/etc/periodic/daily/send-digest`, sin shebang. Eso no representa correctamente
   un script periódico ni demuestra ejecución diaria a las 08:00. Se conserva el
   comando existente en esta intervención de logging y se señala para corrección
   funcional específica. No se ha disparado un digest real durante el ensayo.
3. El bootstrap curl/Alpine heredado depende de repositorios externos. Fijarlo en
   una futura imagen requiere una revisión separada; esta fase no actualiza imágenes.
4. Mantener backups y clave hasta aceptación, sin caducidad ni purga automática.
   Revisar capacidad/memoria CRM tras carga real antes de proponer volver a 4 GiB.

Las comprobaciones automáticas realizadas son correctas y el propietario las ha
aceptado con dispensa de UAT. No se atribuyen pruebas funcionales no realizadas ni
se declaran resueltos los healthchecks, el digest o Nucleotecnológico. Ver el
[estado central](../../docs/roadmap/CURRENT-STATUS.md) para continuar en Fase 4.
