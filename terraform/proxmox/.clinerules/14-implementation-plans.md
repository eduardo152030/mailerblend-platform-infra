# 14 — Implementation plans: ubicación y naming en repositorio de infraestructura

## Regla principal

Cada vez que una tarea requiera crear un **implementation plan** (plan de
implementación aprobado o propuesto, sea generado por el agente o por el
usuario), ese plan DEBE vivir en:

```text
docs/roadmap/planes/
```

Nunca en la raíz del repo, nunca en `reasoning-content/`, nunca suelto junto
al código (`terraform/`, `scripts/`, `tests/`), nunca como archivo
temporal "que luego se mueve".

Los planes de ejecución, propuestas, contratos y preparaciones de
despliegue se almacenan en `docs/roadmap/planes/` junto al roadmap, el estado actual y las decisiones. El estado de la
infraestructura se registra en el roadmap y CURRENT-STATUS.md.

## Naming obligatorio

El nombre del archivo debe identificar la feature/dominio/CT sin necesidad
de abrirlo. Formato `UPPER-KEBAB-CASE` con sufijo descriptivo:

```text
docs/roadmap/planes/CLINE-LXC-SSH-PLAN.md
docs/roadmap/planes/CT618-SWAP-INCREASE.md
docs/roadmap/planes/PHASE7-D091-CHATTERBOX-CHUNKING-IMPL.md
```

Prohibidos los nombres genéricos:

```text
implementation_plan.md            ❌ (¿de qué?)
plan.md                           ❌
new_plan.md                       ❌
temp.md                           ❌
```

Reglas de naming:

1. Incluir el CT o servicio (`CT624-`, `CRM-`, `JOURNAL-`, `PHASE6-`)
cuando el nombre no sea obvio por sí solo.
2. Incluir la versión (`-V1`, `-V2`) solo cuando existan o existieron
versiones anteriores del mismo plan.
3. Usar sufijos descriptivos: `EXECUTION.md`, `PROPOSAL.md`, `PLAN.md`,
`RECOVERY.md`, `CONTRACT.md`, `PREPARATION.md`.
4. Mantener coherencia dentro de un mismo tipo de documento.

## Un plan por feature (evitar duplicados y conflictos de nombre)

- Antes de crear un plan nuevo, comprobar si ya existe uno para la misma
  feature/CT en `docs/roadmap/planes/` (y en decisiones relacionadas).
- Un plan aprobado es un **documento vivo**: se edita en el mismo archivo,
  actualizando su contenido, no se crea un archivo paralelo.
- Solo si un plan sufre un rediseño total se crea `*-V2-*.md`, dejando
  escrito en el nuevo (y en el viejo) cuál reemplaza a cuál.

## No se borran como efecto lateral

Los planes —incluso ya implementados— son el design rationale de record.
No se eliminan, mueven ni renombran como efecto lateral de tareas de
limpieza, refactors o triage. Solo se tocan si la tarea lo pide
explícitamente o con confirmación del usuario.

## Relación con otros documentos

- `docs/roadmap/ROADMAP.md` — visión general de fases.
- `docs/roadmap/CURRENT-STATUS.md` — estado actualizado del rollout.
- `docs/roadmap/DECISIONS.md` — decisiones técnicas aprobadas.
- `docs/runbooks/` — procedimientos operativos (documentación de proceso,
  no planes de implementación).
- `docs/plans/` — no existe en este repo; no crearlo.

## Worktree y plan de la tarea

Antes de guardar un plan, abre o retoma el worktree y la rama de la tarea
según `03-git-workflow.md`. Crea el plan en ese worktree, en la ruta que
define esta regla, y registra en él la rama, el worktree y la base de la
tarea. Un issue con el alcance y las comprobaciones puede sustituir al
plan versionado según la [regla 03](03-git-workflow.md).

Al retomar la tarea, reutiliza el mismo plan. Antes de cerrarla, actualízalo
con lo ejecutado, las validaciones y los pendientes. Para el cierre y los
commits locales, aplica `15-task-commit-closeout.md`.

## Contenido mínimo del plan aprobado

Un plan aprobado debe incluir, como mínimo:

- **Alcance.** Qué se va a cambiar y qué se excluye.
- **Criterios de aceptación verificables.** Cada criterio debe ser
  comprobable con una prueba o verificación concreta.
- **Pruebas requeridas.** Qué pruebas se ejecutarán y qué resultado se
  considera aceptable.
- **Ruta y versión del plan.** La ruta relativa al repositorio y la versión
  del documento que se aprobó.

Enlaza en el PR el issue o la ruta y revisión del plan. Registra la URL
del PR en la referencia de la tarea. El plan
puede actualizarse con resultados y evidencias después de la implementación.

## Desviaciones

Si durante la implementación cambia el alcance o un criterio de aceptación,
registra la desviación en el plan y obtén aprobación antes de darla por
válida. Sin aprobación explícita, la desviación no se considera válida.

## Tareas de solo planificación

Si el encargo es solo planificar, la entrega sigue siendo el documento del
plan y la implementación queda pendiente. El plan debe marcarse como
"propuesto" hasta que el usuario lo apruebe.
