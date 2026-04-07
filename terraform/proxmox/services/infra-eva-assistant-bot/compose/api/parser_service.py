import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

MADRID_TZ = ZoneInfo("Europe/Madrid")
WEEKDAY_MAP = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6,
}

def _next_weekday(now: datetime, target_weekday: int, hour: int, minute: int) -> datetime:
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    days_ahead = (target_weekday - candidate.weekday()) % 7
    if days_ahead == 0 and candidate <= now:
        days_ahead = 7
    elif days_ahead > 0:
        candidate = candidate + timedelta(days=days_ahead)
        return candidate
    return candidate + timedelta(days=days_ahead)

def parse_reminder(text: str) -> dict | None:
    raw = text.strip()
    lower = raw.lower().strip()

    if lower.startswith("eva,"):
        lower = lower[4:].strip()
    elif lower.startswith("eva "):
        lower = lower[4:].strip()

    remind_if_no_response = "si no respondo" in lower and "vuelve a avisarme" in lower
    cancel_on_event_type = "fichado" if ("si ya fiché" in lower or "si ya fiche" in lower) else None
    weekdays_only = "solo días laborables" in lower or "solo dias laborables" in lower

    lower = lower.replace(", si no respondo, vuelve a avisarme", "")
    lower = lower.replace("si no respondo vuelve a avisarme", "")
    lower = lower.replace(", si ya fiché, cancela el recordatorio", "")
    lower = lower.replace(", si ya fiche, cancela el recordatorio", "")
    lower = lower.replace("si ya fiché cancela el recordatorio", "")
    lower = lower.replace("si ya fiche cancela el recordatorio", "")
    lower = lower.replace(", solo días laborables", "")
    lower = lower.replace(", solo dias laborables", "")
    lower = lower.replace("solo días laborables", "")
    lower = lower.replace("solo dias laborables", "")

    now = datetime.now(MADRID_TZ)

    m = re.match(r"^recuérdame en (\d+)\s+minutos?\s+(.+)$", lower, re.IGNORECASE)
    if not m:
        m = re.match(r"^recuerdame en (\d+)\s+minutos?\s+(.+)$", lower, re.IGNORECASE)
    if m:
        minutes = int(m.group(1))
        task = m.group(2).strip()
        remind_at = now + timedelta(minutes=minutes)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "status": "scheduled",
            "recurrence_type": None,
            "recurrence_value": None,
            "weekdays_only": weekdays_only,
            "remind_if_no_response": remind_if_no_response,
            "retry_delay_minutes": 5 if remind_if_no_response else None,
            "cancel_on_event_type": cancel_on_event_type,
            "mode": "relative_minutes",
        }

    m = re.match(r"^mañana recuérdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m:
        task = m.group(1).strip()
        hour = int(m.group(2))
        minute = int(m.group(3))
        remind_at = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "status": "scheduled",
            "recurrence_type": None,
            "recurrence_value": None,
            "weekdays_only": weekdays_only,
            "remind_if_no_response": remind_if_no_response,
            "retry_delay_minutes": 5 if remind_if_no_response else None,
            "cancel_on_event_type": cancel_on_event_type,
            "mode": "tomorrow_at_time",
        }

    m = re.match(r"^manana recuerdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m:
        task = m.group(1).strip()
        hour = int(m.group(2))
        minute = int(m.group(3))
        remind_at = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "status": "scheduled",
            "recurrence_type": None,
            "recurrence_value": None,
            "weekdays_only": weekdays_only,
            "remind_if_no_response": remind_if_no_response,
            "retry_delay_minutes": 5 if remind_if_no_response else None,
            "cancel_on_event_type": cancel_on_event_type,
            "mode": "tomorrow_at_time",
        }

    m = re.match(r"^recuérdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if not m:
        m = re.match(r"^recuerdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m:
        task = m.group(1).strip()
        hour = int(m.group(2))
        minute = int(m.group(3))
        remind_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_at <= now:
            remind_at = remind_at + timedelta(days=1)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "status": "scheduled",
            "recurrence_type": None,
            "recurrence_value": None,
            "weekdays_only": weekdays_only,
            "remind_if_no_response": remind_if_no_response,
            "retry_delay_minutes": 5 if remind_if_no_response else None,
            "cancel_on_event_type": cancel_on_event_type,
            "mode": "today_or_tomorrow_at_time",
        }

    m = re.match(r"^cada\s+(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)\s+recuérdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if not m:
        m = re.match(r"^cada\s+(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)\s+recuerdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m:
        weekday_name = m.group(1).lower()
        task = m.group(2).strip()
        hour = int(m.group(3))
        minute = int(m.group(4))
        target_weekday = WEEKDAY_MAP[weekday_name]
        remind_at = _next_weekday(now, target_weekday, hour, minute)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "status": "scheduled",
            "recurrence_type": "weekly",
            "recurrence_value": weekday_name,
            "weekdays_only": weekdays_only,
            "remind_if_no_response": remind_if_no_response,
            "retry_delay_minutes": 5 if remind_if_no_response else None,
            "cancel_on_event_type": cancel_on_event_type,
            "mode": "weekly_day",
        }

    m = re.match(r"^recuérdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if not m:
        m = re.match(r"^recuerdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m and weekdays_only:
        task = m.group(1).strip()
        hour = int(m.group(2))
        minute = int(m.group(3))
        remind_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_at <= now:
            remind_at = remind_at + timedelta(days=1)
        while remind_at.weekday() >= 5:
            remind_at = remind_at + timedelta(days=1)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "status": "scheduled",
            "recurrence_type": "weekdays",
            "recurrence_value": "mon-fri",
            "weekdays_only": True,
            "remind_if_no_response": remind_if_no_response,
            "retry_delay_minutes": 5 if remind_if_no_response else None,
            "cancel_on_event_type": cancel_on_event_type,
            "mode": "weekdays",
        }

    return None
