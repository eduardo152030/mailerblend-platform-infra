# 00 — Reglas de acción directa y control de bucles

PRIORIDAD ALTA: Estas reglas controlan la ejecución, los reintentos,
la verificación y la detención de tareas. Toda tarea empieza con
la [regla 03](03-git-workflow.md). Los límites de reintentos respetan
las validaciones distintas que exige el plan, el issue o el runbook.

## 1. Ejecución directa

- Actúa de forma directa y decisiva.
- Antes de cada herramienta, expresa como máximo una frase breve indicando
  la siguiente acción.
- No narres deliberaciones internas, dudas hipotéticas ni alternativas
  que todavía no vas a ejecutar.
- No vuelvas a planificar una tarea salvo que aparezca información nueva
  que cambie materialmente el enfoque.
- Evita reescrituras completas Usa replace_in_file para cambios parciales. No reescribas archivos completos a menos de que sea necesario,  Sé conciso, sin introducciones ni resúmenes finales.

## 2. Uso de herramientas y verificación

- Confía en los resultados exitosos de las herramientas.
- Después de una edición exitosa, realiza como máximo una verificación
  dirigida por comprobación necesaria: `git diff`, una prueba concreta o una
  lectura del fragmento afectado.
- No releas un archivo únicamente para confirmar algo que una herramienta
  ya confirmó correctamente.
- No leas el mismo archivo más de dos veces en una tarea, salvo que:
  - el archivo haya cambiado;
  - la lectura anterior fuera parcial;
  - exista una contradicción concreta que deba resolverse.
- No repitas una llamada con los mismos argumentos después de un fallo.

## 3. Política anti-bucles

- Máximo tres intentos para el mismo error o bloqueo:
  un intento inicial y dos reintentos.
- Antes de cada reintento, identifica brevemente la causa probable.
- Cada reintento debe cambiar la estrategia, comando, ruta, herramienta
  o hipótesis.
- No realices un cuarto intento sobre el mismo bloqueo.
- Para procesos en segundo plano, consulta su estado como máximo dos veces.
  No hagas polling repetitivo.
  Para suites de tests/builds, la salida final del comando es
  autoritativa — ver `.clinerules/11-test-command-loop-prevention.md`.

## 4. Detención y reporte

Tras tres intentos fallidos, termina el turno y responde:

[FALLO DETECTADO]
Objetivo y bloqueo actual.

[INTENTOS REALIZADOS]

1. Enfoque y resultado.
2. Enfoque y resultado.
3. Enfoque y resultado.

[ACCIÓN REQUERIDA DEL USUARIO]
Información, permiso o acción concreta necesaria para continuar.

## 5. Registro de decisiones

- No registres cadenas internas de pensamiento.
- Registra únicamente decisiones técnicas, evidencia observada,
  acción ejecutada y resultado.
- No registres lecturas, listados ni acciones triviales.
- Escribe una sola entrada al terminar una decisión arquitectónica,
  un análisis de causa raíz o un cambio real de estrategia.
- Máximo cinco líneas por entrada.

Ubicación:

- Con task o Issue: `reasoning-content/MM-DD-YYYY_hh-mm-ss_Thinking_task_[NUMERO].md`
- Sin task o Issue: `reasoning-content/MM-DD-YYYY_hh-mm-ss_Thinking_task_DRAFT.md`

Formato:

## [Fecha y hora] — [Tarea]

- Decisión:
- Evidencia:
- Acción:
- Resultado: Éxito | Fallo | Pendiente

## 6. Principio IAC-only (Infrastructure-as-Code)

Este repositorio gestiona 17 contenedores LXC en Proxmox mediante Terraform.
**Nunca ejecutes comandos interactivos en producción.**

- **Prohibido**: `pct shell`, `ssh <service>`, `docker exec`, `vim`/`nano`
  en cualquier CT de producción.
- **Obligatorio**: todos los cambios deben ser declarativos (Terraform) o
  mediante scripts versionados en `scripts/`.
- **Excepción**: diagnóstico de lectura (`pct exec`, `ssh -o StrictHostKeyChecking=yes`)
  está permitido siempre que no modifique nada.
- **Ejemplo correcto**: para cambiar la configuración de un CT, edita el
  bloque correspondiente en `terraform/` y ejecuta
  `terraform apply -parallelism=1 -target=proxmox_virtual_environment_container.svc["<service>"]`.
- **Ejemplo incorrecto**: `ssh CT621 "systemctl restart nginx"`.
- Verifica idempotencia: una segunda aplicación sin cambios no debe recrear
  ni recargar servicios innecesariamente.
- No desactives verificación SSH/TLS ni modifiques la configuración SSH del
  propietario para eludir un bloqueo.
