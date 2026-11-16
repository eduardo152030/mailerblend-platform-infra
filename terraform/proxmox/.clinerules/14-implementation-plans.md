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
despliegue se almacenan en `docs/roadmap/planes/` junto al roadmap, la
estatal y las decisiones. Este directorio es la fuente única de verdad
para el estado de la infraestructura.

## Naming obligatorio

El nombre del archivo debe identificar la feature/dominio/CT sin necesidad
de abrirlo. Formato `UPPER-KEBAB-CASE` con sufijo descriptivo:

```text
docs/roadmap/planes/CT624-PILOT-EXECUTION.md              ✅
docs/roadmap/planes/CPU-CONTRACT.md                        ✅
docs/roadmap/planes/INCREMENTAL-INTEGRATION.md             ✅
docs/roadmap/planes/PROGRESSIVE-ROLLOUT.md                 ✅
docs/roadmap/planes/PHASE6-D055-UPTIME-PROPOSAL.md         ✅
docs/roadmap/planes/CT614-SGTM-D043.md                     ✅
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
2. Incluir la versión (`-V1`, `-V2`) solo cuando existan o existierones
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

- `docs/roadmap/planes/ROADMAP.md` — visión general de fases.
- `docs/roadmap/planes/CURRENT-STATUS.md` — estado actualizado del rollout.
- `docs/roadmap/planes/DECISIONS.md` — decisiones técnicas aprobadas.
- `docs/runbooks/planes` — procedimientos operativos (documentación de proceso,
  no planes de implementación).
- `docs/plans/` — no existe en este repo; no crearlo.

## Estado actual (al crear esta regla)

Los planes de ejecución y propuestas de este repositorio viven en
`docs/roadmap/`. Ejemplos vigentes:

- `docs/roadmap/planes/CT624-PILOT-EXECUTION.md` — piloto validado.
- `docs/roadmap/planes/CPU-CONTRACT.md` — contrato CPU aceptado.
- `docs/roadmap/planes/INCREMENTAL-INTEGRATION.md` — preparación rollout.
- `docs/roadmap/planes/PROGRESSIVE-ROLLOUT.md` — política rollout progresivo.
- `docs/roadmap/planes/PHASE6-D055-UPTIME-PROPOSAL.md` — propuesta fase 6.
- `docs/roadmap/planes/CT614-SGTM-D043.md` — ejecución CT614.

## Worktree y plan de la tarea

Antes de guardar un plan, abre o retoma el worktree y la rama de la tarea
según `03-git-workflow.md`. Crea el plan en ese worktree, en la ruta que
define esta regla, y registra en él la rama de la tarea.

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

El PR debe identificar la ruta y la versión del plan que se aprobó. El plan
puede actualizarse con resultados y evidencias después de la implementación.

## Desviaciones

Si durante la implementación cambia el alcance o un criterio de aceptación,
registra la desviación en el plan y obtén aprobación antes de darla por
válida. Sin aprobación explícita, la desviación no se considera válida.

## Tareas de solo planificación

Si el encargo es solo planificar, la entrega sigue siendo el documento del
plan y la implementación queda pendiente. El plan debe marcarse como
"propuesto" hasta que el usuario lo apruebe.