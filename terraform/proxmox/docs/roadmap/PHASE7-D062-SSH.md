# Fase 7. IaC Reliability, Security & Disaster Recovery — SSH de nuevas altas

D062, 2026-11-10 (Europe/Madrid). **Implementación local DONE; despliegue y
aceptación real PENDING VERIFICATION.** Subfase7.4 READY FOR FIRST REAL PROVISIONING TEST.
[Roadmap](ROADMAP.md) · [Estado](CURRENT-STATUS.md) · [Decisión](DECISIONS.md)
· [Procedimiento completo](../runbooks/NEW-LXC-PROVISIONING.md).

## Resultado y alcance

El flujo `new-lxc.py prepare` prepara la clave pública del propietario, configuración
y controlador SSH, con y sin Docker. Terraform ejecuta automáticamente el controlador
al crear el CT seleccionado. Instala openssh-server si falta mediante consola PVE,
fusiona authorized_keys conservando claves/opciones legítimas, valida sintaxis,
comprueba acceso real por clave antes y después de deshabilitar contraseña y emite
recibo únicamente tras PASS. Rollback de configuración, consola y clave conservados.

Provider0.94.0 admite claves de root en creación/clone. Como el mecanismo PVE puede
reemplazar su bloque de claves heredadas, la ruta estándar usa fusión aditiva por
`pct exec`, sin depender de SSH dentro del CT. Inyección del provider disponible
solo con conjunto completo de claves de plantilla revisado y opt-in explícito.
Fuentes primarias enlazadas en el runbook; no se necesita contraseña de bootstrap.

Se probó un marcador Terraform auxiliar y se descartó al ampliar el grafo a todos
los CT. La implementación final usa provisioner de creación en el recurso existente:
plan dirigido de un solo CT. Riesgo conocido: un fallo puede dejarlo tainted;
el runbook exige conservarlo, recuperar por consola/controlador y revisar el estado
antes de cualquier apply, nunca recrearlo automáticamente para resolver SSH.

## Evidencia local

- 15 tests de provisioning: nueve SSH y seis previos; instalación de clave/paquete,
  permisos, conservación/deduplicación, transición sin cerrar contraseña, gate de clave,
  sintaxis/política incompatible, rollback, idempotencia sin recarga y protección17CT.
- 14 tests de inventario PASS; frescura de Notes y referencias PASS.
- Dos pruebas Terraform realmente ejecutadas: fixtures Docker/nativo, mock_provider,
  command=plan, cada una1create/0change/0destroy. Ningún provisioner ejecutado por mocks.
- Terraform fmt/validate PASS, bpg/proxmox0.94.0 sin upgrade.
- Gitleaks sobre los archivos del alcance:0 fugas;152 enlaces locales y diff --check PASS.
- Binario OpenSSH8.9p1 Ubuntu extraído en directorio privado, sin instalar servicio
  local: `sshd -t` PASS y `sshd -T -C` confirma root without-password (sinónimo de
  prohibit-password), pubkey yes, password no, keyboard-interactive no. Solo claves
  efímeras de prueba; no se abrió puerto ni se inició sshd.
- Artefactos/logs privados: `~/.local/share/mailerblend-recovery/ssh/d062/`;
  bundles finales `service.yml-final` y `docker-service.yml-final`.

[Resultados estructurados](evidence/2026-11-10-d062-ssh.json).
No se copió, leyó ni mostró la clave privada del propietario. El cliente OpenSSH
utilizará su identidad local únicamente al ejecutar el primer alta real autorizada.

## Límites y siguiente paso

No hubo conexión a PVE/CT, instalación en producción, creación, cambio de contraseña,
SSH de los17 existentes, commit ni push. Los cambios ajenos permanecen intactos.
Debian/Ubuntu con Python3/systemd y puerto22 es el contrato preparado; plantillas
con Match incompatibles o claves restringidas pueden bloquear de forma segura.
Instalación real de paquetes, conectividad, servicio, recuperación e idempotencia
productiva aún no probadas. Un mock no acredita acceso real ni aceptación.

Siguiente: autorización de un CT concreto, revisión de plantilla/accesos/plan y
primer ensayo real con segunda aplicación. No se ejecuta en esta intervención.
7.2/7.3 globales siguen OUT OF SCOPE; D062 no autoriza publicar Git.
