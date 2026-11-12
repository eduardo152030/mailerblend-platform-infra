# D079 — admisión y recuperación

> Antecedente histórico. La operación aprobada se rige por
> [D082](../release-d082/README.md). No ejecutar un despliegue de esta carpeta
> para sustituir automáticamente la versión aceptada.

> Recursos históricos sustituidos por D080: CT62715GiB/3CPU/2GiBswap,
> guardaCT14GiB, workerhard9GiB ystop8,2GiB. Ver
> [D080](../../../docs/roadmap/PHASE7-D080-QWEN-15G.md).

Versión desplegada en CT627. Procedimiento, límites, backup y resultado en
[informe D079](../../../docs/roadmap/PHASE7-D079-QWEN-CONTINUOUS.md).
`reclaim.py` requiere inyectar PLAN desde el manifiesto D078 y `--execute`;
no ejecutar de nuevo con la autorización consumida. No carga modelos.
El gate previo añade4,5GiB previstos y0,5GiB de reserva al total CT real;
no rebaja las guardas existentes ni descuenta caché supuestamente recuperable.
