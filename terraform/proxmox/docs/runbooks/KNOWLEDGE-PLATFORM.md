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
