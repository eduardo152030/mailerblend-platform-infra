# 15 — Cierre de tarea: commits y verificación

## Flujo de cierre

Antes de cerrar la tarea, confirma que estás en la rama y el worktree
asignados por `03-git-workflow.md`. Abre el plan creado según
`14-implementation-plans.md` y compara su alcance con el diff real.

## Pasos

1. **Verificar worktree y rama.** Confirma que estás en el worktree y la rama
   asignados por `03-git-workflow.md`:
   ```bash
   git worktree list
   git branch --show-current
   ```

2. **Comparar plan con diff.** Abre el plan y verifica que cada cambio
   planificado aparece en `git diff` (o `git diff --cached` si ya está staged).
   Si hay cambios en el diff que no están en el plan, añádelos al plan o
   exclúyelos del commit.

3. **Actualizar plan.** Actualiza el plan con lo ejecutado, las validaciones
   y los pendientes. Si la tarea fue solo planificación, marca el plan como
   "aprobado" o "propuesto" según corresponda.

4. **Staging explícito.** Haz staging solo de los archivos de esta tarea:
   ```bash
   git add <archivo1> <archivo2> ...
   ```
   No incluyas archivos de otras tareas ni cambios ajenos.

5. **Verificar sin errores.** Antes de commitear, verifica que no hay
   trailing whitespace ni problemas de line endings:
   ```bash
   git diff --cached --check
   ```
   Si hay errores, corrígelos antes de continuar.

6. **Commit.** Crea el commit con un mensaje descriptivo que identifique la
   tarea y el servicio/CT si corresponde:
   ```bash
   git commit -m "docs(cline): <descripción del cambio>"
   ```
   Si hay múltiples commits, agrúpalos por alcance funcional (como indica
   `03-git-workflow.md` sección 3).

7. **Verificar worktree limpio.** Al final, el worktree no debe conservar
   cambios propios sin explicar:
   ```bash
   git status --short
   ```
   Si hay archivos untracked no deseados, elimínalos o añádelos al `.gitignore`.

## Tareas de solo planificación

Si la tarea es solo planificación (sin cambios de código), el commit incluye
únicamente el archivo del plan y cualquier documentación asociada. El mensaje
de commit debe indicar claramente que es un plan:
```bash
git commit -m "docs(roadmap): add <plan-name> plan"
```

## Dos IA trabajando en paralelo

Cuando dos IA trabajan en paralelo en worktrees distintos:
- Cada una hace staging y commit solo de sus archivos.
- Si ambas tocan el mismo archivo, coordina el orden de integración.
- El aislamiento Git separa los archivos y el staging. Coordina aparte las
  operaciones que compartan estado o infraestructura.

## Relación con otras reglas

- `03-git-workflow.md` — define worktree y rama por tarea.
- `14-implementation-plans.md` — define ubicación y naming del plan.
- `00-reasoning.md` — principio IaC-only (ningún cambio manual en producción).