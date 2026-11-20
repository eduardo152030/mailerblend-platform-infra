# LinkedIn Sourcing — consulta (#30)

Dashboard, pipeline, detalle, chat histórico, aprobaciones, plantillas,
base de conocimiento, límites, actividad y cooldowns usan lecturas de
CRMAPI. Los colores y estados se separaron de los fixtures, que ya no se
cargan en runtime. Las pantallas de consulta muestran errores de carga.

Las acciones de envío, registro de conversación, aprobación, importación
manual, borrado y edición de configuración quedan en #65. Se preserva
la ruta técnica de ingestión con token. Los enlaces visibles a perfiles
aceptan HTTPS en dominios LinkedIn.

Chromium en aislamiento verificó un lead, conversación, aprobación y
pestañas de configuración con datos sintéticos. Todas las peticiones de
pantalla fueron GET. El API activo devolvió 200 con JWT en trece lecturas
de dashboard, listas y configuración. Release pendiente de observar #64.
