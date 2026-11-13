# D083 — candidato local es/en; Chatterbox aún no activado

**NO DESPLEGADO.** D081 sigue siendo la versión productiva aceptada.
[Informe y límites](../../../docs/roadmap/PHASE7-D083-QWEN-ENGLISH-CHATTERBOX.md).
No hay comandos de ejecución de inferencia o despliegue automático en esta carpeta.

## Archivos y recorrido

- `patch.py`: se aplica sobre una copia exacta del backend D079 aprobado, no sobre
  un checkout arbitrario. Amplía las dos admisiones API a es/en y añade una consulta
  de capacidades que no importa modelos. No habilita Chatterbox en las rutas.
- `isolated_backend.py`: mantiene perfil real, semilla42, modelo0.6B, instrucciones
  desactivadas yjobs privados; persiste el idioma recibido en request.json.
- `agent.py`: valida el contrato es/en, conserva la cola serial, presupuesto y
  supervisor actuales. No despacha Chatterbox ni implementa otro servicio.
- `qwen_language_policy.py`: política ymapa explícito es→Spanish/en→English.
- `worker.py`: comprueba request/text, usa el nombre seleccionado al invocar Qwen
  ylo registra en checkpoint. Misma referencia/transcripción, FP32/SDPA/A/B/300/25.
- `ui/`: fuentes candidatas del fork8af7…; restringen idiomas Qwen, eligen0.6B/42
  por defecto yfiltran motores por capacidades antes de comprobar/descargar modelos.
  Chatterbox no se muestra porque el servidor candidato comunica ready=false.
- `engine_slot.py`: contrato de exclusión para un FUTURO worker, probado con un
  lock sintético. No es una implementación de Chatterbox ni un despliegue de sucola.
- `chatterbox-v3.proposed.json`: revisión/archivos obtenidos por metadata, sin pesos
  descargados. Lock de dependencias eimagen aún pendientes, no es unrelease listo.

La comprobación de protocolo usa los hashes delworker yde la política en app,
PVE ysrcCT. Evita aceptar inglés con unworker antiguo que fuerceSpanish. ElSHA
esperado debe regenerarse tras cualquier cambio candidato enworker.py yrevisarse;
no sustituir manualmente hashes para saltar una incompatibilidad.

## Pruebas sin inferencia

```sh
python3 -m unittest discover -s tests/voicebox -p test_d083.py
node --experimental-strip-types --test tests/voicebox/test_d083_ui.mjs
```

Los modelos son dobles de prueba: no se importa/carga Qwen real ni se usa la voz
personal. La integración llama al método Talker candidato, con referencias sintéticas,
y comprueba idioma, precisión,semilla,checkpoint yreferencia sin traducir. Los tests
UI ejecutan la política/lenguajes TypeScript; no sustituyen unbuild React completo.

Dockerfile es solo una preparación backend sobre la imagen aceptada D079.
**No se ha construido ni se debe desplegar como release de UI completa.** Es
necesario integrar ycompilar las fuentesUI contra el fork fijado, construir untag
candidato distinto yvalidar elconjunto, previa autorización. La compilación ylos
ensayos de audio no se han realizado enD083.

## Próximo despliegue propuesto, no autorizado en este paso

1. Backup coherente nuevo yverificado; conservar imágenes, fuentes ydatosD081/D082.
2. Build fuera de producción, conbase aprobada verificada porID, sin pip/npm flotante.
3. Validación API/UI completa ydobles antes de disponer eltag candidato para revisión.
4. Sinjobs activos, coordinar app+UI, agente+políticaPVE yworker+políticaCT. Cambiar
   únicamente esos componentes, manteniendo supervisor/guardas/recursos. La comprobación
   deprotocolo rechaza versiones mezcladas antes de crear/cargar workers.
5. Tras aprobación de despliegue yaudios: QwenEnglish corto literal yposterior
   verificación española. Una prueba simulada no prueba pronunciación oacento.
6. Chatterbox requiere otra evaluación: imagenCPU separada, descarga selectiva
   fijada ypresupuesto de disco/loader medido antes de cualquier generación. No
   añadirlo a lalista de motores aprobados para activar elbackend nativo in-process.

Rollback: restaurar imagenappD079, UI aceptada, agente/política ytargetsrc D081/D082
coordinadamente, concola vacía. No revertir BD ni borrar nuevos jobs/checkpoints;
los checkpoints históricos QwenSpanish se reconocen sin cambiar suformato.
