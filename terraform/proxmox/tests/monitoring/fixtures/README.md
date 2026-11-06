# Evidencias saneadas para el framework de Fase 4

`phase4-actual-incidents.json` selecciona únicamente IDs/nombres técnicos,
timestamps, contadores, límites y referencias SHA256 de evidencias del repositorio.
No contiene entornos, credenciales, configuración de aplicación ni datos de negocio.

- CT619: comparaciones cacheadas/actuales y extremos medidos reales; no se inventan timestamps de extremos ausentes.
- CT623: hueco de113,635s y contrato90s; la muestra original fallida no existe completa.
- CT617: bytes y timestamp reales del fallo, con ausencia de historia RAM explícita; no permite atribuir una causa única.
- CT61211: timestampRFC3339Nano exacto que terminó el lector.
- Control623: brackets Docker/cgroup reales y gauges cAdvisor. En el replay el ámbito se declara desde la procedencia del archivo, sin afirmar que se conservó su namespace kernel original.

Los datos sintéticos de pruebas de límites y corrupción se crean por separado en
los tests. Ningún replay retrospectivo equivale a desplegar o aceptar un CT.
