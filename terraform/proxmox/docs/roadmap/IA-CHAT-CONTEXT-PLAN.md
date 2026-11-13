# IA-CHAT — contexto de Gemma y evolución pendiente

13 de noviembre de 2026, Europe/Madrid. Fase 7. IaC Reliability, Security & Disaster Recovery.
Documentación operativa DONE; ampliación de contexto TODO, sin despliegue autorizado.

## Cómo usarlo ahora

Gemma dispone de **8192 tokens de contexto por conversación** en el perfil actual.
Ese presupuesto incluye instrucciones, historial enviado, documentos recuperados y
respuesta; no equivale a 8192 tokens disponibles exclusivamente para tus mensajes.

Conviene usar **chats cortos y temáticos**, organizarlos en carpetas y recuperar los
anteriores mediante la búsqueda del historial. Al cambiar de tema, abre otro chat;
para continuar un trabajo largo, guarda un resumen de objetivos, decisiones y datos
imprescindibles y úsalo al iniciar el siguiente.

El historial guardado en Open WebUI no se borra al agotar el contexto ni al descargar
el modelo. Sin embargo, guardarlo no significa que Gemma lo esté viendo completo.
Las carpetas organizan chats y la búsqueda permite encontrarlos: **no añaden memoria
al modelo ni incorporan automáticamente otras conversaciones al prompt**.

Al acercarse al límite, parte del principio puede quedar fuera del contexto, o la
petición puede alcanzar el límite admitido por la ruta de chat. No se ha validado
el comportamiento exacto al llenar los 8192 tokens; no se promete truncado automático
ni recuerdo completo. La reserva de espacio para generar reduce el historial útil.
Un prompt más largo que deba procesarse suele aumentar el tiempo hasta el primer
token; la caché puede reducir ese coste, por lo que no todas las respuestas serán
necesariamente más lentas que la anterior.

## Por qué son 8k

CT 630 mantiene 22528 MiB de RAM. Gemma usa 16384 tokens totales repartidos entre dos
slots: 8192 por slot. Se redujo desde 65536 totales para habilitar SWA completa y
reutilizar el prefijo del historial dentro del margen de memoria. El template
versionado conserva los marcadores de pensamiento desactivado en el historial.
Qwen conserva 65536 totales, 32768 por slot; cambiar de modelo puede requerir carga
fría y no debe cargar ambos modelos simultáneamente.

Se comprobaron tres turnos con reutilización del prefijo y una prueba sintética de
3000 tokens; **no se certificó contexto lleno ni varios usuarios simultáneos**.
La guarda de pruebas exigió RSS/memoria residente inferior al 90 % del límite.
Las cifras y el coste de esta elección están en el
[informe de latencia](IA-CHAT-LATENCY-2026-11-13.md).

## Cómo abordarlo en el futuro

Estas opciones son propuestas TODO, no funcionalidades implantadas ni permisos
para cambiar producción. Primero hay que medir una conversación larga representativa.

| Opción | Qué resolvería | Qué falta comprobar |
|---|---|---|
| Resumen de continuidad manual | Trasladar decisiones importantes a un chat nuevo con poco contexto | Plantilla de resumen y revisión del propietario para no perder datos |
| Resumen automático controlado | Reducir historial sin depender de que el usuario lo resuma | Compatibilidad con v0.13.3, pérdida de información y coste; ejecutarlo explícitamente o fuera de la respuesta principal, sin reintroducir tareas competidoras |
| Recuperar documentos o notas por RAG | Incorporar fragmentos relevantes sin enviar todo el historial | Cobertura, citas, permisos y latencia; el historial de chats no se convierte automáticamente en una base RAG |
| Un solo slot con otro presupuesto de contexto | Investigar más contexto por conversación a costa de concurrencia | Compatibilidad SWA/KV, RAM real y caché; no asumir que cambiar parallel=1 basta ni que el margen está garantizado |
| Otro perfil/modelo o más capacidad de cómputo y memoria | Aumentar contexto útil o reducir lectura de prompts largos | Comparación de calidad en español, memoria, coste y TTFT; no hay compra ni ampliación de recursos aprobada |

## Criterios antes de aplicar una solución

1. Reproducir desde la ruta real de Open WebUI con conversación larga, documentos y
   preguntas sobre datos del principio, mitad y final. Registrar tokens enviados,
   reutilizados y nuevos, exactitud y tiempo hasta el primer token.
2. Probar por separado cada cambio con los mismos pesos y condiciones; registrar
   memoria residente/RSS, swap y memory.events. Mantener la guarda de RAM y un solo
   modelo grande cargado. Verificar qué ocurre realmente al llenar el contexto.
3. Mantener el objetivo de chat corto en caliente de 10 s y tras cinco minutos de
   inactividad de 15 s. Publicar por separado los tiempos de prompts largos y RAG.
4. Preservar historial, backups y rollback; declarar el perfil en IaC y verificar
   idempotencia, caché y calidad. Solicitar autorización del alcance antes de
   desplegar cambios de recursos, slots o servicios. CT 627 y otros CT quedan fuera.

Siguiente paso: recoger un caso largo del propietario y preparar una comparación
sin modificar producción. La Fase 7 global sigue IN PROGRESS; UAT móvil/voz,
reservas DHCP, restauración funcional y recepción humana de Telegram siguen abiertas.
