import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

MADRID_TZ = ZoneInfo("Europe/Madrid")
DEFAULT_REPEAT_EVERY_MINUTES = 2

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

    return candidate + timedelta(days=days_ahead)


def _compute_target_time(now: datetime, hour: int, minute: int) -> datetime:
    target_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target_at <= now:
        target_at = target_at + timedelta(days=1)
    return target_at


def _build_response(
    *,
    task: str,
    remind_at: datetime,
    weekdays_only: bool,
    remind_if_no_response: bool,
    cancel_on_event_type: str | None,
    mode: str,
    recurrence_type: str | None = None,
    recurrence_value: str | None = None,
    is_persistent: bool = False,
    repeat_every_minutes: int | None = None,
    stop_at: datetime | None = None,
    target_time_text: str | None = None,
    minutes_before: int | None = None,
) -> dict:
    return {
        "task_text": task,
        "remind_at": remind_at,
        "status": "scheduled",
        "recurrence_type": recurrence_type,
        "recurrence_value": recurrence_value,
        "weekdays_only": weekdays_only,
        "remind_if_no_response": remind_if_no_response,
        "retry_delay_minutes": 5 if remind_if_no_response else None,
        "cancel_on_event_type": cancel_on_event_type,
        "mode": mode,
        "is_persistent": is_persistent,
        "repeat_every_minutes": repeat_every_minutes,
        "stop_at": stop_at,
        "awaiting_ack": False,
        "target_time_text": target_time_text,
        "minutes_before": minutes_before,
    }


def _normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def _extract_persistent_options(lower: str) -> tuple[str, bool, int | None, tuple[int, int] | None]:
    is_persistent = False
    repeat_every_minutes = None
    stop_at_hm = None

    if "si no respondo" in lower and "vuelve a avisarme" in lower:
        is_persistent = True
        repeat_every_minutes = DEFAULT_REPEAT_EVERY_MINUTES

    if (
        "sigue avisándome" in lower
        or "sigue avisandome" in lower
        or "espera mi listo" in lower
        or "hasta que te diga listo" in lower
        or "no pares hasta que te diga listo" in lower
    ):
        is_persistent = True
        if repeat_every_minutes is None:
            repeat_every_minutes = DEFAULT_REPEAT_EVERY_MINUTES

    m_repeat = re.search(r"cada\s+(\d+)\s+minutos?", lower, re.IGNORECASE)
    if m_repeat:
        is_persistent = True
        repeat_every_minutes = int(m_repeat.group(1))

    m_stop = re.search(
        r"(?:hasta\s+las|hasta\s+que\s+sean\s+las)\s+(\d{1,2}):(\d{2})",
        lower,
        re.IGNORECASE,
    )
    if m_stop:
        is_persistent = True
        if repeat_every_minutes is None:
            repeat_every_minutes = DEFAULT_REPEAT_EVERY_MINUTES
        stop_at_hm = (int(m_stop.group(1)), int(m_stop.group(2)))

    cleaned = lower
    cleanup_patterns = [
        r",?\s*y\s+sigue\s+avis[aá]ndome\s+hasta\s+las\s+\d{1,2}:\d{2}",
        r",?\s*y\s+sigue\s+avis[aá]ndome\s+hasta\s+que\s+sean\s+las\s+\d{1,2}:\d{2}",
        r",?\s*y\s+sigue\s+avis[aá]ndome",
        r",?\s+si\s+no\s+respondo,\s+vuelve\s+a\s+avisarme",
        r",?\s+si\s+no\s+respondo\s+vuelve\s+a\s+avisarme",
        r",?\s+y\s+espera\s+mi\s+listo",
        r",?\s+hasta\s+que\s+te\s+diga\s+listo",
        r",?\s+no\s+pares\s+hasta\s+que\s+te\s+diga\s+listo",
        r",?\s+cada\s+\d+\s+minutos?",
    ]
    for pattern in cleanup_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned, is_persistent, repeat_every_minutes, stop_at_hm


def _compute_stop_at(now: datetime, remind_at: datetime, stop_at_hm: tuple[int, int] | None) -> datetime | None:
    if not stop_at_hm:
        return None

    hour, minute = stop_at_hm
    stop_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if stop_at < remind_at:
        stop_at = stop_at + timedelta(days=1)

    if stop_at <= remind_at:
        stop_at = remind_at

    return stop_at


def parse_reminder(text: str) -> dict | None:
    raw = text.strip()
    lower = _normalize_text(raw)

    if lower.startswith("eva,"):
        lower = lower[4:].strip()
    elif lower.startswith("eva "):
        lower = lower[4:].strip()

    remind_if_no_response = "si no respondo" in lower and "vuelve a avisarme" in lower
    cancel_on_event_type = "fichado" if ("si ya fiché" in lower or "si ya fiche" in lower) else None
    weekdays_only = "solo días laborables" in lower or "solo dias laborables" in lower

    lower = lower.replace(", si ya fiché, cancela el recordatorio", "")
    lower = lower.replace(", si ya fiche, cancela el recordatorio", "")
    lower = lower.replace("si ya fiché cancela el recordatorio", "")
    lower = lower.replace("si ya fiche cancela el recordatorio", "")
    lower = lower.replace(", solo días laborables", "")
    lower = lower.replace(", solo dias laborables", "")
    lower = lower.replace("solo días laborables", "")
    lower = lower.replace("solo dias laborables", "")
    lower = re.sub(r"\s+", " ", lower).strip()

    lower, is_persistent, repeat_every_minutes, stop_at_hm = _extract_persistent_options(lower)
    now = datetime.now(MADRID_TZ)

    # 1) recuérdame en X minutos ...
    m = re.match(r"^recu[eé]rdame en (\d+)\s+minutos?\s+(.+)$", lower, re.IGNORECASE)
    if m:
        minutes = int(m.group(1))
        task = m.group(2).strip()
        remind_at = now + timedelta(minutes=minutes)
        stop_at = _compute_stop_at(now, remind_at, stop_at_hm)

        return _build_response(
            task=task,
            remind_at=remind_at,
            weekdays_only=weekdays_only,
            remind_if_no_response=remind_if_no_response,
            cancel_on_event_type=cancel_on_event_type,
            mode="relative_minutes",
            is_persistent=is_persistent,
            repeat_every_minutes=repeat_every_minutes,
            stop_at=stop_at,
        )

    # 2) mañana recuérdame ... a las HH:MM
    m = re.match(r"^ma[ñn]ana recu[eé]rdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m:
        task = m.group(1).strip()
        hour = int(m.group(2))
        minute = int(m.group(3))
        remind_at = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        stop_at = _compute_stop_at(now + timedelta(days=1), remind_at, stop_at_hm)

        return _build_response(
            task=task,
            remind_at=remind_at,
            weekdays_only=weekdays_only,
            remind_if_no_response=remind_if_no_response,
            cancel_on_event_type=cancel_on_event_type,
            mode="tomorrow_at_time",
            is_persistent=is_persistent,
            repeat_every_minutes=repeat_every_minutes,
            stop_at=stop_at,
        )

    # 3) recuérdame X minutos antes de las HH:MM [task opcional]
    m = re.match(
        r"^recu[eé]rdame\s+(\d+)\s+minutos?\s+antes\s+de\s+(?:que\s+sean\s+)?las\s+(\d{1,2}):(\d{2})(?:\s+(.+))?$",
        lower,
        re.IGNORECASE,
    )
    if m:
        minutes_before = int(m.group(1))
        hour = int(m.group(2))
        minute = int(m.group(3))
        task = (m.group(4) or "").strip()

        if not task:
            task = f"aviso previo a las {hour:02d}:{minute:02d}"

        target_at = _compute_target_time(now, hour, minute)
        remind_at = target_at - timedelta(minutes=minutes_before)
        stop_at = _compute_stop_at(now, remind_at, stop_at_hm)

        return _build_response(
            task=task,
            remind_at=remind_at,
            weekdays_only=weekdays_only,
            remind_if_no_response=remind_if_no_response,
            cancel_on_event_type=cancel_on_event_type,
            mode="before_time",
            is_persistent=is_persistent,
            repeat_every_minutes=repeat_every_minutes,
            stop_at=stop_at,
            target_time_text=f"{hour:02d}:{minute:02d}",
            minutes_before=minutes_before,
        )

    # 4) recuérdame task X minutos antes de las HH:MM
    m = re.match(
        r"^recu[eé]rdame\s+(.+?)\s+(\d+)\s+minutos?\s+antes\s+de\s+(?:que\s+sean\s+)?las\s+(\d{1,2}):(\d{2})$",
        lower,
        re.IGNORECASE,
    )
    if m:
        task = m.group(1).strip()
        minutes_before = int(m.group(2))
        hour = int(m.group(3))
        minute = int(m.group(4))

        target_at = _compute_target_time(now, hour, minute)
        remind_at = target_at - timedelta(minutes=minutes_before)
        stop_at = _compute_stop_at(now, remind_at, stop_at_hm)

        return _build_response(
            task=task,
            remind_at=remind_at,
            weekdays_only=weekdays_only,
            remind_if_no_response=remind_if_no_response,
            cancel_on_event_type=cancel_on_event_type,
            mode="before_time",
            is_persistent=is_persistent,
            repeat_every_minutes=repeat_every_minutes,
            stop_at=stop_at,
            target_time_text=f"{hour:02d}:{minute:02d}",
            minutes_before=minutes_before,
        )

    # 5) cada lunes recuérdame ... a las HH:MM
    m = re.match(
        r"^cada\s+(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)\s+recu[eé]rdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$",
        lower,
        re.IGNORECASE,
    )
    if m:
        weekday_name = m.group(1).lower()
        task = m.group(2).strip()
        hour = int(m.group(3))
        minute = int(m.group(4))
        target_weekday = WEEKDAY_MAP[weekday_name]
        remind_at = _next_weekday(now, target_weekday, hour, minute)

        # Para no romper lo ya validado, no activamos persistencia en recurrentes
        return _build_response(
            task=task,
            remind_at=remind_at,
            weekdays_only=weekdays_only,
            remind_if_no_response=False,
            cancel_on_event_type=cancel_on_event_type,
            mode="weekly_day",
            recurrence_type="weekly",
            recurrence_value=weekday_name,
            is_persistent=False,
            repeat_every_minutes=None,
            stop_at=None,
        )

    # 6) recuérdame ... a las HH:MM
    m = re.match(r"^recu[eé]rdame(?:\s+(.+?))?\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m and not weekdays_only:
        task = (m.group(1) or "").strip()
        hour = int(m.group(2))
        minute = int(m.group(3))

        if not task:
            task = f"recordatorio de las {hour:02d}:{minute:02d}"

        remind_at = _compute_target_time(now, hour, minute)
        stop_at = _compute_stop_at(now, remind_at, stop_at_hm)

        return _build_response(
            task=task,
            remind_at=remind_at,
            weekdays_only=weekdays_only,
            remind_if_no_response=remind_if_no_response,
            cancel_on_event_type=cancel_on_event_type,
            mode="today_or_tomorrow_at_time",
            is_persistent=is_persistent,
            repeat_every_minutes=repeat_every_minutes,
            stop_at=stop_at,
        )

    # 7) recuérdame ... a las HH:MM, solo días laborables
    m = re.match(r"^recu[eé]rdame(?:\s+(.+?))?\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m and weekdays_only:
        task = (m.group(1) or "").strip()
        hour = int(m.group(2))
        minute = int(m.group(3))

        if not task:
            task = f"recordatorio de las {hour:02d}:{minute:02d}"

        remind_at = _compute_target_time(now, hour, minute)
        while remind_at.weekday() >= 5:
            remind_at = remind_at + timedelta(days=1)

        # Para no romper lo ya validado, weekdays sigue como recurrencia clásica
        return _build_response(
            task=task,
            remind_at=remind_at,
            weekdays_only=True,
            remind_if_no_response=remind_if_no_response,
            cancel_on_event_type=cancel_on_event_type,
            mode="weekdays",
            recurrence_type="weekdays",
            recurrence_value="mon-fri",
            is_persistent=False,
            repeat_every_minutes=None,
            stop_at=None,
        )

    return None