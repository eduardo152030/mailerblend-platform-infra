# Inventario operativo LXC mediante IaC

Cobertura: los 17 LXC definidos en `inventory/services/*.yml`. El inventario
[generado](LXC-INVENTORY.md) incluye ficha detallada y tabla resumen. Documentación
parcial significa que existen campos pendientes, no que falte el LXC.

CT614 tiene ya su ficha principal independiente:
[614-LXC-INVENTORY.md](614-LXC-INVENTORY.md). El índice general enlaza esa ficha;
Notes son un resumen operativo separado, ambos versionados. D047 verificó producción
y actualizó únicamente description de CT614; los detalles están en su evidencia.
No se investigaron nuevos servicios ni se aplicó el inventario global.

CT615 dispone también de ficha principal independiente:
[615-LXC-INVENTORY.md](615-LXC-INVENTORY.md), con sus rutas reales de Preview.
D049 aplicó solo sus Notes mediante plan exclusivo description; CT614 no cambió.
[Procedimiento Notes615](../../services/infra-mailerblend-edge/NOTES-IAC.md).

## Fuentes y significado

- **Declarado:** inventario de servicios/defaults y `inventory/documentation.yml`
  (función, aplicaciones, dependencias declaradas en Compose, proyecto y runbook).
  Es el esquema versionado que valida `scripts/generate-lxc-inventory.py`.
- **Observado:** `inventory/lxc-observed.json`, captura fechada de PVE y Docker;
  `routing-observed.json`, únicamente server_name/proxy_pass y upstreams filtrados
  de Nginx CT109. No se recopilan entornos, payloads ni logs completos.
- **Confirmado funcionalmente:** solo lo documentado en el campo correspondiente;
  proceso running o health Docker no equivale a aceptación funcional de negocio.
  Los targets actuales se consultan en Prometheus; el inventario no sustituye ese
  monitor. La aceptación F4 D041 es histórica y está enlazada.

No derivar dominios por similitud del nombre. Por ejemplo, el proxy observado
asocia `infra-svc01.mailerblend.com` con CT 618, aunque el README histórico de
NocoDB se lo atribuye a CT 61211. Se documenta la discrepancia sin cambiar rutas.
Los dominios compartidos identifican un upstream del virtual host; no implican
que todas las rutas pertenezcan al mismo CT ni certifican DNS/TLS/entrega pública.

Los discos observados pueden diferir de los declarados; Terraform ignora cambios
de disco en el recurso existente. Esta tarea no reconcilia tamaños, tags ni otros
recursos. Los contenedores detenidos se documentan como conservados, sin afirmar
que por sí solos sean un backup recuperable.

## Generación y validación

Desde `terraform/proxmox`, con Python 3 y PyYAML disponibles:

```bash
python3 scripts/observe-lxc-inventory.py --output inventory/lxc-observed.json --routes-output docs/inventory/routing-observed.json
python3 scripts/generate-lxc-inventory.py
python3 scripts/generate-lxc-inventory.py --check
python3 -m unittest discover -s tests/inventory
terraform fmt -check inventory.tf main.tf
terraform validate
```

El descubrimiento es de solo lectura, usa SSH estricto existente a PVE y no cambia
servicios. Revisar diferencias antes de generar fichas nuevas. Las notas previas
útiles están preservadas una sola vez en `legacy_notes`, evitando anidarlas al
repetir el descubrimiento. Si aparecen notas manuales nuevas, revisarlas e
incorporarlas explícitamente antes de aplicar.

El generador produce `inventory/generated/lxc-notes.json` y el Markdown desde los
mismos datos. Terraform utiliza `templates/lxc-notes.tftpl` con ese JSON, sin
mantener 17 textos paralelos. El manifiesto de hashes vincula todas las fuentes,
el generador y la plantilla; una precondición bloquea el plan con datos obsoletos.
No editar artefactos generados manualmente.

## Estado D-045 histórico: BLOCKED; CT614/615 aplicados con planes acotados

La Issue de sGTM está creada: [#1](https://github.com/eduardo152030/mailerblend-platform-infra/issues/1).
En D045 las Notes quedaron preparadas, **no aplicadas**. D046 posterior aplicó
exclusivamente CT614: [fuente y procedimiento](../../services/infra-nucleoedge/NOTES-IAC.md).
D049 posterior aplicó exclusivamente CT615. Las Notes del resto siguen sin aplicar.
El bloqueo global descrito a continuación es histórico. `terraform validate` PASS. El plan completo
propone actualizaciones de descripción **y tags** en los 17 CT: elimina las
etiquetas IP y cambia algunas etiquetas por diferencias de mayúsculas/formato.
No propone crear, destruir ni recrear recursos. La política exige solo descripción,
por lo que no se ejecutó apply.

[Revisión del plan](../roadmap/evidence/2026-11-06-d045-plan-review.json) y
[detalle de tags](../roadmap/evidence/2026-11-06-d045-tag-drift.json).
Plan binario, JSON completo y logs permanecen privados en
`~/.local/share/mailerblend-recovery/inventory-d045/`; pueden contener credenciales.
No versionarlos ni pegar su contenido.

Se preparó `inventory/notes-preserve-tags.proposed.tfvars.json`, usando el override
**ya existente** `recovery_preserve_service_tags`. No se carga automáticamente ni
se ha utilizado para aplicar. Propuesta pendiente de autorización: conservar todos
los tags reales y generar un nuevo plan limitado a Notes, sin autorizar cambios
de etiquetas. El estado de etiquetas es una captura que debe verificarse otra vez.

Después de autorizar esa propuesta, preparar un **nuevo** plan completo privado:

```bash
# Crear el directorio privado con permisos 0700 y trabajar con umask 077.
umask 077
terraform plan -input=false -var-file=inventory/notes-preserve-tags.proposed.tfvars.json -out="$HOME/.local/share/mailerblend-recovery/inventory-d045/approved-notes.tfplan"
terraform show -json "$HOME/.local/share/mailerblend-recovery/inventory-d045/approved-notes.tfplan" > "$HOME/.local/share/mailerblend-recovery/inventory-d045/approved-plan.json"
python3 scripts/validate-lxc-notes-plan.py "$HOME/.local/share/mailerblend-recovery/inventory-d045/approved-plan.json" --report docs/roadmap/evidence/d045-approved-plan-review.json
```

Revisar el reporte: únicamente `update` de `description`, con valores idénticos
al inventario generado y sin atributos desconocidos. Ante cualquier otra diferencia,
detenerse y consultar. Solo tras PASS puede aplicarse **ese mismo plan guardado**;
la autorización inicial no cubre el plan bloqueado actual. Respaldar estado y notas
actuales antes de aplicar. Después, comprobar Notes exactas, configuraciones PVE,
boot IDs, IDs/StartedAt/RestartCount de todos los contenedores, y un nuevo plan.
En el procedimiento global D045 no usar `-target`, `make deploy-all` ni ignorar
diferencias para eludir la revisión. D046 autorizó después una intervención
exclusiva CT614 con plan dirigido, validado y aplicado; no habilita otros CT.

La captura inicial privada está en
`~/.local/share/mailerblend-recovery/inventory-d045/before.json`;
la evidencia filtrada versionada permite comparar los 17 CT. No hubo apply en D045. D046 posterior aplicó exclusivamente las Notes CT614,
con respaldo y comprobaciones documentadas en su runbook.

## Información pendiente

- Entorno formal, responsable operativo y repositorios de aplicaciones.
- Funcionalidad extremo a extremo, dependencias externas y alertas específicas.
- CT 613: aplicación hola declarada pero no observada activa.
- CT 610: función del Alertmanager adicional `eloquent_ganguly`.
- CT 623/624/625/626: propósito y necesidad de `test-nginx`.
- Discrepancia documental de dominio CT 61211/618 y tamaños de disco declarados.
- CT 615: incidencia de salud preexistente; CT 614: prevención de caducidad y prueba
  GA4 funcional pendientes en Issue #1. No certificar funciones por health HTTP.

Sin cambios de CPU/RAM/disco/red, aplicaciones, contenedores, proxy/DNS ni reinicios.
Cambios locales previos EVA/Gestoría/Journal preservados. Sin commits ni pushes.
