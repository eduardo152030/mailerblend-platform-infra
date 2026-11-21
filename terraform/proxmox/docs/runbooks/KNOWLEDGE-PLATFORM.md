# Plataforma interna de conocimiento y diagramas

Consultar el [plan](../roadmap/planes/CT633-635-KNOWLEDGE-PLATFORM-PLAN.md)
y el [runbook de alta LXC](NEW-LXC-PROVISIONING.md) para aprovisionamiento, SSH,
observabilidad y rollback. Las definiciones de servicio y volúmenes están en
los Compose a los que enlaza el [inventario](../inventory/LXC-INVENTORY.md).

Después del alta, verificar SSH y observar la concesión DHCP. Instalar el
runtime con `scripts/knowledge-platform/install-docker.sh` a través de SSH
estricto, pasando el hostname exacto del CT como argumento. Usar ficheros privados 0600 con
las variables de `.env.example`. Generar la contraseña PostgreSQL en
hexadecimal. Ejecutar `scripts/knowledge-platform/deploy-compose.sh <servicio>
<directorio-ssh> <env-privado>`. El script valida el candidato y conserva
la configuración previa cuando cambia. Para revertir, reaplicar la versión
previa de Compose y su entorno, conservando los volúmenes.

## Arranque privado de Outline en CT633

El proveedor CRM actual queda fuera por falta de endpoints OIDC compatibles.
La variante privada usa Dex con dos identidades locales, SQLite persistente
y un gateway TLS que escucha solo en `127.0.0.1:18443` en CT633.

1. Usar un directorio privado nuevo fuera de Git. Ejecutar
   `scripts/knowledge-platform/prepare-private-outline.py <directorio> --admin-email <correo> --agent-email <correo>`.
   Reutilizar ese directorio en las reaplicaciones para preservar las claves
   de Outline, el secreto PostgreSQL y los identificadores OIDC.
2. Ejecutar `scripts/knowledge-platform/deploy-private-outline.sh <bootstrap-CT633> <directorio>`.
   El script carga los dos Compose y configura el gateway con la CA privada.
   `login.json` y `ca.key` permanecen en el directorio privado del operador.
3. Abrir un túnel SSH verificado hacia el puerto 18443 de CT633. Resolver
   `knowledge.test` a loopback en el cliente de ese túnel y confiar en la CA
   privada para abrir `https://knowledge.test:18443`. Comprobar `/_health`
   y `/dex/.well-known/openid-configuration` mediante TLS verificado.
4. Autenticar primero al administrador aprobado. Invitar la identidad agente
   al mismo workspace como miembro, mediante `users.invite` con
   `suppressEmail` si aún no se habilitó SMTP. Iniciar sesión con la segunda
   identidad y emitir una clave con los permisos REST concretos requeridos.
5. Mantener el directorio privado en el almacén del operador. Para recuperar
   Dex hacen falta su SQLite, la configuración y los identificadores de los
   usuarios. Para restaurar el servicio completo añadir PostgreSQL, Redis,
   adjuntos y material TLS según el procedimiento del final de este documento.

El acceso privado permite comprobar el producto y el flujo PlantUML. La
publicación definitiva requiere resolver DNS, TLS y rutas autorizadas.
La API autentica la creación del adjunto, y el endpoint local de carga
acepta el formulario firmado sin la clave REST.

## Origen de producción en CT109

La URL de entrada es `https://infra-doc.mailerblend.com/home`, que
redirige a la raíz canónica de Outline. El vhost de CT109 mantiene el
certificado de Certbot, admite clientes de la LAN y reenvía WebSocket,
REST y Dex al gateway de CT633 por TLS validado. CT633 acepta en ese
puerto conexiones desde CT109. El endpoint local de salud sigue
disponible para la sonda. El origen y callback OIDC usan el nombre de
producción. Las instrucciones de `knowledge.test` de la sección anterior
sirven para reconstrucción privada y reversión.

Para reproducir el corte, preparar un directorio root 0700 en cada CT.
En CT633, incluir `cutover-edge.py`, `edge/compose.yml` y
`edge/nginx.conf` con los nombres `compose.yml` y `nginx.conf`.
En CT109, incluir el script, `edge-location.conf` y la CA pública de CT633
como `ct633-ca.pem`. La clave privada de Certbot queda en CT109.
Ejecutar `python3 cutover-edge.py knowledge prepare <directorio>` dentro de
CT633 y `python3 cutover-edge.py edge prepare <directorio>` dentro de CT109,
por SSH estricto. Validar ambos candidatos. Dentro de la ventana, ejecutar
`edge apply` y luego `knowledge apply` mediante el mismo script y directorios.

Comprobar `/home`, `/_health`, el issuer de Dex, login de administrador y
miembro, workspace y sonda. Ante fallo, ejecutar `edge rollback` seguido
de `knowledge rollback` con sus originales y comprobar Docmost en el
vhost y Outline en acceso privado. El historial y la verificación están
en el [plan de corte](../roadmap/planes/CT633-OUTLINE-EDGE-CUTOVER.md).

El navegador necesita HTTPS para Outline y Draw.io. Usar la URL propia en el
ajuste Diagrams.net de Outline. Verificar el origen del editor y repetir la
edición tras reiniciar. PostgreSQL y Redis quedan en su red privada. Configurar
firewall antes de publicar los servicios. PlantUML se usa por IP privada y
con perfil SANDBOX.

Crear una página dedicada para el diagrama y obtener su UUID. Usar una clave
API del agente con acceso de escritura a esa página mediante el almacén
privado de la sesión, como `OUTLINE_API_TOKEN`.

```bash
python3 scripts/knowledge-platform/publish.py \
  --outline https://outline.example.invalid \
  --renderer http://192.0.2.10:8080 \
  --document 00000000-0000-0000-0000-000000000001 diagrama.puml
```

El publicador reemplaza el cuerpo de esa página con un PNG y la fuente
`.puml`. Reusar el UUID para actualizar. El endpoint
`/svg/<fuente codificada>` sirve para probar SVG en el mismo renderizador.

Para recuperar Outline, respaldar de forma consistente PostgreSQL, adjuntos,
configuración, Redis y secretos cifrados. Restaurar primero en un entorno
aislado y recuperar un documento con su Draw.io editable y fuente PlantUML.
