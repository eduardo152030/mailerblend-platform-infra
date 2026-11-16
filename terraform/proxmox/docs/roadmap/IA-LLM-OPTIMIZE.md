# IA-LLM-OPTIMIZE — optimizaciones de inferencia en CPU (CT 630)

Estado: **PENDIENTE / BACKLOG (TODO)**.
Fase 7. IaC Reliability, Security & Disaster Recovery.
Registro: 13 de noviembre de 2026, Europe/Madrid.
Alcance de esta intervención: solo registrar la tarea; **no ejecutar** pruebas,
descargas, despliegues, cambios de CT ni configuración. Sin commit ni push.

## Contexto y metodología obligatoria

Fuera de la sesión se revisaron recomendaciones externas de Gemini. Se aceptan
como candidatas para PROBAR, no como compatibilidad demostrada ni adopción aprobada.
No se ha verificado ni ejecutado ninguna de estas propuestas al registrar la tarea.

Línea base: resultados finales de
[IA-CHAT-LATENCY-2026-11-13](IA-CHAT-LATENCY-2026-11-13.md).

| Modelo | b / ub | pp512 tokens/s | pp2048 tokens/s | tg128 tokens/s | Contexto por conversación |
|---|---|---:|---:|---:|---:|
| Gemma | 2048 / 512 | 18,95 | 17,81 | 8,22 | 8192 |
| Qwen | 512 / 512 | 27,15 | 26,47 | 5,26 | 32768 |

Para cada candidato: medición antes/después con llama-bench, **3 repeticiones** de
pp512, pp2048 y tg128; TTFT con prompt de **3000 tokens** y por la ruta real de
Open WebUI, siguiendo la metodología del informe de latencia. Mantener generación
con 3 hilos y lectura con 4, salvo prueba explícita documentada.
Guarda **RSS < 90 %** del límite y **MemAvailable del host ≥ 21 GiB antes de cargar**;
registrar también memoria residente, caché reutilizada, swap y memory.events.
No aplicar cambios sin medición comparativa, preservación de datos y rollback.
CT 627 y otros CT quedan excluidos; no cambiar recursos del host para superar guardas.

## Subtareas por prioridad

Todas están en **TODO / BACKLOG**. Compatibilidad y tamaños indicados son hipótesis
aportadas para evaluar, no hechos comprobados en esta intervención.

| # | Prueba | Objetivo | Criterio de aceptación |
|---|---|---|---|
| 1 | KV cache `q8_0` en K y V más flash attention en CPU, por modelo | Subir Gemma a 16384 o 32768 tokens por conversación dentro de la guarda | Contexto mayor sin perder más del 5 % de pp/tg frente a la línea base; prefijo reutilizado en tres turnos reales de UI. Si flash attention empeora pp en CPU, probar KV q8_0 sin ella si la versión lo admite; documentar incompatibilidad si no |
| 2 | Alias de router `qwen3.6-35b-code` **sin mmproj**, para agentes | Investigar liberar ~0,9 GB y destinarlos a contexto | Alias operativo, RSS medida y contexto máximo seguro documentado. Mantener el alias con visión para Open WebUI y un solo modelo grande residente |
| 3 | `-ub 1024` en Qwen, con `-b 1024` y `-b 2048` | Mejorar lectura de prompts largos | Adoptar únicamente si mejora pp2048 **y reduce el TTFT de 3000 tokens al menos un 5 %**, dentro de la guarda |
| 4 | ik_llama.cpp, release fijado y AVX2, en instalación paralela sin sustituir el servicio | Evaluar MoE en CPU | Comparar pp/tg con los mismos GGUF; verificar visión de Gemma 4 y tool calling de Qwen. Adoptar solo con mejora ≥ 10 % y sin perder funciones. No cargar simultáneamente dos modelos grandes |
| 5 | `mmproj` Q8_0 para Gemma, si existe repositorio fiable | Investigar ahorro de ~0,6 GB | Verificar procedencia y hashes; misma prueba de visión «PRUEBA 4821» y captura real con texto pequeño, sin pérdida apreciable |
| 6 | Decodificación especulativa con MTP de Qwen3.6: `unsloth/Qwen3.6-35B-A3B-MTP-GGUF`, si llama.cpp lo soporta | Mejorar generación tg | Confirmar soporte de la versión. Descarga extra estimada de ~18 GB: **pedir confirmación antes de descargar**. Adoptar solo si tg mejora ≥ 15 % sin superar la guarda |

Los porcentajes se calculan contra la línea base del modelo y se publican para
pp512, pp2048, tg128 y TTFT; no sustituir una regresión de TTFT por una mejora de
benchmark aislada. Conservar resultados fallidos y motivo de descarte.

## Descartadas en este backlog

- `-t 4` para generación: las mediciones previas de IA-CHAT favorecen 3 hilos:
  Gemma 7,96 frente a 6,38 tokens/s; Qwen 5,13 frente a 4,42. Son la comparación
  histórica de hilos, distinta de la matriz final de batch/ubatch de la tabla base.
- HugePages / mlock: ganancia externa estimada del 3–7 % frente a bloquear ~18 GB
  en un host compartido con unos 25 CT. Estimación y referencia de capacidad aportadas;
  no verificadas de nuevo al registrar la tarea.
- `--cpu-moe`: descartado para este despliegue CPU; la recomendación corresponde
  a reparto CPU/GPU y no aporta el objetivo solicitado en este perfil sin GPU.

## Dependencias y entregables al ejecutar

La subtarea 2 es un **prerrequisito recomendado** del piloto de agente de código:
comparación Cline frente a Aider frente a OpenCode. No inicia ni autoriza ese piloto.
Relacionada con el [plan de contexto de Gemma](IA-CHAT-CONTEXT-PLAN.md).

Entregar `docs/roadmap/IA-LLM-OPTIMIZE-<fecha>.md` con tabla antes/después por subtarea,
compatibilidades, decisiones **adoptado / descartado y motivo**, memoria y evidencias.
Solo los cambios aceptados tras medir pasarán a configuración final versionada
siguiendo el patrón IaC; actualizar el README operativo y verificar idempotencia.
Distinguir preparación local, pruebas, despliegue y aceptación. No marcar DONE por
preparar archivos; exigir resultados verificables y conservar los pendientes de UAT.

Siguiente paso: programar la evaluación y confirmar alcance de ejecución antes de
iniciar pruebas. La Fase 7 global continúa IN PROGRESS. Este registro no autoriza
aplicar ninguna recomendación ni descargar MTP.
