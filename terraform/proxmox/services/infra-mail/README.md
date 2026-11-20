# Relay SMTP compartido

Fase 7 — [#69](https://github.com/eduardo152030/mailerblend-platform-infra/issues/69).
Rama `ops/infra-mail`, base `d99463b6`. Estado IN PROGRESS. Esta ronda incorpora
la configuración de submission y su política de cuota. Inventario del CT,
provisión, Mailpit, monitorización y activación siguen pendientes.

## Alta de un consumidor

1. Asigna una identidad exclusiva y guarda su contraseña en el almacén privado.
   Añade el hash de la contraseña al fichero Dovecot `service-users`.
2. Añade esa identidad a la entrada del remitente autorizado de `sender-login`.
   Aplica la configuración y regenera el mapa con `postmap`.
3. Configura el consumidor con el nombre interno cubierto por el certificado,
   puerto 587, STARTTLS obligatorio, CA de confianza y sus credenciales.
4. Comprueba en el ensayo que su remitente funciona, que se rechaza otro
   remitente y que las credenciales de otro servicio conservan su cuota.
5. Para revocar el acceso, retira la identidad del fichero privado y del mapa y
   vuelve a aplicar la configuración.

La cuenta del proveedor se instala solo en el relay mediante ficheros privados.
La cuota cuenta destinatarios autenticados por minuto. El mapa admite varias
identidades para el mismo remitente. La prueba real requiere verificar recepción
y autenticación del mensaje en el buzón destino después del ensayo Mailpit.

## Provisión

El plan con destino `proxmox_virtual_environment_container.svc["infra-mail"]`
debe mostrar únicamente la creación del CT 632. Registra la concesión
DHCP observada tras el alta y comprueba la resolución antes de activar clientes. Instala y valida Node Exporter con el
[runbook de provisión](../../docs/runbooks/NEW-LXC-PROVISIONING.md).
El instalador `install-relay.sh` requiere un CT dedicado y los siguientes
ficheros en `/etc/infra-mail/private` con acceso solo de root.

| Fichero | Contenido |
|---|---|
| `tls.crt`, `tls.key` | Cadena y clave del certificado del endpoint interno |
| `service-users` | Identidades Dovecot con hashes de contraseña |
| `sender-login` | Mapa Postfix de dirección SMTP a identidades autorizadas |
| `relay-host` | Destino upstream con formato `[hostname]:587` o `[hostname]:465` |
| `relay-password` | Mapa del destino upstream a su usuario y contraseña |

Publica el target individual de Node Exporter y las reglas de
`services/infra-prom/config/rules/infra-mail.yml` solo después del ensayo
aislado. La ruta existente de Alertmanager envía estas alertas a Telegram.

## Ensayo con Mailpit

En el entorno desechable, ejecuta `install-mailpit.sh` y después
`install-relay.sh --mailpit`. El instalador fija el upstream del ensayo a
`127.0.0.1:1025`. Usa certificados e identidades sintéticas. Comprueba
desde un cliente SMTP que se exige STARTTLS, que el servicio solo puede
usar su remitente y que el mensaje aparece en la API de Mailpit en
`127.0.0.1:8025`. El ensayo no necesita las credenciales del proveedor.

Genera el material privado fuera del checkout con `prepare-private.py`
usando la IP que asigne DHCP. El generador conserva las contraseñas de los
consumidores y la CA entre ejecuciones. Copia al CT solo los ficheros
requeridos por el instalador. Conserva `ca.key` fuera del CT, distribuye
`ca.crt` como confianza y entrega a cada consumidor únicamente su contraseña.
Si el router no publica el nombre del CT, usa la IP concedida y cubierta por
el certificado. Comprueba de nuevo el endpoint si cambia la concesión.

El relay se usa para correo de negocio. Las identidades iniciales son CRMAPI
y GoTrue. Las alertas siguen en Telegram mediante su canal existente. El alta
de otro consumidor requiere la indicación del propietario.
