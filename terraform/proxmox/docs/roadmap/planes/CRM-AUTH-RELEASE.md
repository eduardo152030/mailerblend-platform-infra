# CRM Auth — release y reversión (#25)

20/11/2026, 10:25 Europe/Madrid. La única identidad productiva es admin,
provisionada con la API privada de GoTrue. PostgreSQL 16 contiene el esquema
`auth` y la cuenta de servicio carece de permisos sobre tablas de negocio.
SMTP queda pendiente. La sesión vive en memoria, con JWT de 120 segundos.
Logout revoca el refresh. Un JWT ya emitido caduca según su TTL.
La clave anon es el único valor de identidad incluido en Vite.

La matriz en CT9618 con PostgreSQL 16 verificó 401 anónimo y vencido, 403
cruzados, listados, detalle, siete informes, exportación y mutaciones.
Se corrigió el doble parseo JSON de P&L y el tipo de fechas de los cortes.
En producción Chromium verificó login, lectura de contactos, ausencia
de sesión persistida y logout. Verificados golden webform, LinkedIn con
token, health, acceso anónimo rechazado y ausencia de los secretos activos
comprobados en el bundle.

## Integración LinkedIn

Enviar POST a
`https://infra-svc01.mailerblend.com/_svc/v1/linkedin-sourcing/leads/import/service`
con `Content-Type: application/json` y `X-LinkedIn-Import-Token`. El operador
entrega el token desde su almacén privado. El contrato JSON coincide con la
importación de UI. Sin token o con token inválido devuelve 401. Un lote
vacío con token válido devuelve 400. Webform conserva `X-Ingest-Secret`.

## Secuencia y respaldos

La receta en compose/crm-auth prepara el esquema y servicio. CRMAPI se
publica por la receta D051 con una copia privada del Compose y una etiqueta
local del binario anterior. La UI se recrea con docker-compose.release.yml.
Después de confirmar el API JWT y GoTrue, activate-gotrue.py respalda el
vhost, pasa nginx -t y recarga Nginx.

Para revertir, restaurar la copia del vhost y validar y recargar Nginx.
Restaurar la UI con etiqueta 7082472b y el Compose anterior de CRMAPI,
`/opt/healthcheck-d051/crm-api/compose.before-20261120T092512Z.json`.
Copia del vhost terminada en `.before-gotrue-20261120T092532Z`.
Comprobar Basic Auth 401/200, health e ingestión antes de declarar
restaurado. Preservar el esquema y las credenciales para el diagnóstico.

## Separación de desarrollo

La UI utiliza rutas relativas. Vite en desarrollo y preview limita
`connect-src` al mismo origen. Usar API y datos sintéticos locales.
No configurar API productiva en desarrollo, preview ni sandboxes.

## Hardening CT109 (#49)

20/11/2026, 10:28 Europe/Madrid. El vhost tiene HSTS, CSP, X-Frame-Options,
Referrer-Policy y X-Content-Type-Options. El HTTP redirige a HTTPS. El límite
del API de usuario es 30 solicitudes/s por IP, con ráfaga de 90. Los bloques
exactos de webform, LinkedIn y health conservan su configuración.

El ensayo loopback de Nginx comprobó las cabeceras, HTTP 429 en la ruta
general y respuestas del upstream sin limitación de usuario para las
dos excepciones. En producción pasaron Chromium, las cinco cabeceras,
la redirección HTTP, el golden de webform y LinkedIn 401/400.

Para revertir esta ronda, restaurar la copia del vhost terminada en
`.before-hardening-20261120T092819Z`, validar Nginx y recargar.
