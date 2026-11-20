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

Se añadieron listados paginados de formularios web, facturas e historial.
La UI consulta CRMAPI por el mismo origen. El historial exige una
referencia de FormEntries y excluye las filas asociadas a leads LinkedIn.
Los PDF y las mutaciones de factura no forman parte de estos listados.
La lectura de facturas desde contactos conserva su contrato existente.

Se verificaron build Vite, tres contratos 401/403/200 y consultas sobre
datos sintéticos en PostgreSQL 16 aislado. La consulta de historial
excluyó una actividad sintética reservada a LinkedIn.

Decisión del propietario: conversiones queda en solo lectura. Las fallidas
muestran estado y error tanto en la cola como en el detalle. Se retiraron
los controles y el cliente de reintento. El #62 documentará consumidor,
contador de intentos y deduplicación antes de plantear implementación.
