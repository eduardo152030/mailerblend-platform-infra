# 10 — Diff diferencial de revisión

Cada tarea con cambios entrega un archivo `.diff` local junto con su PR.
La implementación inicial y cada ronda de correcciones tienen su propio
artefacto, aunque todas las rondas se publiquen en el mismo PR.

## 1. Registrar el punto de partida

Desde el worktree dedicado, antes de editar y tras cualquier sincronización
acordada, captura el SHA con `git rev-parse HEAD`. Regístralo en el plan o
issue con el alcance de la ronda. Usa `implementation` para la entrega
inicial y `review-01`, `review-02` y sucesivos para el feedback. Agrupa en
una ronda las correcciones solicitadas juntas.

En una corrección, comprueba el SHA del PR sobre el que llegó el feedback.
Si hay commits propios pendientes de una ronda anterior, aclara el alcance
antes de elegir la base. Conserva el SHA registrado si retomas una ronda
interrumpida. Si se actualiza la base Git, verifica que el intervalo elegido
siga aislando los cambios de la ronda.

## 2. Generar y comprobar el artefacto

Después del último commit de la ronda, incluidos los cambios de trazabilidad,
ejecuta desde el módulo Proxmox dentro del worktree:

```bash
git status --short
round_head=$(git rev-parse HEAD)
git diff --stat "$review_base" "$round_head"
git diff --name-status "$review_base" "$round_head"
git diff --check "$review_base" "$round_head"
```

`review_base` es el SHA registrado antes de editar. Comprueba que el
intervalo contiene los archivos de la ronda, incluidos los nuevos, y que
cada cambio pertenece al alcance. Revisa también el contenido del parche
antes de compartirlo para detectar secretos o datos privados. Si aparecen
cambios heredados, ajenos o artefactos anteriores, corrige el intervalo o
resuelve el alcance antes de entregar.

Guarda el artefacto en `reasoning-content/Diff/`, con el nombre
`MM-DD-YYYY_HH-MM-SS_diff_<tarea>_<ronda>.diff` y hora de Europe/Madrid.
Usa una ruta nueva para conservar los archivos ya entregados:

```bash
mkdir -p reasoning-content/Diff
review_stamp=$(TZ=Europe/Madrid date +%m-%d-%Y_%H-%M-%S)
review_path="reasoning-content/Diff/${review_stamp}_diff_${task_slug}_${review_round}.diff"
( set -C; git diff --no-ext-diff --no-textconv --binary "$review_base" "$round_head" > "$review_path" )
wc -l < "$review_path"
git status --short
```

Asigna `task_slug` y `review_round` antes de ejecutar el bloque. Mantén
el artefacto fuera del staging y de los commits salvo petición expresa.
El diff completo contra la base del PR se exporta solo si se solicita,
como un archivo adicional con sufijo `_FULL.diff`. Si se pide un ZIP o
export para revisión, incluye el diferencial de la ronda.

## 3. Excepción sin commit

Si el encargo impide hacer commit, conserva el mismo baseline y limita
el diff de trabajo a los archivos de la ronda. Revisa los cambios ajenos y
los archivos nuevos. Un diff del árbol de trabajo omite archivos untracked.
Incluye y verifica su contenido por separado o indica que el artefacto sigue
incompleto. Identifica la entrega como pendiente, con cambios sin commit.

## 4. Informe de revisión

Aplica la [regla 06](06-task-commit-closeout.md). Tras el enlace al PR,
indica la ronda, los SHA inicial y final, la ruta del `.diff`, el número
de archivos y líneas y el resultado de verificar el alcance. Para cambios
sin commit, identifica el extremo final como árbol de trabajo. El SHA final
de una entrega publicada debe coincidir con el SHA del PR verificado.
