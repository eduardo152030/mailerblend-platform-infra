"""
ai_parser.py — Parser de lenguaje natural para EVA usando Claude Haiku.

Estrategia:
  1. Intenta parsear con Claude (function calling) → JSON estructurado
  2. Si falla (sin API key, error de red, respuesta inválida) → fallback a regex

Variables de entorno:
  ANTHROPIC_API_KEY   — clave de la API de Anthropic (requerida para LLM)
  EVA_AI_PARSER       — "1" para activar, "0" para forzar regex (default: "1")
  TIMEZONE            — zona horaria (default: Europe/Madrid)
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

# ══════════════════════════════════════════
# TOOL DEFINITION — lo que Claude debe extraer
# ══════════════════════════════════════════

PARSE_TOOL = {
    "name": "create_reminder",
    "description": (
        "Extrae la información de un recordatorio o tarea del mensaje del usuario. "
        "Úsala SIEMPRE que el usuario quiera recordar algo, programar una tarea, "
        "o recibir un aviso en el futuro."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "task_text": {
                "type": "string",
                "description": "Descripción concisa de la tarea o recordatorio. Sin prefijos como 'que tengo que' o 'que'. Ejemplos: 'fichar', 'llevar a Ian a logopeda', 'revisar route53', 'cita médico'."
            },
            "remind_at": {
                "type": "string",
                "description": "Fecha y hora en formato ISO 8601: YYYY-MM-DDTHH:MM:00. Debe ser en el futuro."
            },
            "recurrence_type": {
                "type": "string",
                "enum": ["none", "weekly", "weekdays", "interval"],
                "description": "'none' para recordatorio único, 'weekly' para semanal, 'weekdays' para días laborables, 'interval' para repetir cada X minutos."
            },
            "recurrence_value": {
                "type": "string",
                "description": "Para weekly: nombre del día (lunes, martes...). Para interval: número de minutos como string. Para otros: null."
            },
            "is_persistent": {
                "type": "boolean",
                "description": "true si debe repetirse hasta que el usuario diga 'listo'."
            },
            "repeat_every_minutes": {
                "type": "integer",
                "description": "Minutos entre repeticiones si is_persistent=true o recurrence_type=interval. null si no aplica."
            },
            "stop_at": {
                "type": "string",
                "description": "ISO 8601 de cuándo dejar de repetir. null si no hay límite."
            },
            "weekdays_only": {
                "type": "boolean",
                "description": "true si solo aplica en días laborables (lunes-viernes)."
            },
            "mode": {
                "type": "string",
                "description": "Modo de parsing: relative_minutes, today_or_tomorrow_at_time, tomorrow_at_time, weekly_day, weekdays, before_time, interval_minutes, absolute_date, next_weekday."
            }
        },
        "required": ["task_text", "remind_at", "recurrence_type", "is_persistent", "weekdays_only", "mode"]
    }
}


# ══════════════════════════════════════════
# SYSTEM PROMPT
# ══════════════════════════════════════════

def _build_system_prompt(now: datetime) -> str:
    day_names = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    weekday = day_names[now.weekday()]
    return f"""Eres el parser de recordatorios de EVA, un asistente personal en español.

Fecha y hora actual: {now.strftime('%Y-%m-%d %H:%M')} ({weekday}, zona horaria Europa/Madrid)

Tu única función es extraer la información de recordatorios del mensaje del usuario usando la tool create_reminder.

Reglas importantes:
- SIEMPRE usa la tool create_reminder si el mensaje contiene intención de recordatorio
- La fecha remind_at DEBE ser en el futuro respecto a ahora
- "mañana" = {(now + timedelta(days=1)).strftime('%Y-%m-%d')}
- "pasado mañana" = {(now + timedelta(days=2)).strftime('%Y-%m-%d')}
- "esta tarde" / "tarde" → hora en PM (después de las 13:00)
- "esta noche" → después de las 20:00
- "a las 8" sin contexto de tarde → 08:00 si no ha pasado, si pasó → 20:00
- "en X minutos/horas" → ahora + X
- "el próximo lunes" → próximo lunes aunque hoy sea lunes
- task_text debe ser conciso y sin prefijos innecesarios ("que tengo que", "que")
- Si hay contexto extra después de la hora (ej: "a las 5, tengo lo de Ian"), inclúyelo en task_text
- Para recordatorios recurrentes diarios laborables: recurrence_type="weekdays", weekdays_only=true
- Para "sigue avisándome": is_persistent=true, repeat_every_minutes=2 (o el valor indicado)

Si el mensaje NO es un recordatorio (es una cancelación, consulta, saludo, etc.), NO uses la tool."""


# ══════════════════════════════════════════
# LLAMADA A CLAUDE
# ══════════════════════════════════════════

async def _call_claude(text: str, context: list[dict] | None, now: datetime) -> dict | None:
    """
    Llama a Claude Haiku con function calling.
    Devuelve el dict de argumentos de create_reminder o None si no hay tool use.
    """
    if not ANTHROPIC_API_KEY:
        return None

    messages = []

    # Añadir contexto conversacional si existe
    if context:
        for msg in context[-6:]:  # últimos 6 mensajes
            role = "user" if msg["direction"] == "inbound" else "assistant"
            messages.append({"role": role, "content": msg["text"]})

    messages.append({"role": "user", "content": text})

    payload = {
        "model": MODEL,
        "max_tokens": 1024,
        "system": _build_system_prompt(now),
        "tools": [PARSE_TOOL],
        "tool_choice": {"type": "auto"},
        "messages": messages,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        data = r.json()

    # Extraer tool use
    for block in data.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == "create_reminder":
            return block.get("input", {})

    return None  # No tool use — mensaje no es un recordatorio


# ══════════════════════════════════════════
# CONVERSIÓN DE RESULTADO A FORMATO EVA
# ══════════════════════════════════════════

def _ai_result_to_parsed(args: dict, now: datetime) -> dict | None:
    """Convierte los argumentos de Claude al formato que espera main.py."""
    try:
        remind_at_str = args.get("remind_at", "")
        # Parsear ISO 8601
        remind_at = datetime.fromisoformat(remind_at_str).replace(tzinfo=TZ)

        # Si la fecha ya pasó, ajustar al día siguiente
        if remind_at <= now:
            remind_at = remind_at + timedelta(days=1)

        recurrence_type = args.get("recurrence_type", "none")
        if recurrence_type == "none":
            recurrence_type = None

        stop_at = None
        if args.get("stop_at"):
            try:
                stop_at = datetime.fromisoformat(args["stop_at"]).replace(tzinfo=TZ)
            except Exception:
                pass

        repeat_every_minutes = args.get("repeat_every_minutes")
        if isinstance(repeat_every_minutes, str):
            try:
                repeat_every_minutes = int(repeat_every_minutes)
            except Exception:
                repeat_every_minutes = None

        recurrence_value = args.get("recurrence_value")
        if recurrence_value in ("null", "none", ""):
            recurrence_value = None

        return {
            "task_text": args.get("task_text", "").strip(),
            "remind_at": remind_at,
            "status": "scheduled",
            "recurrence_type": recurrence_type,
            "recurrence_value": recurrence_value,
            "weekdays_only": bool(args.get("weekdays_only", False)),
            "remind_if_no_response": False,
            "retry_delay_minutes": None,
            "cancel_on_event_type": None,
            "mode": args.get("mode", "today_or_tomorrow_at_time"),
            "is_persistent": bool(args.get("is_persistent", False)),
            "repeat_every_minutes": repeat_every_minutes,
            "stop_at": stop_at,
            "awaiting_ack": False,
            "target_time_text": None,
            "minutes_before": None,
        }
    except Exception as exc:
        print(f"[ai_parser] conversion error: {exc}")
        return None


# ══════════════════════════════════════════
# ENTRY POINT — llamado desde main.py
# ══════════════════════════════════════════

async def parse_reminder_ai(text: str, context: list[dict] | None = None) -> dict | None:
    """
    Intenta parsear con Claude. Si falla, devuelve None para que
    main.py llame al parser de regex como fallback.
    """
    if not AI_PARSER_ENABLED or not ANTHROPIC_API_KEY:
        return None

    now = datetime.now(TZ)
    try:
        args = await _call_claude(text, context, now)
        if args is None:
            return None  # Claude dice que no es un recordatorio
        result = _ai_result_to_parsed(args, now)
        if result and result["task_text"]:
            print(f"[ai_parser] ✅ '{result['task_text']}' → {result['remind_at'].strftime('%Y-%m-%d %H:%M')} mode={result['mode']}")
            return result
        return None
    except Exception as exc:
        print(f"[ai_parser] error, falling back to regex: {exc}")
        traceback.print_exc()
        return None