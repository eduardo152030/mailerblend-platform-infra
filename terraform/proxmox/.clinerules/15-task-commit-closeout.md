# 15 — Cierre de tarea: commits, PR y revisión

## Flujo de cierre

Cuando el alcance autoriza un PR, la IA implementadora lo abre y la IA
revisora lo verifica. Un encargo limitado al commit termina con el cierre local. Antes de cualquier acción, confirma que estás en la
rama y el worktree asignados por `03-git-workflow.md`. Abre el plan creado
según `14-implementation-plans.md` y compara su alcance con el diff real.

## IA implementadora

### 1. Verificar worktree y rama

Confirma que estás en el worktree y la rama asignados por
`03-git-workflow.md`:
```bash
git worktree list
git branch --show-current
```

### 2. Comparar plan con diff

Abre el plan y verifica que cada cambio planificado aparece en `git diff`
(o `git diff --cached` si ya está staged). Si hay cambios en el diff que no
están en el plan, añádelos al plan o exclúyelos del commit.

### 3. Actualizar plan

Actualiza el plan con lo ejecutado, las validaciones y los pendientes.
Si hay desviaciones, documentalas con la aprobación correspondiente.

### 4. Staging explícito

Haz staging solo de los archivos de esta tarea:
```bash
git add <archivo1> <archivo2> ...
```
No incluyas archivos de otras tareas ni cambios ajenos.

### 5. Verificar sin errores

Antes de commitear, verifica que no hay trailing whitespace ni problemas
de line endings:
```bash
git diff --cached --check
```
Si hay errores, corrígelos antes de continuar.

### 6. Commit

Si el alcance permite commits, crea el commit con un mensaje descriptivo que identifique la tarea y el
servicio/CT si corresponde:
```bash
git commit -m "docs(cline): <descripción del cambio>"
```
Si hay múltiples commits, agrúpalos por alcance funcional (como indica
`03-git-workflow.md` sección 3).

### 7. Verificar worktree limpio

Al final, el worktree no debe conservar cambios propios sin explicar:
```bash
git status --short
```
Si hay archivos untracked no deseados, elimínalos o añádelos al `.gitignore`.

### 8. Publicar rama y abrir PR

Publica la rama y abre el PR hacia `main` cuando ambas acciones estén
autorizadas. El PR debe incluir:

- **Referencia al plan aprobado.** Ruta y versión del documento.
- **Resumen del diff.** Qué archivos se tocan y por qué.
- **Pruebas ejecutadas.** Lista de pruebas con sus resultados (PASS/FAIL).
- **Desviaciones aprobadas.** Si las hay, con la aprobación registrada.

### 9. Entregar para revisión

Deja la integración pendiente de la revisión independiente y de las
comprobaciones requeridas. En el resumen final, indica:

- La **rama**.
- El **enlace al PR**.
- La **ruta del plan**.
- Los **hashes de los commits**.
- El **estado de las comprobaciones**.

La revisión la realiza **otra IA**, en una sesión separada. La IA
implementadora no aprueba su propio PR.

## IA revisora

### 1. Verificar worktree y rama

Confirma que estás en el worktree y la rama asignados por
`03-git-workflow.md`:
```bash
git worktree list
git branch --show-current
```

### 2. Obtener el plan aprobado

Abre el plan aprobado según `14-implementation-plans.md`. Extrae el
alcance, los criterios de aceptación y las pruebas requeridas.

### 3. Comparar diff real del PR con el plan

Revisa el diff real del PR y verifica que cada cambio planificado está
presente y que no hay cambios fuera del alcance aprobado.

### 4. Verificar cada criterio de aceptación

Para cada criterio de aceptación del plan:

- **CUMPLE.** El criterio se cumple y hay evidencia (resultado de prueba,
  verificación, enlace a log).
- **NO CUMPLE.** Falta un requisito, hay un cambio fuera del alcance
  aprobado o falta evidencia de una prueba obligatoria.

### 5. Decisión

- **APROBAR.** Si todos los criterios del plan se cumplen con evidencia.
  El PR está listo para integración.
- **SOLICITAR CAMBIOS.** Si falta un criterio, hay un cambio fuera del
  alcance aprobado o falta evidencia. En ese caso, indica:
  - El **criterio incumplido**.
  - El **archivo o la prueba** afectada.
  - Qué hace falta corregir.

Después de la corrección, revisa la nueva versión del PR antes de aprobar.

### 6. Registrar resultado

Actualiza el plan con el resultado de la revisión (aprobado o cambios
solicitados) y la evidencia correspondiente.

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

- `03-git-workflow.md` — define worktree, rama, PR y flujo de revisión.
- `14-implementation-plans.md` — define ubicación, naming y contenido del plan.
- `00-reasoning.md` — principio IaC-only (ningún cambio manual en producción).
