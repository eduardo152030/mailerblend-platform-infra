# Inventario y propuesta de retirada de Budibase (#31)

20/11/2026 Europe/Madrid. Inventario de solo lectura. El dominio original
sirve CRM UI desde CT618:18089. CT109 envía las cuatro ubicaciones de API
a 18088 y GoTrue a 18090. Ninguna ruta de la configuración activa de CT109 apunta a CT618:8080.
El upstream anterior sigue disponible en la red local y sirve de rollback.

## Dependencias observadas

| Componente | Estado y uso comprobado |
| --- | --- |
| budibase-app | CT618 healthy. Publica su HTTP en LAN. Conserva /data, el catálogo y una automatización publicada. |
| budibase-couchdb | CT618 activo, sin puerto publicado. Budibase referencia COUCH_DB_URL. Conserva el volumen /opt/couchdb/data. |
| budibase-redis | CT618 healthy, sin puerto publicado. Budibase referencia REDIS_URL. En la muestra se observaron 64 conexiones desde budibase-app. Conserva /data. |
| Originales | budibase-worker, budibase-app-d051-original y budibase-app-pre-recovery permanecen detenidos. |
| Email_send_new_entry | Activa en catálogo publicado. Disparador ROW_SAVED sobre contactos y acción SEND_EMAIL_SMTP. Se conserva hasta verificar el aviso equivalente de #68 en producción. |

La muestra de conexiones no acredita ausencia de consumidores esporádicos.
En los miembros de nucleo_network inspeccionados, solo budibase-app tenía
las claves de integración CouchDB/Redis examinadas. Falta comprobar los
accesos LAN al puerto histórico, los usos fuera de CT618 y los
consumidores de la automatización. Los triggers PostgreSQL instalados en
contactos actualizan fecha y propagan nombre. La inspección no acreditó
una vía de correo equivalente para escrituras directas mediante CRMAPI.

## Áreas de IaC

- Compose y recuperación pertenecen a services/infra-composable-crm,
  con receta de D051, prueba de recuperación y salud de Budibase.
- inventory/services/infra-composable-crm.yml conserva la etiqueta de
  servicio anterior. Reconciliar inventario derivado en el cambio aprobado.
- services/infra-prom/config/rules/container-availability.yml espera
  budibase-app en CT618. Cambiar solo esa expectativa al retirar. No
  silenciar la vigilancia actual de CRMAPI ni GoTrue.
- Mantener runbooks y evidencias de recuperación mientras respalden
  operaciones e historial. Revisar scripts de deploy, rotación,
  restauración y generación de inventario antes de retirar referencias
  ejecutables. TLS y DNS del dominio actual permanecen operativos.

## Secuencia autorizada

1. Verificar el aviso nuevo de CRMAPI (#68) en producción mediante infra-mail,
   reservado a correo de negocio. Confirmar consumidores LAN y exclusividad de Redis.
2. Exportar los volúmenes del legado y el catálogo de aplicaciones a almacenamiento
   privado en `/mnt/storage`. Verificar SHA-256 y restaurar en un CT aislado.
   Comprobar CouchDB, catálogo y login con una identidad sintética.
3. Tras validar la restauración, detener de forma reversible los contenedores del
   legado. Conservar Redis si otro servicio lo usa. Registrar inicio y fin en
   Europe/Madrid y observar 24 horas los logs de CRMAPI, n8n y Redis, además de
   Prometheus. Ante incidencias, restaurar el servicio y verificar el rollback.
4. Pasadas 24 horas sin incidencias, eliminar únicamente los contenedores, imágenes
   y volúmenes exclusivos del legado. Retirar las referencias activas de Compose,
   scripts, inventario, monitorización y pruebas. Conservar evidencias históricas
   y los respaldos verificados.
5. Comprobar plan Terraform sin destrucción ajena, monitorización operativa, TLS,
   health 200, contactos anónimo 401, ambos golden, cinco minutos sin FIRING
   relacionado y búsqueda de referencias activas sin resultados.

La autorización del propietario cubre las fases de retirada y borrado bajo estos
controles. La fusión del inventario deja las operaciones pendientes en #31.
