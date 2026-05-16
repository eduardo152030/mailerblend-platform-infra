# Guía de uso — EVA, tu asistente personal

EVA es tu asistente personal en Telegram. Habla con ella en español natural — no necesitas comandos exactos ni sintaxis especial.

---

## Qué puede hacer EVA

- Recordarte cosas a una hora concreta
- Avisarte cada X minutos hasta que confirmes
- Repetir recordatorios diarios, semanales o solo entre semana
- Guardar tareas sin fecha para cuando puedas
- Capturar links, fotos y documentos como tareas
- Gestionar ideas de contenido (YouTube, LinkedIn, TikTok)
- Enviarte un resumen diario a las 8:00
- Avisarte si llevas días sin publicar en un canal

---

## Recordatorios simples

```
eva, recuérdame fichar a las 9
recuérdame comprar leche a las 19:30
mañana recuérdame llamar al médico a las 10
el viernes recuérdame revisión semanal a las 9
```

EVA confirma el recordatorio y te dice la hora. Si la hora es incorrecta:
```
no, a las 11:30
```

---

## Recordatorios persistentes (con reintento)

Para cosas que necesitas confirmar antes de que EVA deje de insistir:

```
recuérdame fichar a las 8:40 cada 5 minutos hasta las 9:00
recuérdame lavarles los dientes a los niños a las 19:55 cada 5 minutos hasta las 20:15
recuérdame tomar la medicación a las 8:00 cada 10 minutos hasta las 8:30
```

EVA te avisará cada X minutos. Cuando lo hayas hecho, responde:
```
listo
```

EVA lo marca como completado y programa el próximo aviso para mañana a la misma hora.

---

## Recordatorios recurrentes

```
cada lunes recuérdame revisión semanal a las 9
cada viernes recuérdame cerrar la semana a las 17
recuérdame fichar de lunes a viernes a las 8:40 cada 5 minutos hasta las 9:00
```

---

## Confirmar, posponer o cancelar

### Confirmar que ya lo hiciste
```
listo
ok
hecho
ya está
```

### Posponer
```
en 10 minutos
en 1 hora
luego
mañana
a las 11
```

Con nota:
```
a las 13:00, confirmar con Luis antes
```

### Cancelar por ID
```
eva, cancela el 28
```

### Editar hora
```
eva, cambia el 28 a las 11:00
```

### Listar tus recordatorios
```
eva, lista mis recordatorios
mis recordatorios
qué tengo pendiente
```

---

## Tareas sin fecha

Para cosas que tienes que hacer pero no sabes cuándo:

```
tengo que revisar el router
hay que actualizar el certificado
pendiente: migrar la base de datos
debo llamar a Hacienda
tarea: revisar el contrato
```

EVA las guarda en Focalboard como tarjetas pendientes. Puedes asignarles fecha desde la UI cuando tengas un momento.

Si llevas más de 7 días sin gestionar una tarea, EVA te avisará automáticamente a las 9:30.

---

## Capturar links

Pega un link solo y EVA lo guarda como tarea:
```
https://example.com
```

EVA crea: "Revisar example.com"

Con contexto adicional:
```
https://portal.discover.com
revisar el apartado de analytics
```

El texto después del link se guarda como nota de la tarea.

---

## Fotos y screenshots

Envía una foto directamente a EVA. La guarda como tarea con el screenshot adjunto.

Con caption:
```
[foto] revisar este error
```

Para guardarla como idea de contenido:
```
[foto] #contenido
[foto] idea para video #contenido #NT
```

---

## Documentos y PDFs

Adjunta un PDF o documento y EVA lo guarda como adjunto de la tarea más reciente.

---

## Ideas de contenido

Añade `#contenido` a cualquier mensaje para guardarlo en el board de contenido:

```
idea para video sobre trading con volumen #contenido #tradeintuit
https://cline.bot/ #contenido #NT
[foto] hook para TikTok #contenido #mailerblend
```

### Proyectos disponibles
| Tag | Proyecto |
|---|---|
| `#mailerblend` | Proyecto Mailerblend |
| `#NT` | Núcleo Tecnológico |
| `#personal` | Personal |
| `#tradeintuit` | TradeIntuit |
| `#sage` | Proyecto SAGE |

### Formatos detectados automáticamente
Incluye "youtube", "short", "reel" o "linkedin" en el texto para asignar el formato.

---

## Hashtags y etiquetas

Los hashtags se extraen automáticamente del texto:

```
revisar configuración nginx #sage #producción
```

Se guardan como tags de la tarea en Focalboard.

---

## Operaciones por ID

Cuando EVA confirma una acción, incluye el ID entre corchetes `[28]`. Úsalo para operar directamente:

```
28 cancelala
28 complétala
28 en progreso
28 posponla para el lunes a las 10
28 agrégale una nota: esperando respuesta de soporte
28 cámbiala a nuevo nombre: revisar logs de producción
```

---

## Preguntas sobre tus recordatorios

```
qué tengo mañana
cuándo tengo la revisión semanal
tengo algo el viernes
```

---

## Resumen diario

Todos los días a las 8:00 EVA te envía un resumen de lo que tienes para hoy, incluyendo contexto de lo que pospusiste ayer. El tono sigue tu configuración de personalidad.

---

## Recordatorios de publicación

Si configuras canales de publicación (LinkedIn, YouTube, TikTok), EVA te avisa a las 9:00 cuando llevas más días de lo esperado sin publicar.

---

## Focalboard — la UI

Puedes gestionar tus tareas visualmente desde la UI (Lovable). Los cambios que hagas allí (cambiar estado, fecha, etc.) se sincronizan automáticamente con EVA cada 60 segundos.

Cuando EVA detecta un cambio desde la UI, te notifica por Telegram:
```
✅ "Revisar servidor" completado desde la UI (https://eva-flow.lovable.app) [42]
📅 Fecha actualizada desde la UI: "Llamar al médico" [38]
    Nueva fecha: lunes 19/05 a las 10:00
```

---

## Comportamiento esperado

### Cuando EVA no entiende
```
No te entendí del todo. Prueba con:
- eva, recuérdame en 2 minutos probar sistema
- eva, lista mis recordatorios
...
```

### Cuando mandas un link con contexto
EVA puede preguntar:
```
Veo que me pasaste un link. ¿Quieres que lo guarde como recordatorio o necesitas ayuda con algo relacionado?
```
Responde: `es un recordatorio` o `guárdalo`

### Cuando hay un aviso activo
Si EVA ya te envió un recordatorio y mandas una hora:
```
en 20 minutos
a las 11
```
EVA lo interpreta como snooze — no crea un nuevo recordatorio.

---

## Solución de problemas básica

**EVA no responde**  
Verifica que el bot esté activo. Si la IP del servidor cambió, puede haber un problema de webhook. Normalmente se resuelve solo en minutos.

**El recordatorio no llegó a la hora correcta**  
Di `no, a las HH:MM` justo después de la confirmación para corregirlo.

**Guardé algo pero no aparece en Focalboard**  
El sync tarda hasta 60 segundos. Espera un momento y recarga la UI.

**Quiero eliminar todo lo completado**  
```
elimina todas las completadas
elimina todas las canceladas
elimina todas las completadas y canceladas
```

**El recordatorio persistente no para**  
```
eva, cancela el [ID]
```
O márcalo como completado desde la UI de Focalboard.

---

## Ejemplos de sesión completa

```
Tú:   recuérdame fichar a las 8:40 cada 5 minutos hasta las 9:00
EVA:  ✅ Anotado [175]: "Fichar entrada" — hoy a las 08:40
      🔁 Repetiré cada 5 min hasta las 09:00 o hasta "listo".

(a las 8:40)
EVA:  ⏰ Ficha la entrada [175]. Di "Listo" cuando lo hayas hecho.

Tú:   listo
EVA:  ✅ Perfecto. Próximo aviso: mañana lunes a las 08:40.

---

Tú:   https://stockstotrade.com/market-updates #tradeintuit
EVA:  📌 Apuntado en Focalboard: "Revisar stockstotrade.com"
      Cuando tengas un momento, asígnale fecha desde la UI.

---

Tú:   [foto con caption "#contenido idea para TikTok sobre gaps de apertura"]
EVA:  💡 Idea de contenido guardada [203]: "idea para TikTok sobre gaps de apertura"
      🖼️ Screenshot adjunto.
      📋 Estado: Idea → /contenido

---

Tú:   qué tengo mañana
EVA:  Mañana tienes: fichar entrada a las 08:40, revisión semanal a las 09:00
      y lavarles los dientes a los niños a las 19:55.
```

---

## Limitaciones conocidas

- EVA es un asistente personal — diseñada para un solo usuario principal
- Los recordatorios necesitan una hora concreta para dispararse; sin hora se guardan como tareas sin fecha
- El reconocimiento de intención puede fallar ocasionalmente con mensajes muy ambiguos; en ese caso re-escribe el mensaje de forma más directa
- Los archivos adjuntos tienen un límite de 20MB