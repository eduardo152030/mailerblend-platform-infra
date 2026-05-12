"""
undated_tasks_reminder.py — Recordatorios por tareas sin fecha

Detecta tareas activas sin fecha que llevan demasiado tiempo sin gestión
y envía alertas por Telegram.

Integración con run_scheduler.py:
    from undated_tasks_reminder import check_undated_tasks
    await check_undated_tasks(send_fn)

Configuración en tabla: undated_tasks_config
"""

import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select, text

from db import SessionLocal
from models import Reminder, User

TZ = ZoneInfo(os.getenv("TIMEZONE", "Europe/Madrid"))

# ── Configuración por defecto ─────────────────────────────────────────────
DEFAULT_CONFIG = {
    "enabled": True,
    "days_threshold": 7,           # días sin gestión para alertar
    "minimum_tasks_for_summary": 3, # mínimo para usar resumen agregado
    "send_individual_alerts": True, # alertas individuales
    "send_summary_alert": True,     # resumen agregado
    "max_items_in_summary": 5,      # tareas a mostrar en resumen
}

# Escalado anti-spam: avisar en estos días exactos
ALERT_DAYS = [7, 14, 30]
ALERT_TOLERANCE_HOURS = 23  # ventana para considerar "hoy toca avisar"


# ── Config helpers ────────────────────────────────────────────────────────

def _get_config(db) -> dict:
    """Lee configuración desde BD. Devuelve defaults si no existe."""
    try:
        row = db.execute(text("""
            SELECT key, value FROM undated_tasks_config
        """)).fetchall()
        config = dict(DEFAULT_CONFIG)
        for key, val in row:
            if key in ("enabled", "send_individual_alerts", "send_summary_alert"):
                config[key] = val.lower() in ("true", "1", "yes")
            elif key in ("days_threshold", "minimum_tasks_for_summary",
                         "max_items_in_summary"):
                config[key] = int(val)
        return config
    except Exception:
        return dict(DEFAULT_CONFIG)


def _last_alert_days_ago(reminder_id: int, db) -> int | None:
    """Devuelve cuántos días hace que se envió la última alerta para esta tarea."""
    try:
        row = db.execute(text("""
            SELECT created_at FROM undated_task_alerts
            WHERE reminder_id = :rid
            ORDER BY created_at DESC LIMIT 1
        """), {"rid": reminder_id}).fetchone()
        if not row:
            return None
        last = row[0]
        if last.tzinfo is None:
            last = last.replace(tzinfo=TZ)
        return (datetime.now(TZ) - last).days
    except Exception:
        return None


def _record_alert(reminder_id: int, db) -> None:
    """Registra que se envió una alerta para esta tarea."""
    try:
        db.execute(text("""
            INSERT INTO undated_task_alerts (reminder_id, created_at)
            VALUES (:rid, now())
        """), {"rid": reminder_id})
    except Exception as e:
        print(f"[undated] error recording alert: {e}")


# ── Core logic ────────────────────────────────────────────────────────────

def get_undated_stale_tasks(db, user_id: int, days_threshold: int) -> list[dict]:
    """
    Devuelve tareas activas sin fecha que llevan más de days_threshold días
    sin gestión (usando focalboard_synced_at, sent_at o created_at como proxy).

    Criterios:
    - status in (scheduled, pending) — activas
    - remind_at año >= 2099 (sin fecha real)
    - (ahora - max(focalboard_synced_at, created_at)) > days_threshold días
    - focalboard_card_id NOT NULL (son tareas reales, no recordatorios internos)
    """
    cutoff = datetime.now(TZ) - timedelta(days=days_threshold)

    rows = db.execute(
        select(Reminder)
        .where(Reminder.user_id == user_id)
        .where(Reminder.status.in_(["scheduled", "pending"]))
        .where(Reminder.focalboard_card_id.isnot(None))
    ).scalars().all()

    stale = []
    for r in rows:
        # Verificar que no tiene fecha real (año 2099 = sin fecha)
        if r.remind_at:
            local_dt = r.remind_at
            if local_dt.tzinfo is None:
                local_dt = local_dt.replace(tzinfo=TZ)
            if local_dt.year < 2099:
                continue  # tiene fecha real → no es "sin fecha"

        # Calcular última actividad
        candidates = [r.created_at]
        if r.focalboard_synced_at:
            candidates.append(r.focalboard_synced_at)
        if r.sent_at:
            candidates.append(r.sent_at)

        last_activity = None
        for c in candidates:
            if c is None:
                continue
            if hasattr(c, 'tzinfo') and c.tzinfo is None:
                c = c.replace(tzinfo=TZ)
            if last_activity is None or c > last_activity:
                last_activity = c

        if last_activity is None:
            continue

        days_inactive = (datetime.now(TZ) - last_activity).days
        if days_inactive < days_threshold:
            continue

        stale.append({
            "id": r.id,
            "task_text": r.task_text,
            "days_inactive": days_inactive,
            "last_activity": last_activity,
            "tags": getattr(r, "tags", None),
            "priority": getattr(r, "priority", "P3"),
        })

    # Ordenar por días inactivos (más antigua primero)
    stale.sort(key=lambda x: x["days_inactive"], reverse=True)
    return stale


def _should_alert_today(days_inactive: int, last_alert_days_ago: int | None) -> bool:
    """
    Determina si hay que alertar hoy según el escalado anti-spam.

    Lógica:
    - Si nunca se alertó → alertar siempre que supere cualquier umbral,
      independientemente de cuánto tiempo lleve (fix: evita bloquear tareas
      que ya superaron la ventana cuando el scheduler las detecta por primera vez)
    - Si ya se alertó → alertar solo cuando se cruza el siguiente umbral
    """
    for threshold in ALERT_DAYS:
        if days_inactive >= threshold:
            if last_alert_days_ago is None:
                # Nunca alertado → alertar en el primer check que supera este umbral
                return True
            else:
                # Ya alertado → alertar solo si cruzamos un nuevo umbral desde la última alerta
                days_at_last_alert = days_inactive - last_alert_days_ago
                if days_at_last_alert < threshold <= days_inactive:
                    return True
    return False


def build_undated_task_alerts(tasks: list[dict], config: dict, db) -> list[dict]:
    """
    Filtra las tareas que deben recibir alerta individual hoy.
    Respeta anti-spam escalado.
    """
    to_alert = []
    for task in tasks:
        last_alert = _last_alert_days_ago(task["id"], db)
        if _should_alert_today(task["days_inactive"], last_alert):
            to_alert.append(task)
    return to_alert


def build_individual_message(task: dict) -> str:
    days = task["days_inactive"]
    name = task["task_text"][:60]
    tags = f" {task['tags']}" if task.get("tags") else ""
    return (f"📌 La tarea '{name}'{tags} lleva {days} días sin fecha "
            f"y sin gestionarse. ¿Le asignas una fecha o la completas?")


def build_summary_message(tasks: list[dict], max_items: int) -> str:
    n = len(tasks)
    shown = tasks[:max_items]
    lines = [f"📋 Tienes {n} tarea{'s' if n != 1 else ''} sin fecha "
             f"desde hace más de 7 días:\n"]
    for t in shown:
        lines.append(f"  • [{t['id']}] {t['task_text'][:45]} ({t['days_inactive']}d)")
    if n > max_items:
        lines.append(f"  … y {n - max_items} más.")
    lines.append("\n¿Quieres revisarlas? Puedes asignarles fecha desde la UI.")
    return "\n".join(lines)


# ── Main entry point ──────────────────────────────────────────────────────

async def check_undated_tasks(send_fn) -> int:
    """
    Punto de entrada desde run_scheduler.py.
    Revisa tareas sin fecha y envía alertas si procede.

    Retorna número de mensajes enviados.
    """
    db = SessionLocal()
    sent = 0
    try:
        config = _get_config(db)
        if not config["enabled"]:
            return 0

        users = db.execute(select(User)).scalars().all()

        for user in users:
            if not user.telegram_chat_id:
                continue

            stale = get_undated_stale_tasks(
                db, user.id, config["days_threshold"]
            )
            if not stale:
                continue

            # ── Alertas individuales ──────────────────────────────────────
            if config["send_individual_alerts"]:
                to_alert = build_undated_task_alerts(stale, config, db)
                # Solo enviar individual si son pocas (< minimum_tasks_for_summary)
                if len(stale) < config["minimum_tasks_for_summary"]:
                    for task in to_alert:
                        msg = build_individual_message(task)
                        try:
                            await send_fn(user.telegram_chat_id, msg)
                            _record_alert(task["id"], db)
                            sent += 1
                            print(f"[undated] individual alert sent: [{task['id']}] {task['task_text'][:40]}")
                        except Exception as exc:
                            print(f"[undated] send error: {exc}")

            # ── Resumen agregado ──────────────────────────────────────────
            if (config["send_summary_alert"] and
                    len(stale) >= config["minimum_tasks_for_summary"]):
                # Anti-spam: enviar resumen máximo una vez por día
                # usando la tarea más antigua como referencia
                oldest = stale[0]
                last_alert = _last_alert_days_ago(oldest["id"], db)
                if last_alert is None or last_alert >= 1:
                    msg = build_summary_message(stale, config["max_items_in_summary"])
                    try:
                        await send_fn(user.telegram_chat_id, msg)
                        # Registrar alerta para todas las tareas del resumen
                        for task in stale[:config["max_items_in_summary"]]:
                            _record_alert(task["id"], db)
                        sent += 1
                        print(f"[undated] summary sent: {len(stale)} tasks")
                    except Exception as exc:
                        print(f"[undated] summary send error: {exc}")

            db.commit()

    except Exception as exc:
        print(f"[undated] check error: {exc}")
        import traceback; traceback.print_exc()
    finally:
        db.close()
    return sent


# ── REST API helper (montado desde main.py) ───────────────────────────────

def get_undated_tasks_config_api(db) -> dict:
    return _get_config(db)


async def update_undated_tasks_config_api(db, body: dict) -> dict:
    allowed = {
        "enabled", "days_threshold", "minimum_tasks_for_summary",
        "send_individual_alerts", "send_summary_alert", "max_items_in_summary"
    }
    for key, val in body.items():
        if key not in allowed:
            continue
        db.execute(text("""
            INSERT INTO undated_tasks_config (key, value)
            VALUES (:k, :v)
            ON CONFLICT (key) DO UPDATE SET value = :v
        """), {"k": key, "v": str(val).lower() if isinstance(val, bool) else str(val)})
    db.commit()
    return _get_config(db)