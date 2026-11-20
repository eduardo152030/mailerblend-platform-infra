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

Release #66, 20/11/2026 14:22–14:27 Europe/Madrid. UI 31f7d464,
integración d99463b6, respaldo UI before-66.ChvV5U. CRMAPI conserva
42f108d4. Pasaron TLS, health 200, contactos anónimo 401, ambos
golden y cinco minutos sin FIRING relacionado. Chromium en producción
verificó login Supabase, dashboard, pipeline y configuración solo GET.
La regresión de Smart management comprobó el informe USD y los
listados de gastos y proveedores de consulta.
