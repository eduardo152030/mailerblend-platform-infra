# CT636 — EVA UI con autenticación y correo compartidos

24/11/2026 (Europe/Madrid). Fase 7. Preparación IN PROGRESS y publicación
de la aplicación BLOCKED por el contrato de autenticación y la credencial
de Focalboard incluida en el código del navegador.

- [PR #99](https://github.com/eduardo152030/mailerblend-platform-infra/pull/99).
- Corte autorizado. Rama `feat/eva-ui-cutover`, worktree `/tmp/mailerblend-platform-infra-eva-cutover`, base `6bf2909ad158f6f59729bbd6a7831e4cb094fbec`.
- [PR #100](https://github.com/eduardo152030/mailerblend-platform-infra/pull/100) para el inventario del corte.
- Rama `feat/infra-eva-ui`, worktree `/tmp/mailerblend-platform-infra-eva-ui`.
- Base de la ronda `implementation`: `3d4e8248453164ea81f3dfa4fba56bc272a2d389`.
- Base de la ronda `review-01`: `564fd1b81da505f0dbfa6652e72ac5b1eebba2e3`.
  El propietario autorizó continuar hasta el corte. Primer cambio: transporte
  SMTP aislado, con pruebas locales y sin modificar el envío de Telegram.
- Fuente de UI: [eva-focus-board](https://github.com/eduardo152030/eva-focus-board/tree/7732d78b1dc0c0e110c778f51e87566cd31fbb08).
- Destino solicitado: `https://infra-eva-ui.mailerblend.com`. La resolución
  IPv4 respondió el 24/11. El registro de Route 53 lo configuró el propietario.
  La respuesta DNS no acredita vhost, certificado ni enrutamiento funcional.
- La consulta SSH estricta a PVE devolvió CT622 en ejecución y no encontró
  CT636. Queda por comprobar disponibilidad global, nodo, almacenamiento,
  plantilla, MAC y concesión DHCP antes del plan real.

## Alcance

Declarar un CT dedicado en el mismo nodo que CT622, siguiendo el
[runbook LXC](../../runbooks/NEW-LXC-PROVISIONING.md). La [especificación
candidata](../../../inventory/services/infra-eva-ui.yml) se incorpora al inventario para el plan dirigido.
CT622 seguirá ejecutando API, datos, tareas programadas y Telegram. La UI
se construirá desde un commit revisado, con lockfile e imágenes fijadas, y
se publicará por HTTPS mediante el ingreso existente, previa verificación
del destino DNS. Aplicación, rutas, secretos de runtime y operación deben
ser reproducibles mediante configuración y scripts versionados.

## Contratos pendientes

1. La UI inicia sesión con el JWT propio de EVA y llama a Focalboard desde
   el navegador mediante una credencial fija. Retirar la credencial del
   cliente y coordinar su revocación y sustitución tras identificar los
   consumidores. Servir las operaciones de tablero desde una API con
   autorización por usuario y operación. Mantener las credenciales de
   servicio de Focalboard únicamente en el backend.
2. Reutilizar el [GoTrue de CT618](CRM-UI-AUTH-CONTRACT-PLAN.md). Asociar
   emisor y sujeto a la identidad EVA y conservar sus permisos efectivos.
   Validar JWT y permisos en CT622 tanto por el ingreso como por la ruta
   directa. Separar las llamadas de scheduler, sync y Telegram de la
   sesión humana. Verificar las URL de redirección que use el flujo.
3. Enviar el correo de EVA desde CT622 mediante el
   [relay de CT632](../../../services/infra-mail/README.md). Usar identidad
   exclusiva, remitente autorizado, destinatario del propietario y
   STARTTLS con verificación del certificado. Resolver el buzón y
   remitente por configuración privada. Encapsular reintentos del correo
   para evitar duplicados y conservar la entrega independiente por Telegram.
4. Preparar backup y restauración aislada de CT622 y de los componentes
   de ingreso, identidad y relay que cambien. El rollback restaura esos
   cambios coordinadamente y retira la ruta de UI. Los datos de CT622
   permanecen en su ubicación.

## Validación de la declaración

`new-lxc.py prepare` exige una IP observada para generar SSH y sondas.
Con DHCP pendiente, usar la secuencia de provisión DHCP de
[CT633–635](CT633-635-KNOWLEDGE-PLATFORM-PLAN.md) y generar el bundle del
nuevo CT después de verificar su concesión. El intento local terminó
en esa guarda. No se generó un plan Terraform para CT636.

## Aceptación

- Plan Terraform real limitado a una creación. Segunda aplicación sin
  recreaciones ni recargas innecesarias. Sondas TLS, HTTP y métricas
  del nuevo CT verificadas antes de incorporarlas al catálogo.
- Login con la cuenta compartida. API devuelve 401 para token ausente,
  inválido o vencido y 403 para permisos insuficientes. Un usuario sin
  acceso tampoco puede operar contra la API directa o Focalboard. El
  bundle servido carece de credenciales privadas.
- Tablero, tareas y adjuntos funcionan contra el backend de CT622.
  Los datos existentes se conservan y se valida una restauración.
- Mailpit recibe el mensaje de prueba con STARTTLS. Se rechazan
  remitentes no autorizados. El propietario confirma recepción real
  en el buzón y recepción por Telegram. Un fallo de correo no impide
  Telegram y un reintento no duplica el envío.
- El nombre acordado sirve la UI con certificado válido. El rollback
  de la ruta y de la configuración de backend, auth y relay se ensaya
  antes del corte.

Siguiente paso: resolver el acceso de Focalboard y revisar los cambios de
EVA UI y CT622 junto con los contratos de GoTrue y SMTP. Los recursos y el
CTID de la especificación son una propuesta para validación.

## Ronda review-01 — corte autorizado

La consulta global de PVE del 24/11 confirmó que CT622 y CT632 están en
ejecución en el nodo `pve` y que CT636 no aparece en el clúster.
Se añadió el transporte `eva_mail.py` al código de CT622. Permite enviar
un correo puntual al único destinatario definido por el operador. Lee el
cuerpo de stdin y usa `EVA_SMTP_HOST`, `EVA_SMTP_USERNAME`,
`EVA_SMTP_PASSWORD`, `EVA_SMTP_FROM`, `EVA_SMTP_OWNER` y, si se usa una
CA privada, `EVA_SMTP_CA_FILE`. Se comprobó localmente el orden STARTTLS,
autenticación y entrega, la verificación del hostname y el bloqueo antes
de autenticar al fallar TLS. Quedan el alta de identidad en CT632, el
ensayo Mailpit, la conexión con una acción de EVA y la recepción real.

## Plan Terraform real del corte

24/11/2026 (Europe/Madrid). Se incorporó el CT636 al inventario y se
regeneraron las fichas y Notes. Con TLS y SSH estrictos el plan dirigido
contra el estado operativo devolvió 1 alta, 0 cambios y 0 bajas. Revisados
VMID 636, nodo pve, Debian 12 presente, local-lvm activo con capacidad,
1 vCPU, 1024 MiB RAM, 512 MiB swap, 12 GiB, DHCP en vmbr0 con firewall,
LXC sin privilegios y nesting/keyctl. El bundle SSH usa descubrimiento de
DHCP por MAC tras comprobar identidad PVE.

La creación con keyctl requiere sesión directa temporal `root@pam`
según el [runbook LXC](../../runbooks/NEW-LXC-PROVISIONING.md#docker-sin-privilegios-y-la-guarda-keyctl).
Se solicitó autorización específica para esa sesión. Después del alta
quedan desplegar la versión de UI con GoTrue, sustituir la credencial
Focalboard y validar el SMTP de EVA y Telegram.

## TLS en CT109

[PR #101](https://github.com/eduardo152030/mailerblend-platform-infra/pull/101).

24/11/2026 (Europe/Madrid). Rama `ops/eva-ui-ct109-tls`, worktree
`/tmp/mailerblend-platform-infra-eva-tls`, base `c519e3adc231201aae1235649f9f55e73ce419c0`.
El propietario autorizó preparar HTTPS en CT109. El wildcard Certbot
vigente cubre el nombre solicitado, como en CT634. Usar ese certificado
en un vhost de mantenimiento con HTTP 503, sin upstream hasta el corte.
Guardar respaldo de Nginx, validar la sintaxis, comprobar TLS y repetir
el despliegue para verificar idempotencia.

Vhost de mantenimiento aplicado en CT109. `nginx -t` PASS y respaldo
en `/var/backups/eva-ui-nginx.qZnEIw/nginx`. La primera sonda coincidió
con la recarga y falló viendo el certificado anterior; tras estabilizar,
la sonda local y la LAN devolvieron HTTP 503 con TLS válido. Se añadió
una espera acotada y rollback explícito al instalador. La segunda
aplicación confirmó contenido idéntico y evitó recargar. Draw.io y la API
EVA existente devolvieron HTTP 200 con TLS válido. El wildcard vence
el 18/02/2027 UTC y continúa bajo la renovación Certbot de CT109.

## Alta efectiva de CT636

[PR #102](https://github.com/eduardo152030/mailerblend-platform-infra/pull/102).

24/11/2026 Europe/Madrid. Ronda `implementation`, rama
`ops/eva-ct636-provision`, worktree `/tmp/mailerblend-platform-infra-eva-provision`,
base `663d2ea7ede5eea68679edbf9a83ffe8c75286c5`. Autorización explícita para
la sesión temporal directa de root@pam, limitada al alta de este CT.
Terraform aplicó 1 alta, 0 cambios y 0 bajas en el nodo pve. La segunda
ejecución del plan dirigido devolvió cero cambios. CT636 está RUNNING con
concesión DHCP observada `192.168.1.73` y con acceso por clave del
propietario verificado mediante bootstrap SSH estricto. El acceso de
recuperación por consola se conservó. Sesión temporal cerrada en el
proceso operador. Respaldo del estado Terraform conservado fuera de Git.

HTTPS válido en CT109, HTTP 503 de mantenimiento. Quedan el runtime y
el despliegue de la UI, la integración GoTrue/Focalboard, la identidad
SMTP, la monitorización y la aceptación con mensajería real.

## Runtime Docker de CT636

[PR #103](https://github.com/eduardo152030/mailerblend-platform-infra/pull/103).

Ronda `implementation`, rama `ops/eva-ct636-runtime`, worktree
`/tmp/mailerblend-platform-infra-eva-runtime`, base
`c64fe72c64af1693aba53aad074be53177f29f2c`. Reutilizar el instalador Debian
con versiones fijadas. Verificar daemon, Compose y una ejecución aislada
sin tocar el vhost de mantenimiento ni el backend CT622.

24/11/2026 Europe/Madrid. Docker 29.9.3 y Compose 5.7.1 instalados en
CT636 mediante el script versionado y SSH estricto. La imagen de prueba
`hello-world` se descargó correctamente. El arranque aislado devolvió
código 126: runc no pudo abrir `net.ipv4.ip_unprivileged_port_start`
durante la inicialización. Coincide con la incidencia documentada en
[el runbook LXC](../../runbooks/NEW-LXC-PROVISIONING.md#excepción-apparmor-aprobada-para-ct633635).
La excepción anterior se limita a CT633–635. Runtime BLOCKED para
contenedores de aplicación. CT636 sigue activo; CT109 mantiene TLS válido
y HTTP 503. Próximo paso: aprobar la excepción para CT636 o preparar la
UI estática con Nginx nativo y conservar el confinamiento actual.

## Servidor estático nativo de CT636

[PR #104](https://github.com/eduardo152030/mailerblend-platform-infra/pull/104).

Ronda `implementation`, rama `ops/eva-ui-native`, worktree
`/tmp/mailerblend-platform-infra-eva-native`, base
`c86a5fd7c19ee3627bc269b6305b119d6cc0fd19`. La UI Vite se entrega como
archivos estáticos. Preparar Nginx en loopback para ensayar el origen
sin ampliar el perfil AppArmor. El vhost de CT109 conserva mantenimiento.

24/11/2026 Europe/Madrid. Nginx 1.22.1-9+deb12u11 instalado desde Debian
en CT636 con el instalador versionado. Health local HTTP 204, única
escucha en `127.0.0.1:8080` y raíz HTTP 503 mientras no hay un bundle.
Segunda ejecución sin recarga. CT109 mantiene el HTTP 503 con TLS válido.
El perfil AppArmor se conserva. Antes del corte queda entregar el bundle
con GoTrue y acceso autorizado al tablero y habilitar el salto de CT109.

## Identidad de GoTrue en la API de EVA

[PR #105](https://github.com/eduardo152030/mailerblend-platform-infra/pull/105).

Ronda `implementation`, rama `feat/eva-ui-auth`, worktree
`/tmp/mailerblend-platform-infra-eva-auth`, base
`c710000bbcaee2f83ef8350a8956d11c9c64ea14`. Añadir un punto de sesión para
la futura UI con validación en GoTrue y autorización explícita por UUID
del propietario. Conservar los contratos de los procesos internos de CT622.

24/11/2026 Europe/Madrid. La ruta pública de GoTrue `/auth/v1/user`
respondió 401 sin token con TLS válido. CT622 incorpora en código
`GET /ui/session`, que valida el bearer con GoTrue y exige el UUID
configurado en `EVA_UI_OWNER_SUBJECT`. El valor se obtiene de la cuenta
del propietario mediante el canal operativo de identidad. La prueba
local de la dependencia confirmó propietario 200, otra cuenta 403,
sesión ausente o no válida 401 y servicio caído, redirección o respuesta
inválida 503. El cambio aún no está desplegado. Quedan aplicar la
autorización al tablero, conectar la UI, rotar la credencial antigua y
ensayar el corte.

## Acceso de la UI a los tableros

[PR #106](https://github.com/eduardo152030/mailerblend-platform-infra/pull/106).

Ronda `implementation`, rama `feat/eva-ui-board`, worktree
`/tmp/mailerblend-platform-infra-eva-board`, base
`02a011c7570d44f3fd688baf671e26412e164984`. Usar el token de servicio de
CT622 para las operaciones de tarjetas de tareas y contenidos. Exigir
sesión GoTrue del propietario y mantener el token en el servidor.

24/11/2026 Europe/Madrid. En código, `/ui/board/v2/boards` ofrece
listar, crear, editar y borrar tarjetas. Requiere la sesión GoTrue
del propietario y solo acepta los dos tableros de la configuración EVA.
En edición y borrado verifica que la tarjeta pertenece al tablero.
El cliente Focalboard agrega el token de CT622 y las cabeceras requeridas.
Pruebas ASGI con upstream simulado PASS para los cuatro métodos, acceso
anónimo, tablero ajeno, tarjeta ajena y payload que intenta cambiar de
tablero. Faltan prueba del token de servicio real, actualización de
eva-focus-board y despliegue coordinado. CT109 sigue en mantenimiento.

## Integración y ensayo local de la UI

26/11/2026 Europe/Madrid. Rama `feat/eva-ui-final-cutover`, worktree
`/tmp/eva-infra-final`, base `3ae2a596a382cbe5127a13701c766a88a9e2e119`.
La UI se actualiza en [eva-focus-board #1](https://github.com/eduardo152030/eva-focus-board/pull/1).
Build con Bun y seis pruebas aprobadas. Las llamadas al tablero usan el
backend y GoTrue. Credencial histórica ausente del bundle. Ensayar en
loopback y conservar el HTTP 503 de CT109 hasta verificar las rutas
autorizadas, el acceso del propietario y la mensajería real.

Ensayo de CT636 PASS. Se instaló por SHA-256 el bundle de
`eva-focus-board@4d0e883` en el origen local y se comparó el HTML
servido con el artefacto. La segunda aplicación comprobó todos los
archivos sin reemplazar el origen. CT109 sigue en HTTP 503 con TLS
válido. El ensayo no verifica login, adjuntos, administración ni correo.
La revisión de la UI está pendiente de integración por el propietario.
Para el corte quedan las rutas del mismo origen, el mapa UUID del
propietario, la rotación Focalboard y las pruebas reales del relay y Telegram.
