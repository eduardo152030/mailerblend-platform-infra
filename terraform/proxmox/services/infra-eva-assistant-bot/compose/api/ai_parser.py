"""
ai_parser.py v2 — Motor de IA central de EVA.
"""
import json
import os
import re
import traceback
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import httpx

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
AI_PARSER_ENABLED = os.getenv("EVA_AI_PARSER", "1") == "1"
MODEL = "claude-haiku-4-5-20251001"

def _now(): return datetime.now(TZ)

def _day_context(now):
    days = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    return (f"Ahora: {now.strftime('%Y-%m-%d %H:%M')} ({days[now.weekday()]}, Europa/Madrid)\n"
            f"Mañana: {(now+timedelta(days=1)).strftime('%Y-%m-%d')}\n"
            f"Pasado mañana: {(now+timedelta(days=2)).strftime('%Y-%m-%d')}")

async def _claude(system, user, max_tokens=512, messages=None, tools=None, tool_choice=None):
    if not ANTHROPIC_API_KEY: return None
    msgs = messages or [{"role":"user","content":user}]
    payload = {"model":MODEL,"max_tokens":max_tokens,"system":system,"messages":msgs}
    if tools: payload["tools"] = tools
    if tool_choice: payload["tool_choice"] = tool_choice
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key":ANTHROPIC_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
                json=payload)
            if r.status_code != 200:
                print(f"[ai] API {r.status_code}: {r.text[:200]}"); return None
            return r.json()
    except Exception as exc:
        print(f"[ai] error: {exc}"); return None

# ══════════ 1. DETECCIÓN DE INTENCIÓN ══════════

INTENT_SYSTEM = """Eres el clasificador de intenciones de EVA, asistente personal en español.
Clasifica el mensaje en UNA intención:
- create_reminder: crear recordatorio o aviso futuro
- cancel_reminder: cancelar/borrar un recordatorio específico (por ID, descripción o fecha: "cancela el 28", "borra el de mañana", "elimina lo que tengo el viernes")
- cancel_all_date: cancelar TODOS los recordatorios de una fecha o en general ("cancela todo lo de mañana", "borra lo que tengo el viernes", "puedes eliminarlos/cancelarlos" refiriéndose a un grupo)
- edit_reminder: cambiar hora/fecha/texto de un recordatorio
- ack_reminder: confirmar que ya hizo algo (listo, ok, vale, hecho, ya está)
- snooze_reminder: posponer aviso (en 10 minutos, luego, más tarde)
- list_reminders: ver lista de recordatorios pendientes
- pending_task: tarea SIN fecha (tengo que, pendiente, hay que, debo) — NO usar para preguntas ni cancelaciones
- question: pregunta sobre sus recordatorios (qué tengo mañana, cuándo es X, cuántos tengo)
- correction: corregir hora del último recordatorio (no, a las 11)
- admin_cleanup: limpiar duplicados, borrar recordatorios de prueba/test, limpiar Focalboard
- add_note: añadir nota/texto/contexto a la última tarea o recordatorio mencionado ("agrégale una nota", "añade que", "agrega esto")
- chat: conversación general, saludo, o mensaje no relacionado

Responde SOLO con JSON sin markdown: {"intent":"string","confidence":0.0-1.0,"hint":"razón breve","date_hint":"fecha mencionada en ISO si aplica o null"}"""

async def detect_intent(text, memory_context="", conversation_history=None):
    system = INTENT_SYSTEM
    if memory_context:
        system += f"\n\nContexto del usuario:{memory_context}"
    now = _now()
    prompt = f"{_day_context(now)}\n\nMensaje: '{text}'"
    # Incluir historial conversacional para entender referencias como "cámbialo", "muévelo"
    messages = []
    if conversation_history:
        for msg in conversation_history[-6:]:
            role = "user" if msg.get("direction") == "inbound" else "assistant"
            msg_text = msg.get("text", "")
            if msg_text and len(msg_text) < 500:  # Evitar mensajes muy largos
                messages.append({"role": role, "content": msg_text})
    messages.append({"role": "user", "content": prompt})
    # FIX: pasamos messages completo, el arg 'user' queda ignorado por _claude cuando messages!=None
    data = await _claude(system, prompt, max_tokens=120, messages=messages)
    if not data: return {"intent":"unknown","confidence":0.0}
    try:
        raw = data["content"][0]["text"].strip()
        # Extract first valid JSON object — ignore any trailing text or markdown
        # Find the first { and last } to extract clean JSON
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]
        result = json.loads(raw)
        intent = result.get("intent","unknown")
        conf = float(result.get("confidence",0.8))
        hint = result.get("hint","")
        print(f"[intent] '{text[:40]}' → {intent} ({conf:.2f}) — {hint}")
        return {"intent":intent,"confidence":conf,"hint":hint}
    except Exception as e:
        print(f"[intent] parse error: {e}, raw: {data['content'][0]['text'][:100]}")
        return {"intent":"unknown","confidence":0.0}

# ══════════ 2. PARSER DE RECORDATORIOS ══════════

PARSE_TOOL = {
    "name":"create_reminder",
    "description":"Extrae información estructurada de un recordatorio.",
    "input_schema":{
        "type":"object",
        "properties":{
            "task_text":{"type":"string","description":"Descripción concisa sin prefijos innecesarios."},
            "remind_at":{"type":"string","description":"ISO 8601: YYYY-MM-DDTHH:MM:00. Debe ser futuro."},
            "recurrence_type":{"type":"string","enum":["none","weekly","weekdays","interval"]},
            "recurrence_value":{"type":"string","description":"Día para weekly, minutos para interval, null para otros."},
            "is_persistent":{"type":"boolean"},
            "repeat_every_minutes":{"type":"integer"},
            "stop_at":{"type":"string","description":"ISO 8601 o null."},
            "weekdays_only":{"type":"boolean"},
            "mode":{"type":"string","description":"relative_minutes|today_or_tomorrow_at_time|tomorrow_at_time|weekly_day|weekdays|before_time|interval_minutes|absolute_date|next_weekday"}
        },
        "required":["task_text","remind_at","recurrence_type","is_persistent","weekdays_only","mode"]
    }
}

async def parse_reminder_ai(text, context=None, memory_context=""):
    if not AI_PARSER_ENABLED or not ANTHROPIC_API_KEY: return None
    now = _now()
    days = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    system = (f"{_day_context(now)}\n"
              f"Pasado mañana: {(now+timedelta(days=2)).strftime('%Y-%m-%d')}\n\n"
              f"Eres el parser de recordatorios de EVA. Extrae usando create_reminder.\n"
              f"Reglas: remind_at debe ser futuro. 'esta tarde'→PM. 'próximo X'→siempre siguiente semana. "
              f"task_text sin prefijos. Contexto tras coma va en task_text.\n"
              f"IMPORTANTE para recordatorios persistentes:\n"
              f"- Si dice 'cada X minutos' → is_persistent=true, repeat_every_minutes=X\n"
              f"- Si dice 'hasta las HH:MM' → stop_at=fecha+HH:MM:00 en ISO 8601\n"
              f"- Si dice 'todos los días' → recurrence_type=weekdays, weekdays_only=false\n"
              f"- Si dice 'días laborables'/'lunes a viernes'/'de lunes a jueves' → recurrence_type=weekdays, weekdays_only=true\n"
              f"- SIEMPRE incluir repeat_every_minutes y stop_at cuando se mencionan\n"
              f"{memory_context}"
              f"\nSi NO es un recordatorio, no uses la tool.")
    messages = []
    if context:
        for msg in context[-6:]:
            role = "user" if msg.get("direction")=="inbound" else "assistant"
            messages.append({"role":role,"content":msg.get("text","")})
    messages.append({"role":"user","content":text})
    data = await _claude(system, text, max_tokens=1024, messages=messages,
                          tools=[PARSE_TOOL], tool_choice={"type":"auto"})
    if not data: return None
    for block in data.get("content",[]):
        if block.get("type")=="tool_use" and block.get("name")=="create_reminder":
            return _args_to_parsed(block.get("input",{}), now)
    return None

def _args_to_parsed(args, now):
    try:
        remind_at = datetime.fromisoformat(args["remind_at"]).replace(tzinfo=TZ)
        if remind_at <= now:
            remind_at += timedelta(days=1)
            print(f"[ai_parser] remind_at adjusted +1 day: {remind_at}")
        rec_type = args.get("recurrence_type","none")
        if rec_type == "none": rec_type = None
        stop_at = None
        if args.get("stop_at"):
            try:
                stop_at = datetime.fromisoformat(args["stop_at"]).replace(tzinfo=TZ)
                # FIX: asegurar que stop_at también es futuro respecto a remind_at
                if stop_at <= remind_at:
                    stop_at = stop_at + timedelta(days=1)
                    print(f"[ai_parser] stop_at adjusted +1 day: {stop_at}")
            except Exception as e:
                print(f"[ai_parser] stop_at parse error: {e}")
        repeat = args.get("repeat_every_minutes")
        if isinstance(repeat,str):
            try: repeat = int(repeat)
            except: repeat = None
        rec_val = args.get("recurrence_value")
        if rec_val in ("null","none","",None): rec_val = None
        result = {
            "task_text": args.get("task_text","").strip(),
            "remind_at": remind_at, "status":"scheduled",
            "recurrence_type":rec_type, "recurrence_value":rec_val,
            "weekdays_only":bool(args.get("weekdays_only",False)),
            "remind_if_no_response":False, "retry_delay_minutes":None,
            "cancel_on_event_type":None,
            "mode":args.get("mode","today_or_tomorrow_at_time"),
            "is_persistent":bool(args.get("is_persistent",False)),
            "repeat_every_minutes":repeat, "stop_at":stop_at,
            "awaiting_ack":False, "target_time_text":None, "minutes_before":None,
        }
        if result["task_text"]:
            print(f"[parse] ✅ '{result['task_text']}' → {remind_at.strftime('%Y-%m-%d %H:%M')} mode={result['mode']}")
            return result
        return None
    except Exception as exc:
        print(f"[parse] error: {exc}"); return None

# ══════════ 3. RESPONDER PREGUNTAS ══════════

async def answer_question_ai(question, reminders_summary, memory_context=""):
    if not ANTHROPIC_API_KEY: return None
    now = _now()
    days = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    system = (f"Eres EVA, asistente personal. Responde preguntas sobre recordatorios "
              f"de forma concisa y natural en español. "
              f"Hoy es {days[now.weekday()]} {now.strftime('%d/%m/%Y')} a las {now.strftime('%H:%M')}.\n"
              f"{memory_context}\n"
              f"Recordatorios activos:\n{reminders_summary or 'No hay recordatorios activos.'}\n"
              f"Responde en 1-3 líneas.")
    data = await _claude(system, question, max_tokens=250)
    return data["content"][0]["text"].strip() if data else None

# ══════════ 4. CONFIRMACIÓN NATURAL ══════════

async def build_reply_ai(source_text, parsed, reminder_id=None, memory_context=""):
    if not ANTHROPIC_API_KEY: return None
    now = _now()
    local_dt = parsed["remind_at"]
    days = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    if local_dt.date() == now.date():
        fecha = f"hoy a las {local_dt.strftime('%H:%M')}"
    elif local_dt.date() == (now+timedelta(days=1)).date():
        fecha = f"mañana a las {local_dt.strftime('%H:%M')}"
    else:
        fecha = f"el {days[local_dt.weekday()]} {local_dt.strftime('%d/%m')} a las {local_dt.strftime('%H:%M')}"
    extras = []
    if parsed.get("recurrence_type")=="weekly": extras.append(f"cada {parsed.get('recurrence_value','semana')}")
    elif parsed.get("recurrence_type")=="weekdays": extras.append("días laborables")
    elif parsed.get("is_persistent"): extras.append(f"repito cada {parsed.get('repeat_every_minutes',2)} min hasta 'listo'")
    extra_str = f" ({', '.join(extras)})" if extras else ""
    id_str = f" [{reminder_id}]" if reminder_id else ""
    system = ("Eres EVA, asistente personal. Confirma el recordatorio de forma breve y natural "
              "en español, como una persona. Sin emojis extraños, sin 'EVA:' al inicio. Máximo 2 líneas. "
              "Última línea siempre: 'Si la hora no es correcta, di \"no, a las HH:MM\".'")
    prompt = (f"Usuario dijo: '{source_text}'\n"
              f"Recordatorio: '{parsed['task_text']}' — {fecha}{extra_str}.{id_str}")
    data = await _claude(system, prompt, max_tokens=150)
    return data["content"][0]["text"].strip() if data else None

# ══════════ 5. CHAT GENERAL ══════════

async def chat_reply_ai(text, memory_context=""):
    if not ANTHROPIC_API_KEY: return None
    system = ("Eres EVA, asistente personal en español. Eres concisa, amable y directa. "
              "Si no entiendes el mensaje como recordatorio, orienta al usuario con 1-2 ejemplos "
              "concretos de lo que puedes hacer. Nunca más de 3 líneas."
              f"{memory_context}")
    data = await _claude(system, text, max_tokens=150)
    return data["content"][0]["text"].strip() if data else None

# ══════════ 6. RESUMEN DIARIO CON IA ══════════

async def build_briefing_ai(reminders_today: list[dict],
                              recent_events: list[dict],
                              user_facts: list[dict],
                              persona: dict) -> str | None:
    """
    Genera el resumen diario matutino con Claude.
    
    reminders_today: lista de {id, task_text, remind_at, status}
    recent_events: últimos events relevantes de ayer (postponed, cancelled, created)
    user_facts: memoria del usuario
    persona: config de personalidad
    """
    if not ANTHROPIC_API_KEY:
        return None

    now = _now()
    days = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
    day_str = f"{days[now.weekday()]} {now.strftime('%d/%m/%Y')}"

    name = persona.get("name", "Eva")
    user_name = persona.get("user_name", "")
    tone = persona.get("tone", "informal")
    language = persona.get("language", "es")
    use_emoji = persona.get("emoji", True)
    notes = persona.get("personality_notes", "")

    # Construir sección de recordatorios de hoy
    if reminders_today:
        reminders_str = "\n".join(
            f"- [{r['id']}] {r['task_text']} a las {r['remind_at']}" 
            for r in reminders_today
        )
    else:
        reminders_str = "(ninguno)"

    # Construir contexto de eventos recientes relevantes
    events_str = ""
    if recent_events:
        event_lines = []
        for e in recent_events[:8]:
            if e["type"] == "reminder_rescheduled":
                event_lines.append(f"- Ayer pospusiste: {e['value']}")
            elif e["type"] == "reminder_cancelled":
                event_lines.append(f"- Ayer cancelaste: {e['value']}")
            elif e["type"] == "reminder_corrected":
                event_lines.append(f"- Ayer corregiste la hora de: {e['value']}")
        if event_lines:
            events_str = "Contexto de ayer:\n" + "\n".join(event_lines)

    # Memoria relevante
    facts_str = ""
    if user_facts:
        facts_str = "Lo que sé del usuario:\n" + "\n".join(
            f"- {f['key'].replace('_',' ')}: {f['value']}" for f in user_facts[:10]
        )

    emoji_instruction = "Usa emojis con moderación." if use_emoji else "No uses emojis."

    tone_map = {
        "informal": "informal y cercano",
        "formal": "formal y profesional",
        "profesional": "profesional pero accesible",
    }
    tone_desc = tone_map.get(tone, "natural")

    lang_map = {
        "es-ve": "español venezolano natural (pana, chamo, epale, chévere cuando fluya)",
        "es-es": "español de España natural",
        "es": "español neutro",
    }
    lang_desc = lang_map.get(language, "español")

    system = (
        f"Eres {name}, asistente personal{f' de {user_name}' if user_name else ''}. "
        f"Genera el resumen diario matutino de hoy {day_str}.\n\n"
        f"Tono: {tone_desc}. Idioma: {lang_desc}. {emoji_instruction}\n"
        f"{notes}\n\n"
        f"Reglas del briefing:\n"
        f"- Empieza con un saludo breve y la fecha\n"
        f"- Si hay recordatorios, menciónalos de forma natural y conversacional, no como lista\n"
        f"- Usa el contexto de ayer para dar relevancia ('ayer lo pospusiste', 'es la segunda vez esta semana')\n"
        f"- Si no hay nada, dilo con optimismo en 1 línea\n"
        f"- Máximo 5-6 líneas en total\n"
        f"- No inventes información que no esté en los datos\n\n"
        f"{facts_str}\n{events_str}"
    )

    prompt = f"Recordatorios de hoy:\n{reminders_str}"

    data = await _claude(system, prompt, max_tokens=300)
    if data:
        return data["content"][0]["text"].strip()
    return None

# ══════════ 7. INFERIR PRIORIDAD ══════════

PRIORITY_SYSTEM = """Eres el clasificador de prioridad de EVA. 
Dado el texto de una tarea o recordatorio, asigna una prioridad P0-P4:

P0 — Critical: sistema caído, producción afectada, emergencia real
P1 — High: urgente, bloquea trabajo, debe hacerse hoy
P2 — Moderate: importante, esta semana, afecta a otros
P3 — Low: rutina, cuando pueda, no urgente (DEFAULT para la mayoría)
P4 — Negligible: algún día, backlog, sin impacto si espera

Señales de alta prioridad: "urgente", "crítico", "producción", "error", "caído", "ahora", "hoy", "importante"
Señales de baja prioridad: "cuando pueda", "algún día", "sin prisa", "pendiente", "backlog"

Responde SOLO con JSON: {"priority": "P0"|"P1"|"P2"|"P3"|"P4", "reason": "breve razón"}"""

async def infer_priority(task_text: str) -> str:
    """
    Infiere la prioridad P0-P4 de una tarea usando Claude Haiku.
    Devuelve "P3" (Low) como fallback.
    """
    if not ANTHROPIC_API_KEY:
        return "P3"
    
    data = await _claude(PRIORITY_SYSTEM, f"Tarea: '{task_text}'", max_tokens=80)
    if not data:
        return "P3"
    
    try:
        raw = data["content"][0]["text"].strip()
        s = raw.find("{"); e = raw.rfind("}") + 1
        if s >= 0 and e > s:
            raw = raw[s:e]
        result = json.loads(raw)
        priority = result.get("priority", "P3")
        reason = result.get("reason", "")
        if priority in ("P0","P1","P2","P3","P4"):
            print(f"[priority] '{task_text[:30]}' → {priority} — {reason}")
            return priority
    except Exception as exc:
        print(f"[priority] error: {exc}")
    return "P3"