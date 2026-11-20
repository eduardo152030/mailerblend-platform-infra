# Smart management — consulta e informes (#29)

Gastos y Proveedores consultan CRMAPI. Los informes aplican la partición
seleccionada y una moneda a la vez. El filtro limita las concesiones del
JWT y el API responde 403 para una partición ajena. El detalle de
proveedor suma todos sus gastos autorizados por moneda en PostgreSQL,
incluidas las filas fuera de la primera página. Se retiró la referencia
sin uso a /gastos/stats-summary. La exportación CSV sigue autenticada.

El catálogo publicado no acredita las nuevas altas y ediciones de esta
UI. Se retiraron sus controles de Smart management y se registraron
en #63. Se conserva el contrato de API usado por otros consumidores.

Pruebas aisladas: build Vite, 401, 403, 422 y filtros de seis informes,
resumen de proveedor y totales con filas sintéticas EUR/USD en
PostgreSQL 16. Release productivo pendiente de la observación de #61.

Release #64, 20/11/2026 Europe/Madrid. Imágenes 42f108d4, integración
d929607f. Respaldo API compose.before-20261120T131627Z.json y UI
before-64.TbgFuN. Seis informes 200, resumen 200, moneda inválida 422,
ambos golden y cinco minutos sin FIRING relacionado. La corrección de
etiquetas EUR/USD en gráficos va en el release UI #66.
