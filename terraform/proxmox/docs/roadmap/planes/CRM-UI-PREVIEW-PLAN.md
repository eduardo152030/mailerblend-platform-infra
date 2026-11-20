# CT618 — preparación de preview CRM UI

[PR #39](https://github.com/eduardo152030/mailerblend-platform-infra/pull/39).

[Issue #24](https://github.com/eduardo152030/mailerblend-platform-infra/issues/24).
Fase 7, IN PROGRESS, 19/11/2026 Europe/Madrid.
Rama `feat/crm-ui-preview`, worktree hermano `mailerblend-platform-infra-crm-preview`,
SHA inicial `18743981dc27135879e4e9f321eab43fc08b4088`.

Lovable trasladado a [compose/crm-ui](../../../services/infra-composable-crm/compose/crm-ui/),
incluidas guías y prompts. Se sincronizó el lockfile npm para instalación limpia.
Dockerfile multietapa con digests verificados, Nginx con health y fallback SPA,
Compose publicado solo en loopback. La UI usa `/_svc/v1` relativo. Nginx
responde 503 para esa ruta y CSP limita conexiones al mismo origen. Sin
upstream real, hostname externo ni datos CRM.

Instalación limpia, build, typecheck, lint del cliente y Vitest PASS con
Node 22.23.1 y npm 10.9.8. Raíz, ruta profunda y assets PASS con Vite Preview.
Bundle sin dominio del API real. Lint global reportó errores y avisos en
el código importado. Build advierte por tamaño del bundle y datos Browserslist
antiguos.

Pendientes: Compose y Nginx con Docker real, idempotencia y digest del release.
Para una preview externa, confirmar DNS, fuente declarativa del proxy y
control de acceso antes de configurar TLS. Sin despliegue en CT618.

## Validación del servidor estático

Ronda 02, 19/11/2026 Europe/Madrid. Inicio `b29ef9b4`; base integrada
`b14f555f`. Resueltos los conflictos de seguimiento conservando en orden
el avance integrado de #23 y la preview de #24.

Se extrajo la imagen Nginx fijada por digest, verificando manifiestos y
capas por SHA256. Se ejecutó el binario dentro del rootfs en un namespace
local con red limitada a loopback, usando el nginx.conf del repositorio y
el build de Lovable. Solo se adaptó el usuario del archivo global de
Nginx en el rootfs temporal para el mapeo de UID local.

PASS: nginx -t; health por wget; raíz, /contactos y /linkedin-sourcing
devuelven el index; assets coinciden byte a byte y un asset inexistente
devuelve 404; GET/POST de API devuelven 503; se comprueba CSP del mismo
origen. Esto valida Nginx y las rutas de la preview. Pendientes Compose
real, idempotencia, digest del release y TLS externo. Sin cambios en CT618.

## Validación de Compose y proxy TLS de laboratorio

19/11/2026 Europe/Madrid. Rama `test/crm-ui-preview-validation`,
worktree hermano `mailerblend-platform-infra-crm-preview-validation`,
SHA inicial `0d6c345de8166130da400e79f3899b19f3a11ac9`. El PR #39 ya se integró.
[PR de validación #40](https://github.com/eduardo152030/mailerblend-platform-infra/pull/40).

- Docker Compose 2.32.4 descargado y comprobado con el SHA256 de la release.
  `docker compose config --format json` PASS con valores por defecto y
  overrides sintéticos de imagen y puerto. Ambos modelos conservan loopback,
  destino 8080 y healthcheck; no inyectan variables de CRMAPI.
- Nginx de la imagen fijada, en el rootfs aislado, recibió un virtual host
  temporal con TLS y autenticación básica, upstream loopback y credenciales
  de prueba. Curl validó cadena de confianza local y SAN sin excepciones:
  solicitud anónima 401, /contactos autenticado equivalente al index, POST a
  API 503. La adaptación de UID del ensayo anterior sigue aplicando.
- El certificado, las credenciales y el host sintético son solo de laboratorio.
  Esto no activa TLS en el dominio real ni prueba el ciclo de vida de Compose.
  Pendientes build de imagen final, idempotencia del servicio y acceso TLS
  en el proxy definitivo con DNS y titularidad confirmados. CT618 intacto.

## Ejecución de Compose en VM desechable

19/11/2026 Europe/Madrid. Rama `test/crm-ui-compose-runtime`, worktree
hermano `mailerblend-platform-infra-crm-compose-runtime`. Base
`4e8b5013d87125c394a53dc445eaadebfb317e20`, con #40 integrado.
[PR de ejecución #41](https://github.com/eduardo152030/mailerblend-platform-infra/pull/41).

QEMU 6.2 con TCG, Alpine 3.22, Docker 28.3.3 y Compose 2.32.4.
VM local temporal sin volúmenes, credenciales ni red de producción.
El primer build agotó el espacio de tmpfs después de npm ci. Se movieron
los datos de Docker al disco virtual desechable de 12 GB y se reintentó
con la misma fuente y digests. El build terminó y el servicio quedó healthy.

- Imagen local: `sha256:152feba841af890ee593b7f371eeab39ecb981db16482bcd654731992869ea78`,
  linux/amd64. Identificador de imagen local; sin publicación a un registro.
- Dos ejecuciones consecutivas de `docker compose up -d --wait`: PASS.
  ID, StartedAt, imagen y estado healthy idénticos. ID `bc3fd3a117b5`;
  StartedAt `2026-11-19T21:26:42.356782965Z` (UTC).
- Verificación HTTP por loopback: health devuelve ok, raíz y /contactos
  devuelven HTML idéntico y la ruta de API devuelve 503. PASS.

Sigue pendiente la exposición restringida en el proxy y dominio definitivos,
la validación TLS allí y, si se publica una imagen, el digest del registro.
Esta prueba no modifica CT618 ni certifica el lint global heredado.

## Proxy de preview preparado

20/11/2026 Europe/Madrid. Rama `feat/crm-ui-restricted-preview-proxy`,
worktree hermano `mailerblend-platform-infra-crm-preview-proxy`, SHA de
inicio `98bbc34a04ccdbb9dafdc05fd8b373a171724075`. PR #41 integrado y
aceptado por el propietario para la validación de laboratorio.

Lectura SSH estricta: Nginx activo en CT109, vhost habilitado
`/etc/nginx/sites-enabled/infra-svc01.mailerblend.com.conf` enlazado a
`sites-available`, con TLS y upstreams CT618:18088 y CT618:8080. GET del
login legacy y de `/_svc/health`: ambos HTTP 200 con certificado
verificado. El repositorio contiene el [inventario observado](../../inventory/routing-observed.json).
No se encontró una plantilla vigente del vhost legado en Git.

La [plantilla de preview](../../../services/infra-composable-crm/compose/crm-ui/proxy/preview.conf.template)
usa un vhost independiente con TLS y autenticación básica y un upstream
loopback en 18089. Las credenciales del proxy no se reenvían a la UI.
La configuración de la UI sigue devolviendo 503 en API y no contiene
destinos reales. La propuesta de topología coloca el Compose de preview
en el mismo host que el vhost para conservar loopback. Confirmar host,
titularidad DNS y certificado antes de preparar el despliegue.
No reutilizar el vhost actual para la preview.

Para probar la plantilla se sustituyeron únicamente los cuatro parámetros
`CRM_UI_PREVIEW_HOST`, `CRM_UI_PREVIEW_CERT`, `CRM_UI_PREVIEW_KEY` y
`CRM_UI_PREVIEW_USERS`. Son nombres y rutas, no contenido de secretos.
Conservar las variables de Nginx `$host` y `$scheme` al renderizar.
Nginx local por digest, SAN de laboratorio y puerto local 18443: sintaxis
PASS, anónimo 401, ruta autenticada 200 y POST a API 503. En la futura
ventana comprobar el modelo renderizado con la versión real del proxy,
respaldar su configuración, reencontrar los 200 del servicio legado y
verificar una segunda aplicación sin recarga innecesaria. El laboratorio
no certifica DNS ni TLS definitivo. Ninguna acción mutante en CT109 o CT618.
