# Ensayo aislado de CRM Auth (#25)

Usar un motor Docker desechable con imágenes disponibles localmente y sin
conexión a producción. El Compose crea PostgreSQL 16 desde cero, con una
cuenta de servicio propietaria de `auth`, GoTrue y Mailpit. Los servicios
usan una red interna sin puertos publicados. Generar dos valores sintéticos
hexadecimales y configurarlos como `CRM_REHEARSAL_DB_PASSWORD` y
`CRM_REHEARSAL_JWT_SECRET` en un archivo local `.env` con permisos 0600.

Validar con `docker compose config --quiet` y arrancar con
`docker compose up -d --wait`. Desde el host aislado, identificar las
direcciones del puente interno de GoTrue y Mailpit con `docker inspect`,
y ejecutar `python3 smoke.py IP_GOTRUE IP_MAILPIT < .env`. El smoke prueba
el contrato HTTP y comprueba que el token de refresh se rechace tras el
logout. El ensayo de aceptación del #25 requiere además Supabase JS,
caducidad efectiva del token de acceso, autorización cruzada, proxy y
verificación de esquema y permisos sobre la copia representativa de CT618.

Para el flujo del SDK, instalar con `npm ci` en el entorno de preparación y
ejecutar `node sdk-smoke.mjs IP_GOTRUE < .env` desde el laboratorio.
El test espera la caducidad real antes de repetir la consulta de usuario.

El 20/11/2026 se verificó en CT9618 con la NIC desconectada. PostgreSQL
registró 27 tablas en `auth` y ninguna en `public`. GoTrue aceptó alta por
API de administración, login, refresh y logout con identidades sintéticas.
Mailpit recibió el correo de recuperación. Supabase JS rechazó el refresh
revocado y un JWT de acceso después de caducar. La verificación de CRMAPI,
los 401/403 de negocio y el despliegue de GoTrue siguen pendientes.

## Concesiones aprobadas para la API

La única cuenta inicial de producción tendrá `app_metadata.crm_role = admin`.
La política admite `app_metadata.project_roles` por módulo de UI y
`app_metadata.expense_roles` con valores `viewer:<partición>` o
`editor:<partición>`. Los roles de gastos pueden leer SHARED y su propia
partición. Solo admin y editor:SHARED pueden escribir SHARED. La fuente de
concesiones es un JWT firmado con issuer y audiencia comprobados.

El ensayo HTTP de la política verificó 401 sin JWT, con firma o issuer
incorrectos, token vencido y token de servicio. Dio 403 al intentar leer
o escribir otra partición, escribir como viewer y acceder a otro módulo.
Admin pudo leer y escribir las tres particiones y acceder a los tres módulos.
La autorización efectiva de consultas, exportaciones y mutaciones debe
probarse con CRMAPI y PostgreSQL antes de retirar Basic Auth.
