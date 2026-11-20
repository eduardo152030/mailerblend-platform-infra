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
