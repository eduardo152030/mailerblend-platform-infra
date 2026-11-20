# Auditoría de hardening CRM (#49)

20/11/2026. El proxy y CORS están desplegados por #56 y #57. Esta ronda
añade Gitleaks en CI, retira valores de credenciales de ejemplos operativos
y limita el CSV de LinkedIn a 512 KiB en la interfaz. La API recibe JSON,
con el tope existente de 100 leads por lote. El correo y las credenciales
se configuran fuera del repositorio.

## SQL y validación de entrada

El inventario cubre los módulos Python de routers v1. Contactos e intake
ya usan modelos de entrada. Gastos, oportunidades, pendientes, presupuestos,
proveedores y varios routers de LinkedIn todavía aceptan cuerpos genéricos.
Los filtros dinámicos de SQL construyen índices de parámetros, cláusulas
predefinidas y listas de columnas permitidas. Queda pendiente revisar
cada interpolación y sustituir los cuerpos genéricos por modelos de dominio
sin cambiar los contratos de ingestión.

## Contenido y archivos

El gráfico genera CSS como texto y restringe el identificador, las claves
y los separadores de estilo. La importación CSV necesita una extensión y
un tipo admitidos antes de leer el archivo. El navegador convierte el
contenido a JSON para el importador autenticado. Los gastos guardan una
referencia adjunto_url. Esta revisión no encontró un endpoint que almacene
archivos binarios. La API valida las referencias HTTPS sin credenciales. Queda pendiente probar las
pantallas con datos sintéticos antes del release.

Las dos rutas de importación LinkedIn comparten un modelo Pydantic para el
lote. Las pruebas HTTP aisladas verificaron el 400 de lote vacío, el 401 sin
token de servicio y el 422 para un cuerpo mal formado. Gastos rechaza nuevas
referencias de adjuntos HTTP o con credenciales embebidas con 422. Omitir el
campo conserva las referencias existentes al editar un gasto.

## Release #58 en CT618

20/11/2026, 13:32 Europe/Madrid. UI y CRMAPI activos con la etiqueta
`0d8a23ee`. CT109 conservó el vhost y las excepciones existentes.
El primer intento generó dos alertas pendientes de health durante la
recreación. Se restauraron las imágenes anteriores y se verificó el
rollback. El segundo intento lanzó ambos servicios tras el scrape de
cAdvisor. TLS, health 200, contactos anónimo 401, lectura con JWT,
webform golden y LinkedIn golden con deduplicación pasaron. Siete
consultas de Prometheus a intervalos de cinco segundos sin alertas
nuevas. Respaldo del API `compose.before-20261120T123157Z.json` y de la
UI en `/opt/crm-ui-release/before-58.KJGFP2`, con etiqueta previa
`39e9aad67c16`. El resto de #49 sigue en curso.

## Contratos de escritura y ventanas SQL

Los cuerpos de escritura JSON ahora tienen modelos por responsabilidad:
oportunidades, pendientes, presupuestos, proveedores, gastos y los
módulos de LinkedIn. Se preserva la diferencia entre campos omitidos y
nulos en PATCH. La prueba aislada verificó ocho rechazos 422 y comprobó
que OpenAPI carece de cuerpos de objeto genérico en v1.

La ventana de tiempo de actividad, limpieza, aprobaciones, cooldowns,
resultados y dashboard de LinkedIn se pasa por parámetros de asyncpg.
Se verificaron índices y argumentos en siete rutas con un driver
instrumentado. Los fragmentos estructurales restantes seleccionan
columnas o cláusulas predefinidas y mantienen los datos en parámetros.
La prueba de limpieza usó dry_run y conservó los registros.

## Resultado de despliegue de SQL y cuerpos

20/11/2026 Europe/Madrid. Se mantiene en producción el release #58.
Tres intentos para el API `84064c56` alcanzaron salud de Docker:

1. Recreación tras el scrape. Pasaron health, TLS, acceso anónimo 401 y
   ambos golden. Las lecturas de seis rutas SQL devolvieron 200 y CORS
   permitió solo el origen configurado. Apareció DockerContainerUnhealthy
   pendiente para crm-api. Rollback verificado.
2. Sonda inicial a 1 s. Los mismos golden pasaron. Reapareció la alerta
   pendiente en la ventana ampliada. Rollback verificado.
3. API paralelo en 18091. Docker marcó healthy y la sonda anónima
   devolvió 401. Prometheus marcó DockerContainerUnhealthy pendiente del
   candidato a las 13:42 Europe/Madrid, antes de cambiar el vhost. Se
   detuvo el candidato. El servicio anterior y su vhost siguen activos.

Los cambios de SQL y cuerpos quedan listos para revisión. El bloqueo
operativo es la divergencia observada entre Docker y cAdvisor durante
el arranque. Los registros de Prometheus y los respaldos se conservan.

## Correlación Docker y cAdvisor

20/11/2026. Hora UTC de la telemetría.

| Intento | Arranque | Primer 0 | Primer 1 |
| --- | --- | --- | --- |
| Recreación | 12:35:58 | 12:35:58 | 12:36:28 |
| Sonda inicial a 1 s | 12:38:58 | 12:38:59 | 12:39:29 |
| Paralelo | 12:41:33 | 12:41:34 | 12:42:04 |

Para la primera recreación, el evento Docker ya capturado indica
`health_status: healthy` a las 12:36:09 UTC. Para los otros intentos,
el historial completo de eventos dejó de estar disponible. La
correlación usa la identidad del contenedor y su hora de inicio exportada.
`ALERTS` registró PENDING y ningún FIRING para estos intentos.

cAdvisor representa `starting` y `unhealthy` como 0. El cambio mantiene
`for: 5m`, filtra `crm-api-parallel` y aplica gracia de 90 s únicamente a
la identidad en arranque de CRMAPI. Docker usa start_period de 30 s y
start_interval de 1 s. El archivo activo de CT610 se respaldó en
`/opt/infra-prom/crm-health-before-20261120T124719Z.yml`. Se conservó el
resto de reglas y se validó con promtool antes de la recarga. La API de
reglas confirmó el cambio aplicado.

La ventana de estabilización productiva dura cinco minutos. Se consulta
el historial de ALERTS desde el inicio del despliegue para detectar
cualquier FIRING relacionado, incluso si se resuelve entre dos consultas.

## Reintento autorizado y aprobado

20/11/2026, 13:47–13:53 Europe/Madrid. CRMAPI `84064c56` quedó en CT618
con healthcheck healthy, start_period de 30 s y start_interval de 1 s.
Respaldo de Compose `compose.before-20261120T124757Z.json`. CT109
conservó el vhost activo. Pasaron TLS, health 200, contactos anónimo
401, autenticación Supabase, golden webform y golden LinkedIn con
deduplicación. Cinco minutos sin ninguna alerta FIRING relacionada.
El test promtool verificó gracia, exclusión y que un fallo persistente
sigue disparando la alerta. #49 DONE técnico. Siguiente #28, FormEntries.
