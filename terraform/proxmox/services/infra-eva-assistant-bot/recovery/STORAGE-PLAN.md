# EVA CT 622 — plan de almacenamiento autorizado

Aceptación central: **Fase 3 DONE — Accepted with UAT Waiver**, 2026-11-02.
Ver [DECISIONS](../../../docs/roadmap/DECISIONS.md), D-011. UAT manual no ejecutada
y dispensada por el propietario; no acredita todos los flujos funcionales.

Estado: autorizado el 2026-11-02; ejecución y resultados en
[PHASE2-EXECUTION.md](../../infra-prom/PHASE2-EXECUTION.md).
Las cifras siguientes son el inventario previo. No hay nuevos jobs destructivos
automáticos. La limpieza manual de caché y la retención autorizada del journal se
mantienen separadas del despliegue idempotente de aplicaciones.

## Medición y espacio potencial

Filesystem real ~39,26 GiB, disponible ~5,38 GiB; inodos libres ~82%.

| Fuente | Medición real | Operación propuesta tras aprobación | Estimación y consecuencias |
|---|---|---|---|
| Build cache | 129 registros, ~23,04 GB, todos Reclaimable=true y Shared=false; last-used >7 días | Retirar caché antigua no usada manteniendo un presupuesto inicial de 4 GB. Exportar antes las imágenes activas/rollback y verificar el código de build. | Objetivo máximo orientativo ~19,04 GB. Próximos builds más lentos, pueden necesitar red/dependencias que ya no estén disponibles. No afecta a volúmenes de DB, pero no prometer recuperación byte a byte. |
| containerd | 24.524.083.200 bytes físicos (~22,84 GiB) | Dejar que Docker/BuildKit liberen contenido sin referencias después de gestionar caché. | NO sumar esta cifra a build cache: es el almacenamiento físico que incluye esas capas. Nunca borrar snapshots/blobs manualmente. |
| Journal | ~4,14 GB en archivos: ~4,01 GB archivados y ~134 MB activos | Exportar copia binaria coherente y sus checksums fuera del CT; retirar solo archivados conforme a una retención aprobada de 1 GiB / hasta 30 días. | ~3 GB potenciales; se pierde consulta local del historial retirado. El límite de espacio puede conservar menos de 30 días. Recuperación del historial desde archivo, no desde el FS limpiado. |
| Logs Docker | Focalboard ~1,22 GB; scheduler ~179 MB; sync ~111 MB; API ~56 MB; otros menores | Exportar los logs necesarios y aplicar logging 20m x 5 por servicio de forma controlada. | Hasta ~1,2 GB orientativos sobre los tamaños observados, según la retención y recreación. Los logs históricos no migran automáticamente a los nuevos contenedores. |
| Imágenes | Docker informa ~19,1 GB; 7 activas | Conservar imágenes activas y de rollback. | No atribuir ahorro independiente ni ejecutar image prune general: hay contenido/capas compartidas y cifras de reclamación que requieren contraste. |
| Datos /opt | ~2 GiB | Preservar PostgreSQL, uploads, persona, Focalboard y configuración. | Cero ahorro propuesto. |

Las cifras son aproximadas y mezclan GB decimales/GiB donde se indica. El techo
orientativo combinado de caché+journal+logs es del orden de **23 GB**, NO una garantía.
No sumar los 24,5 GB containerd ni los 19,1 GB de imágenes a ese cálculo. La cantidad
real se conoce después de cada acción aprobada comparando df y las referencias.
No existe un dry-run de prune validado aquí: el inventario no equivale a una simulación
exacta. Si no se reconstruye/exporta una imagen necesaria, conservar su caché.

## Política propuesta

- Ningún system/volume/container prune global; no rm de ficheros Docker/containerd.
- Caché: operación manual aprobada, mínima edad 7 días y presupuesto conservado 4 GB.
  No activar GC periódico hasta revisar resultados, frecuencia de builds y aprobación.
- Logs por servicio: json-file, 20m, 5 archivos. Cambio ya preparado localmente en
  Compose; no tiene efecto retroactivo sobre contenedores existentes.
- Journal: propuesta de presupuesto 1 GiB y máximo temporal 30 días; no se instaló
  un drop-in ni se activó limpieza. La eliminación de historia necesita aprobación.
- El mantenimiento Docker del Compose preparado es informativo, no ejecuta prune.
- Backups preoperación conservados sin purga automática; política de caducidad debe
  acordarse según los requisitos de los datos. Segunda copia cifrada fuera de PVE.

## Backup y recuperación antes de tocar almacenamiento

1. Registrar imagen ID/digest y guardar las imágenes actualmente ejecutadas, además
   de Compose/configuración/secrets (archivos privados), fuera del CT. No hacer pull
   latest para obtener un supuesto backup equivalente.
2. PostgreSQL: dump lógico consistente y roles con utilidades de la misma versión;
   prueba pg_restore/listado y restauración aislada. Para backup físico, parada limpia
   o mecanismo soportado; nunca una copia en caliente de postgres/data presentada
   como consistente.
3. Coordinar pausa de escrituras con la copia de uploads/persona y datos Focalboard.
   Identificar su backend real y preservar su DB de manera consistente, no solo los
   ficheros de configuración. Focalboard está unhealthy y necesita diagnóstico antes
   de una recreación. Alternativa: copia fría completa CT 622 con ventana aprobada.
4. Exportar journal y logs Docker fuera del CT, con UID/GID/permisos y checksums.
   Protegerlos porque pueden contener datos personales o credenciales en mensajes.
5. Guardar en `/mnt/storage` (otro disco del nodo), no en el rootfs con 5 GiB libres;
   copiar además fuera del host. Verificar espacio, permisos y segunda copia.
6. Ensayar restauración de datos e imágenes en entorno aislado sin acceso a endpoints
   de producción. Un checksum comprueba transporte, no funcionamiento de aplicación.

## Secuencia tras una futura aprobación EVA

A. Backup/export y verificación. Registrar df, cache, journal, logs, health y datos.
B. Limpiar únicamente caché aprobada, con Docker/BuildKit, sin tocar imágenes/volúmenes
   activos. Medir el ahorro; detenerse si no coincide con el inventario o falla un build.
C. Archivar y gestionar journal conforme a la retención aprobada. No reiniciar Docker
   ni otros servicios como parte de una limpieza de caché.
D. Aplicar logging en piloto de un servicio sin estado, con la imagen instalada,
   sin build/pull. Validar; después por lotes. PostgreSQL requiere su propia ventana.
   No ejecutar el deploy genérico que pueda actualizar latest sin revisar sus efectos.
E. Comprobar espacio libre, DB, HTTP, uploads, schedulers, métricas y ausencia de errores.
   Mantener alertas existentes; no ocultar la presión de disco subiendo umbrales.

La limpieza de caché y archivos de journal ya exportados no debería requerir parar
la aplicación. La recreación de logs sí reinicia los servicios afectados: reservar
5–15 minutos para piloto y validación, y 15–30 minutos adicionales si hay que coordinar
DB/Focalboard; estimaciones sujetas a backup, carga y pruebas previas.

## Rollback y aceptación

Revertir Compose/retención evita borrados futuros, pero NO devuelve bytes ya eliminados.
Caché se reconstruye (con tiempo/red); imágenes y datos se restauran desde backups
verificados; journal/logs se consultan o reimportan desde el archivo conservado según
formato. No sobrescribir bases vivas ni mezclar datos de fechas diferentes.

Aceptar solo si: backups restaurables; aplicaciones y DB conservadas; IDs/digests
esperados; ningún volumen de datos eliminado; mínimo objetivo de 25% de espacio libre
tras las operaciones aprobadas, con crecimiento estable; logs nuevos rotando; journal
respetando política acordada; sin nuevas alertas de disponibilidad o pérdida de tareas.
La segunda ejecución sin cambios no debe recrear contenedores. Limpiezas son operaciones
explícitas separadas, no acciones implícitas de un despliegue idempotente.

Referencias oficiales:
- https://docs.docker.com/build/cache/garbage-collection/
- https://docs.docker.com/engine/storage/containerd/
- https://docs.docker.com/engine/logging/configure/

## Herramientas de ejecución preservando originales

- `scripts/generate-eva-storage-compose.py` compila el modelo con
  `installed-images.lock.json`: IDs locales inmutables, `pull_policy: never` y red
  `eva-network` externa. Instalar el resultado como
  `/opt/infra-eva-assistant-bot/docker-compose.storage-recovery.yml`.
- `scripts/apply-eva-preserving-logging.sh --execute REGISTRO SERVICIO` compara antes
  del cambio imagen, entorno y comando, detiene limpiamente y renombra el original
  a `*-pre-storage-recovery`. Crea solo su reemplazo en `eva-storage-recovery`,
  conserva datos/montajes/recursos y verifica logging 20m x 5. No elimina originales.
  No usar el despliegue genérico con latest ni Compose del proyecto anterior.
- `scripts/eva-storage-maintenance.sh --execute REGISTRO cache|journal` exige
  backup, copia externa, restauración, imágenes y logs preservados. La versión
  instalada de Buildx admite `--reserved-space 4GB --max-used-space 4GB`, con
  `--filter until=168h --all`; no admite el antiguo `--keep-storage`.
- `scripts/check-eva-functional.py BASELINE` comprueba HTTP, PostgreSQL, imágenes,
  contenedores originales y recuentos de archivos sin mostrar secretos.
- El backup frío nativo completo incluye el image store, journal y logs Docker.
  Se restaura aislado y se contrastan SHA/UID/GID/modo de los archivos antes de
  aceptar esa copia como archivo histórico. La segunda copia externa va cifrada
  y debe verificarse descifrándola; no basta con comprobar el ciphertext.

Aplicar primero un piloto de API en el clon. Para PostgreSQL, parar ordenadamente
los escritores (API, scheduler, sync, digest y Focalboard); actualizar logging de
PostgreSQL y esperar `pg_isready` antes de arrancarlos gradualmente. Repetir las
pruebas y comprobar que una segunda aplicación no cambia ID/StartedAt.

Los logs grandes permanecen en los contenedores originales detenidos: no atribuir
su tamaño como ahorro. Se preservan para rollback. Para revertir configuración,
detener el reemplazo y renombrarlo a un nombre libre; devolver su nombre al original
e iniciarlo, coordinando los escritores para PostgreSQL. Nunca arrancar dos
PostgreSQL sobre el mismo directorio. Revertir journal no recupera historia borrada:
consultarla desde el backup archivado verificado, sin sobrescribir registros vivos.

El orquestador `scripts/rollout-eva-storage.sh --execute REGISTRO BASELINE` realiza
esa secuencia con timeout/reintentos configurables (`READINESS_TIMEOUT=120`,
`READINESS_INTERVAL=2`). Si PostgreSQL ya pertenece al proyecto recuperado, no
repite la parada coordinada. Los helpers deben instalarse juntos en un directorio
privado del CT. No incorpora limpieza implícita: caché y journal son pasos explícitos.

### Excepciones autorizadas durante el ensayo

El propietario autorizó por separado la parada forzada del mantenimiento heredado
inactivo y del cron sin tareas, porque sus PID 1 no gestionan SIGTERM. Se limita a
`ALLOW_FORCE_MAINTENANCE=1` y `ALLOW_FORCE_CRON=1`: el helper
`stop-eva-container.sh` verifica procesos exactos y ausencia de datos montados; para
cron exige además API detenida. Sin esos flags no hay SIGKILL. Los procesos Python
scheduler/sync se paran con SIGINT tras verificar su manejador; los demás con SIGTERM.
El nuevo mantenimiento informativo incorpora un trap para terminar ordenadamente.

En el clon aislado el cron no puede descargar curl desde Alpine. El helper
`seed-eva-isolated-cron.py` recupera exclusivamente los directorios de paquetes de
su contenedor original detenido, sobre la misma imagen y sin red externa. Rechaza
una ruta por defecto o eth0 activo. No se usa en producción. El check exige crond
real y curl instalado, no solo un estado Running transitorio. La instalación de
paquetes al arrancar es una dependencia heredada pendiente de fijar en una futura
imagen; esta fase conserva la imagen y el comando de aplicación existentes.

El modelo aplicado y su ID de contenedor se guardan en
`/opt/infra-eva-assistant-bot/.storage-recovery/`, sin secretos. Se usa `--no-recreate`
y se rechaza cualquier diferencia del modelo registrado antes de un cambio implícito.
Esto evita depender de que el hash de etiqueta interno de Compose coincida con el
hash de `config --hash` tras opciones de CLI. La adopción explícita de un piloto
verificado solo se necesitó en el clon (`ALLOW_ADOPT_VERIFIED_RECOVERY=1`).
