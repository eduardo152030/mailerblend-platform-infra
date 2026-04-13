"""
memory_service.py — Memoria semántica de EVA.

Funciones:
  - extract_facts_from_message(): extrae hechos de un mensaje del usuario con Claude
  - get_user_facts(): devuelve los hechos de un usuario como string de contexto
  - upsert_fact(): guarda o actualiza un hecho en la BD
  - build_memory_context(): genera el bloque de contexto para inyectar en el system prompt
"""

import os
import json
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import select, text

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-haiku-4-5-20251001"

# ══════════════════════════════════════════
# EXTRACCIÓN DE HECHOS CON LLM
# ══════════════════════════════════════════

EXTRACT_SYSTEM = """Eres el sistema de memoria de EVA, un asistente personal.
Tu función es extraer hechos útiles y persistentes sobre el usuario a partir de sus mensajes.

Extrae SOLO hechos que sean:
- Rutinas o horarios habituales ("ficha a las 8:00", "sale a las 17:40")
- Personas y contexto ("Ian es su hijo", "tiene logopeda los miércoles a las 17:00")
- Preferencias o contexto profesional ("trabaja en mailerblend", "se llama Jainer")
- Compromisos recurrentes ("revisión del médico cada 6 meses")

NO extraigas:
- Recordatorios puntuales (eso va en la tabla reminders)
- Información temporal que no sea patrón habitual

Responde SOLO con JSON válido, sin markdown:
{"facts": [{"key": "string_snake_case", "value": "string descriptivo"}]}

Si no hay hechos útiles, responde: {"facts": []}"""


async def extract_facts_from_message(text: str, existing_facts: list[dict]) -> list[dict]:
    """
    Analiza un mensaje del usuario y extrae hechos persistentes.
    Devuelve lista de {key, value} o lista vacía.
    """
    if not ANTHROPIC_API_KEY:
        return []

    existing_str = ""
    if existing_facts:
        existing_str = "\nHechos ya conocidos:\n" + "\n".join(
            f"- {f['key']}: {f['value']}" for f in existing_facts[:15]
        )

    prompt = f"Mensaje del usuario: '{text}'{existing_str}"

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": MODEL,
                    "max_tokens": 300,
                    "system": EXTRACT_SYSTEM,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            if r.status_code != 200:
                return []
            data = r.json()
            raw = data["content"][0]["text"].strip()
            # Extract first valid JSON object — handles markdown fences and trailing text
            _s = raw.find("{"); _e = raw.rfind("}") + 1
            if _s >= 0 and _e > _s:
                raw = raw[_s:_e]
            parsed = json.loads(raw.strip())
            facts = parsed.get("facts", [])
            if facts:
                print(f"[memory] extracted {len(facts)} facts: {[f['key'] for f in facts]}")
            return facts
    except Exception as exc:
        print(f"[memory] extract error: {exc}")
        return []


# ══════════════════════════════════════════
# BD: leer y escribir hechos
# ══════════════════════════════════════════

def upsert_fact(db: Session, user_id: int, key: str, value: str, source: str = "conversation") -> None:
    """Inserta o actualiza un hecho del usuario."""
    try:
        db.execute(
            text("""
                INSERT INTO user_facts (user_id, key, value, source)
                VALUES (:user_id, :key, :value, :source)
                ON CONFLICT (user_id, key)
                DO UPDATE SET value = EXCLUDED.value,
                              source = EXCLUDED.source,
                              updated_at = now()
            """),
            {"user_id": user_id, "key": key, "value": value, "source": source}
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"[memory] upsert error: {exc}")


def get_user_facts(db: Session, user_id: int) -> list[dict]:
    """Devuelve todos los hechos del usuario como lista de dicts."""
    try:
        rows = db.execute(
            text("SELECT key, value FROM user_facts WHERE user_id = :uid ORDER BY updated_at DESC LIMIT 30"),
            {"uid": user_id}
        ).fetchall()
        return [{"key": r[0], "value": r[1]} for r in rows]
    except Exception:
        return []


def build_memory_context(facts: list[dict]) -> str:
    """
    Genera el bloque de texto de memoria para inyectar en el system prompt.
    Devuelve string vacío si no hay hechos.
    """
    if not facts:
        return ""
    lines = "\n".join(f"- {f['key'].replace('_', ' ')}: {f['value']}" for f in facts)
    return f"\nLo que sé del usuario:\n{lines}\n"


# ══════════════════════════════════════════
# PROCESO COMPLETO: analizar + guardar
# ══════════════════════════════════════════

async def process_message_for_memory(db: Session, user_id: int, text: str) -> None:
    """
    Analiza un mensaje entrante, extrae hechos y los guarda.
    Se llama de forma asíncrona desde el webhook — no bloquea la respuesta.
    """
    try:
        existing = get_user_facts(db, user_id)
        facts = await extract_facts_from_message(text, existing)
        for fact in facts:
            key = fact.get("key", "").strip()
            value = fact.get("value", "").strip()
            if key and value:
                upsert_fact(db, user_id, key, value)
    except Exception as exc:
        print(f"[memory] process error: {exc}")
        traceback.print_exc()