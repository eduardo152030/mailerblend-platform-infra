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
