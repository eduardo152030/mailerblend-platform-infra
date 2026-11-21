# 11 — Creación y trazabilidad de issues

Aplica cuando se solicita registrar trabajo en GitHub o se identifica un
pendiente independiente. Rige para Codex, Cline y otros agentes. El vínculo
plan o issue → worktree → rama → PR se rige por [la regla 03](03-git-workflow.md).

## Flujo

1. Leer AGENTS, ROADMAP, CURRENT-STATUS y las decisiones o runbooks aplicables.
   Revisar inventario o evidencia suficiente para distinguir una observación
   de una propuesta. Verificar el repositorio remoto antes de publicar.
2. Buscar por servicio, VMID y términos del síntoma o capacidad con
   `gh issue list --state all --search "<términos>"`. Reutilizar y enlazar
   un issue abierto que ya cubra el trabajo. Si se cerró con alcance distinto,
   enlazarlo y explicar la diferencia. Comentar o reabrir solo si se pidió.
3. Elegir tipo, prefijo y etiqueta existente. Especificar fase, dominio y
   prioridad en el cuerpo. Usar prioridad media salvo justificación.
   Dominios habituales: Proxmox/IaC, CRM, observabilidad, plataforma de
   conocimiento, correo, seguridad y recuperación, y documentación.
4. Crear con el formulario equivalente de GitHub si existe. Para CLI,
   preparar el Markdown con el esquema de abajo y pasarlo con
   `gh issue create --repo <org/repo> --title "<prefijo>: <título>" --body-file <archivo> --label <etiqueta>`.
   Consultar `gh label list` antes de aplicar etiquetas. Usar las etiquetas
   existentes. La creación de una taxonomía nueva es una tarea separada.
5. Verificar número, URL, título, etiquetas y estado mediante
   `gh issue view <N> --json number,url,title,labels,state`. Entregar los enlaces
   y dependencias reales. Crear un issue registra el trabajo. La ejecución
   conserva las autorizaciones y guardas del repositorio.

| Tipo | Prefijo | Etiqueta habitual |
|---|---|---|
| Incidencia | `fix:` | `bug` |
| Capacidad | `feat:` | `enhancement` |
| Operación o investigación | `chore:` | `enhancement` o `question` |
| Mejora técnica | `refactor:` | `enhancement` |
| Documentación | `docs:` | `documentation` |

Investigar vulnerabilidades y exposiciones sensibles por el canal privado
autorizado. Excluir secretos, dumps íntegros y datos privados de issues y PR.

## Plantilla de cuerpo

```markdown
## Resumen
<resultado que se busca>

## Contexto y evidencia
<estado actual, fase, VMID o servicios y enlaces verificados>
<si es incidencia, comportamiento esperado y reproducción segura>

## Alcance y límites
<cambios previstos, exclusiones y autorizaciones necesarias>

## Criterios de aceptación
- [ ] <resultado verificable>
- [ ] <pruebas, documentación y evidencia de producción si aplica>

## Clasificación y relaciones
- Tipo:
- Dominio:
- Prioridad:
- Estado inicial: TODO
- Relación: Depends on #N, Part of #N o Related to #N si aplica
```

Usar `Closes #N` en el PR que satisfaga todos los criterios. Para entregas
parciales, usar `Part of #N`; para contexto, `Related to #N`. La fusión de
documentación o código local no acredita despliegue ni aceptación en producción.

Un plan versionado sigue siendo válido para ajustes pequeños, urgentes o
de una ronda existente. Registrar trabajo futuro independiente en GitHub y
enlazarlo desde el roadmap cuando corresponda. ROADMAP, CURRENT-STATUS,
DECISIONS y los planes versionados conservan sus funciones.
