# Avisos de contactos y recuperación de contraseña

Fase 7. [#68](https://github.com/eduardo152030/mailerblend-platform-infra/issues/68)
depende del relay [#69](https://github.com/eduardo152030/mailerblend-platform-infra/issues/69)
para producción. Rama `ops/crm-contact-notifications`, worktree
`../mailerblend-platform-infra-crm-notifications`, base inicial `d99463b6`.

Aplica la migración `14_contact_notifications.sql` antes de activar la versión de
CRMAPI que usa la cola. En un ensayo aislado, usa un destinatario sintético y
verifica que la creación de contacto se confirma con el SMTP caído. Comprueba
después el reintento, el registro de intentos y la ficha abierta desde el enlace.

El worker y GoTrue necesitan identidades diferentes del relay, STARTTLS en 587
y la CA correspondiente. Los valores se suministran desde el entorno privado.
Configura el destinatario inicial y activa el aviso como administrador desde
Configuración → Notificaciones, tras comprobar el trabajador y el SMTP. La
activación se aplica a nuevos contactos.

Antes de aplicar el proxy de recuperación al dominio de CRM, ensaya el paso a
paso con GoTrue y Mailpit. Verifica que el enlace usa `/auth/v1/verify`,
redirige a `/restablecer`, permite cambiar la contraseña y el usuario puede
entrar de nuevo. Incluye 401/403 de la configuración para usuarios sin rol
admin y los dos golden tests de ingestión en la validación de producción.

El ensayo local con PostgreSQL 14 verificó cola, deduplicación, fallo SMTP,
auditoría y reintento hasta capturar un mensaje en Mailpit. Queda repetir sobre
el PostgreSQL 16 del ensayo, validar GoTrue extremo a extremo y activar el relay.

El ensayo de recuperación sobre PostgreSQL 16 y GoTrue 2.197.0 confirmó el
correo capturado por Mailpit, el enlace con prefijo público, la redirección,
el cambio de contraseña y el inicio de sesión con la nueva contraseña. La
conexión de migraciones fija `search_path=auth`. El worker conserva pendiente
su ensayo de entrega sobre PostgreSQL 16 con las imágenes de release.
