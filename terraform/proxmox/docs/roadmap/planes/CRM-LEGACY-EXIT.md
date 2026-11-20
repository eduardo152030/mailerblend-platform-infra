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
| Email_send_new_entry | Activa en catálogo publicado. Disparador ROW_SAVED sobre contactos y acción SEND_EMAIL_SMTP. Se conserva hasta confirmar su uso y decidir su destino. |

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

## Secuencia propuesta

1. Confirmar con los responsables los accesos LAN, los consumidores de
   CouchDB/Redis y el efecto de Email_send_new_entry. Validar su reemplazo
   o retirada en aislamiento sin iniciar envíos reales.
2. Identificar respaldo reciente y ensayar la recuperación de catálogo,
   identidad y una muestra funcional. Acordar plazo de conservación y
   punto de reversión. Preservar las copias y los servicios vigentes hasta
   la aprobación del propietario.
3. Con autorización separada, aplicar cambios versionados al inventario,
   expectativas de salud y Compose. Empezar por una detención reversible
   y validar el dominio, GoTrue, 401 anónimo, ambos golden y cinco minutos
   sin FIRING relacionado. Revertir ante fallo.
4. Tratar cualquier borrado de contenedores, volúmenes o datos como una
   acción con aprobación separada. El procedimiento inicial conserva
   datos, imágenes y respaldos.

El inventario no autoriza una parada ni una limpieza de producción.
