"""
persona_service.py — Carga y gestiona la configuración de personalidad de EVA.

El fichero de configuración vive en /app/persona/{telegram_username}.json
o /app/persona/default.json como fallback.

Recarga automática si el fichero cambia (sin reiniciar el contenedor).
"""

import json
import os
import time
from pathlib import Path

PERSONA_DIR = Path(os.getenv("PERSONA_DIR", "/app/persona"))

# Cache: {username: (config_dict, mtime)}
_cache: dict[str, tuple[dict, float]] = {}

DEFAULT_PERSONA = {
    "name": "Eva",
    "tone": "informal",
    "language": "es",
    "emoji": True,
    "briefing_hour": 8,
    "briefing_enabled": True,
    "user_name": "Usuario",
    "phrases": {
        "greeting": "¡Hola! 👋",
        "confirmed": "Listo",
        "cancelled": "Cancelado",
        "unknown": "No entendí, prueba con otro comando",
        "morning": "¡Buenos días! ☀️",
        "no_reminders": "No tienes nada pendiente por ahora",
    },
    "personality_notes": "Sé amable, conciso y directo. Responde siempre en español.",
}


def load_persona(telegram_username: str | None) -> dict:
    """
    Carga la configuración de personalidad para un usuario.
    Orden de búsqueda:
      1. /app/persona/{username}.json
      2. /app/persona/default.json
      3. DEFAULT_PERSONA hardcoded
    """
    candidates = []
    if telegram_username:
        candidates.append(PERSONA_DIR / f"{telegram_username}.json")
    candidates.append(PERSONA_DIR / "default.json")

    for path in candidates:
        if path.exists():
            try:
                mtime = path.stat().st_mtime
                cached = _cache.get(str(path))
                if cached and cached[1] == mtime:
                    return cached[0]
                config = json.loads(path.read_text(encoding="utf-8"))
                # Merge with defaults so missing keys don't break anything
                merged = {**DEFAULT_PERSONA, **config}
                merged["phrases"] = {**DEFAULT_PERSONA["phrases"], **config.get("phrases", {})}
                _cache[str(path)] = (merged, mtime)
                print(f"[persona] loaded {path.name} for '{telegram_username}'")
                return merged
            except Exception as exc:
                print(f"[persona] error loading {path}: {exc}")

    return DEFAULT_PERSONA.copy()


def build_system_prompt(persona: dict, memory_context: str = "") -> str:
    """
    Construye el system prompt dinámicamente desde la config de personalidad.
    """
    name = persona.get("name", "Eva")
    user_name = persona.get("user_name", "el usuario")
    tone = persona.get("tone", "informal")
    language = persona.get("language", "es")
    emoji = persona.get("emoji", True)
    notes = persona.get("personality_notes", "")

    # Instrucciones de tono
    tone_instructions = {
        "informal": "Habla de forma informal y cercana, como un amigo de confianza.",
        "formal": "Habla de forma formal y profesional, con respeto y cortesía.",
        "profesional": "Habla de forma profesional pero accesible, sin ser frío.",
    }.get(tone, "Habla de forma natural y directa.")

    # Instrucciones de idioma
    lang_instructions = {
        "es-ve": "Usa español de Venezuela. Modismos naturales: 'pana', 'chamo', 'epale', 'chévere', 'vale', 'bro'. No fuerces los modismos — úsalos cuando fluyan natural.",
        "es-es": "Usa español de España. Natural, sin forzar regionalismos.",
        "es": "Usa español neutro, comprensible para cualquier hispanohablante.",
    }.get(language, "Usa español neutro.")

    emoji_instruction = (
        "Puedes usar emojis con moderación para dar calidez a las respuestas."
        if emoji else
        "No uses emojis."
    )

    prompt = f"""Eres {name}, asistente personal de {user_name}.

{tone_instructions}
{lang_instructions}
{emoji_instruction}

Reglas de comunicación:
- Respuestas cortas y directas. Máximo 3 líneas salvo que se pida más detalle.
- Nunca empieces con "Claro que sí", "Por supuesto", ni frases de relleno.
- Nunca uses "EVA:" ni tu nombre al inicio de la respuesta.
- Si confirmas un recordatorio, sé concreto: qué, cuándo.
- Si no entiendes algo, pide aclaración en una sola línea.

{notes}
{memory_context}"""

    return prompt.strip()


def get_phrase(persona: dict, key: str) -> str:
    """Devuelve una frase configurada o un fallback."""
    return persona.get("phrases", {}).get(key, DEFAULT_PERSONA["phrases"].get(key, ""))