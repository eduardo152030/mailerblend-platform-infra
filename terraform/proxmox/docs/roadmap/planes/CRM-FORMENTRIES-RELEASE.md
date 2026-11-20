# FormEntries — conversiones offline (#28)

La lectura usa la tabla existente con filtros, paginación, agregados y
detalle. El router exige el proyecto FormEntries cuando JWT está activo.
La UI representa el estado real `SENT`. El filtro histórico `SYNCED` sigue
siendo aceptado. Se verificaron en aislamiento fechas, filtros, paginación,
404 para un ID inexistente y 401 sin JWT.

El esquema permite `PENDING`, `SENT`, `FAILED` y `SKIPPED`. La guía describe
un consumidor automático de la cola PENDING, pero el repositorio no
identifica el consumidor desplegado ni quién contabiliza los intentos.
La UI heredada de Lovable también permite pulsar reintentar en PENDING.
Queda pendiente decidir qué efecto debe tener el botón en producción:
reencolar solo FAILED y dejar que el consumidor contabilice el siguiente
envío, o mantener temporalmente una pantalla de consulta. Facturas y la
automatización publicada se tratan en la continuación de #28.
