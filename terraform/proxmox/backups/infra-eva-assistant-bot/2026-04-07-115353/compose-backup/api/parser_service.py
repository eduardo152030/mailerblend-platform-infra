import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

MADRID_TZ = ZoneInfo("Europe/Madrid")

def parse_reminder(text: str) -> dict | None:
    raw = text.strip()
    lower = raw.lower().strip()

    if lower.startswith("eva,"):
        lower = lower[4:].strip()
    elif lower.startswith("eva "):
        lower = lower[4:].strip()

    m = re.match(r"^recuérdame en (\d+)\s+minutos?\s+(.+)$", lower, re.IGNORECASE)
    if m:
        minutes = int(m.group(1))
        task = m.group(2).strip()
        remind_at = datetime.now(MADRID_TZ) + timedelta(minutes=minutes)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "mode": "relative_minutes",
        }

    m = re.match(r"^recuerdame en (\d+)\s+minutos?\s+(.+)$", lower, re.IGNORECASE)
    if m:
        minutes = int(m.group(1))
        task = m.group(2).strip()
        remind_at = datetime.now(MADRID_TZ) + timedelta(minutes=minutes)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "mode": "relative_minutes",
        }

    m = re.match(r"^recuérdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m:
        task = m.group(1).strip()
        hour = int(m.group(2))
        minute = int(m.group(3))
        now = datetime.now(MADRID_TZ)
        remind_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_at <= now:
            remind_at = remind_at + timedelta(days=1)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "mode": "today_or_tomorrow_at_time",
        }

    m = re.match(r"^recuerdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m:
        task = m.group(1).strip()
        hour = int(m.group(2))
        minute = int(m.group(3))
        now = datetime.now(MADRID_TZ)
        remind_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if remind_at <= now:
            remind_at = remind_at + timedelta(days=1)
        return {
            "task_text": task,
            "remind_at": remind_at,
            "mode": "today_or_tomorrow_at_time",
        }

    return None
