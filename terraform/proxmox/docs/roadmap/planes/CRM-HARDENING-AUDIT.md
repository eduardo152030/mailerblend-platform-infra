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
