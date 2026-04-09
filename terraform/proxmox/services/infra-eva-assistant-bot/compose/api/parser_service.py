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


def _compute_target_time(now: datetime, hour: int, minute: int, force_pm: bool = False) -> datetime:
    if force_pm and hour <= 12:
        hour = hour + 12 if hour < 12 else hour
    target_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target_at <= now:
        # Auto-flip PM solo para horas muy ambiguas (1-6): "a las 5" puede ser tarde
        # 7+ son claramente mañaneras — saltar al día siguiente sin flip
        if not force_pm and 1 <= hour <= 6:
            target_pm = now.replace(hour=hour + 12, minute=minute, second=0, microsecond=0)
            if target_pm > now:
                return target_pm
        target_at = target_at + timedelta(days=1)
    return target_at


def _force_pm_hour(hour: int, force: bool = False) -> int:
    """Convierte hora ambigua a PM si force=True y la hora es <= 12."""
    if force and 1 <= hour <= 12:
        return hour + 12 if hour < 12 else hour
    return hour


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


def _clean_task(task: str) -> str:
    """Limpia prefijos innecesarios del texto de la tarea."""
    task = task.strip()
    # "que tengo X" → "X"
    task = re.sub(r"^que\s+tengo\s+(?:que\s+)?", "", task, flags=re.IGNORECASE)
    # "que X" → "X" (solo si queda algo significativo)
    task = re.sub(r"^que\s+(?=\w)", "", task, flags=re.IGNORECASE)
    # "mañana tengo que X" → "X"  
    task = re.sub(r"^ma[ñn]ana\s+(?:tengo\s+que\s+|tengo\s+)?", "", task, flags=re.IGNORECASE)
    return task.strip()


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
        r",?\s+hasta\s+las\s+\d{1,2}:\d{2}",
        r",?\s+hasta\s+que\s+sean\s+las\s+\d{1,2}:\d{2}",
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


def parse_reminder(text: str, context: list[dict] | None = None) -> dict | None:
    """
    context: lista de dicts {"direction": "inbound"|"outbound", "text": str}
    Se usa para resolver referencias relativas como "cámbialo a las 10"
    o "el mismo de antes pero mañana".
    Por ahora se usa para extraer la hora/tarea del mensaje anterior
    cuando el mensaje actual es muy corto o ambiguo.
    """
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

    # Normalizar "hoy", "esta tarde", "esta noche", "esta mañana" — no aportan
    # información que el parser no deduzca ya de la hora, y rompen los regex.
    # Pero antes de limpiarlos, detectar si el usuario indica explícitamente tarde/noche
    # para forzar conversión PM en horas ambiguas (1-8).
    _force_pm = bool(re.search(r'\b(?:esta\s+)?(?:tarde|noche)\b', lower))

    lower = re.sub(r"\s+hoy\b", "", lower)
    lower = re.sub(r"\s+esta\s+(?:tarde|noche|ma[ñn]ana)\b", "", lower)
    lower = re.sub(r"\besta\s+(?:tarde|noche|ma[ñn]ana)\s+", "", lower)

    # Limpiar contexto extra después de la hora: "a las 3:50, tengo X" → "a las 3:50"
    # El contexto extra se preserva como parte del task si va ANTES de la hora
    _comma_time = re.search(r'(a las\s+\d{1,2}:\d{2})\s*,\s*(.+)$', lower)
    if _comma_time:
        _extra_context = _clean_task(_comma_time.group(2).strip())
        lower = lower[:_comma_time.start(2)-2].rstrip(', ')
        _inject_context = _extra_context
    else:
        _inject_context = None

    # Verbos de acción genéricos — si el task es uno de estos, el contexto es mejor task
    _GENERIC_VERBS = {
        "ir", "salir", "volver", "llamar", "hacer", "ver", "pasar",
        "entrar", "llegar", "quedar", "enviar", "mandar", "comprar",
    }

    # Normalizar hora sin minutos: "a las 5" → "a las 05:00", "a las 17" → "a las 17:00"
    # Para horas ambiguas (1-8), si ya pasó hoy en formato AM se convierte a PM (+12h)
    # Debe ir antes de los patrones para que todos los regex vean siempre HH:MM
    def _expand_hour(m):
        h = int(m.group(1))
        return f"a las {h:02d}:00"

    lower = re.sub(r'\ba las\s+(\d{1,2})\b(?!:\d)', _expand_hour, lower)

    lower = re.sub(r"\s+", " ", lower).strip()

    # 0) recordatorio por intervalo — detectar ANTES de _extract_persistent_options
    #    porque esa función elimina "cada X minutos" del texto.
    #    Variantes soportadas:
    #      cada 3 minutos recuérdame tomar agua
    #      eva, cada 5 minutos recuérdame revisar el horno
    #      recuérdame cada 10 minutos hacer ejercicio
    #      avísame cada 2 minutos tomar pastilla [hasta las HH:MM]
    _interval_patterns = [
        r"^(?:recu[eé]rdame\s+|av[ií]same\s+)?cada\s+(\d+)\s+minutos?\s+(?:recu[eé]rdame\s+)?(.+)$",
        r"^recu[eé]rdame\s+cada\s+(\d+)\s+minutos?\s+(.+)$",
        r"^av[ií]same\s+cada\s+(\d+)\s+minutos?\s+(.+)$",
    ]
    for _pat in _interval_patterns:
        _m = re.match(_pat, lower, re.IGNORECASE)
        if _m:
            interval = int(_m.group(1))
            task = _m.group(2).strip()
            # Extraer stop_at del task si lleva "hasta las HH:MM"
            _stop_hm = None
            _stop_match = re.search(
                r"(?:hasta\s+las|hasta\s+que\s+sean\s+las)\s+(\d{1,2}):(\d{2})",
                task, re.IGNORECASE
            )
            if _stop_match:
                _stop_hm = (int(_stop_match.group(1)), int(_stop_match.group(2)))
                task = re.sub(
                    r",?\s*(?:hasta\s+las|hasta\s+que\s+sean\s+las)\s+\d{1,2}:\d{2}", "",
                    task, flags=re.IGNORECASE
                ).strip()
            now = datetime.now(MADRID_TZ)
            remind_at = now + timedelta(minutes=interval)
            stop_at = _compute_stop_at(now, remind_at, _stop_hm)
            cancel_on_event_type_0 = "fichado" if ("si ya fiché" in lower or "si ya fiche" in lower) else None

            return _build_response(
                task=task,
                remind_at=remind_at,
                weekdays_only=False,
                remind_if_no_response=False,
                cancel_on_event_type=cancel_on_event_type_0,
                mode="interval_minutes",
                is_persistent=True,
                repeat_every_minutes=interval,
                stop_at=stop_at,
            )

    lower, is_persistent, repeat_every_minutes, stop_at_hm = _extract_persistent_options(lower)
    now = datetime.now(MADRID_TZ)
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

    # 2) mañana recuérdame ... a las HH:MM  (orden original)
    m = re.match(r"^ma[ñn]ana recu[eé]rdame\s+(.+)\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m:
        task = _clean_task(m.group(1).strip())
        hour = int(m.group(2))
        minute = int(m.group(3))
        remind_at = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        stop_at = _compute_stop_at(now + timedelta(days=1), remind_at, stop_at_hm)
        if _inject_context and task and len(task) < 8:
            task = f"{task}, {_inject_context}"

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

    # 2b) recuérdame mañana ... a las HH:MM  (orden invertido — más natural)
    m = re.match(
        r"^recu[eé]rdame\s+ma[ñn]ana\s+(?:a las\s+(\d{1,2}):(\d{2})\s+)?(.+?)(?:\s+a las\s+(\d{1,2}):(\d{2}))?$",
        lower, re.IGNORECASE
    )
    if m:
        if m.group(1) and m.group(2):
            hour, minute = int(m.group(1)), int(m.group(2))
            task = m.group(3).strip()
        elif m.group(4) and m.group(5):
            hour, minute = int(m.group(4)), int(m.group(5))
            task = m.group(3).strip()
        else:
            hour, minute = 9, 0
            task = m.group(3).strip()

        if task and len(task) >= 2:
            remind_at = (now + timedelta(days=1)).replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            return _build_response(
                task=task, remind_at=remind_at, weekdays_only=weekdays_only,
                remind_if_no_response=remind_if_no_response,
                cancel_on_event_type=cancel_on_event_type, mode="tomorrow_at_time",
                is_persistent=is_persistent, repeat_every_minutes=repeat_every_minutes,
                stop_at=_compute_stop_at(now, remind_at, stop_at_hm),
            )

    # 2c) recuérdame ... el próximo lunes/martes/...  [a las HH:MM]
    m = re.match(
        r"^recu[eé]rdame\s+(?:que\s+)?(.+?)\s+el\s+pr[oó]ximo\s+"
        r"(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)"
        r"(?:\s+a las\s+(\d{1,2}):(\d{2}))?$",
        lower, re.IGNORECASE
    )
    if m:
        task = m.group(1).strip()
        weekday_name = m.group(2).lower()
        hour   = int(m.group(3)) if m.group(3) else 9
        minute = int(m.group(4)) if m.group(4) else 0
        target_weekday = WEEKDAY_MAP.get(weekday_name, 0)
        remind_at = _next_weekday(now, target_weekday, hour, minute)
        # forzar que sea PRÓXIMO (al menos 1 día adelante)
        if remind_at.date() == now.date():
            remind_at = remind_at + timedelta(days=7)
        return _build_response(
            task=task, remind_at=remind_at, weekdays_only=False,
            remind_if_no_response=remind_if_no_response,
            cancel_on_event_type=cancel_on_event_type, mode="next_weekday",
            is_persistent=is_persistent, repeat_every_minutes=repeat_every_minutes,
            stop_at=_compute_stop_at(now, remind_at, stop_at_hm),
        )

    # 2d) recuérdame ... el DD/MM/YYYY [a las HH:MM]
    #     recuérdame ... el DD-MM-YYYY [a las HH:MM]
    #     "que es el" / "es el" también válido
    m = re.match(
        r"^recu[eé]rdame\s+(?:que\s+)?(.+?)"
        r"(?:\s+que\s+es|\s+es)?\s+el\s+"
        r"(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})"
        r"(?:\s+a las\s+(\d{1,2}):(\d{2}))?$",
        lower, re.IGNORECASE
    )
    if m:
        task   = m.group(1).strip()
        day    = int(m.group(2))
        month  = int(m.group(3))
        year   = int(m.group(4))
        hour   = int(m.group(5)) if m.group(5) else 9
        minute = int(m.group(6)) if m.group(6) else 0
        try:
            remind_at = now.replace(
                year=year, month=month, day=day,
                hour=hour, minute=minute, second=0, microsecond=0
            )
            if remind_at <= now:
                # fecha pasada — avisamos igualmente (puede ser cumpleaños futuro)
                pass
            return _build_response(
                task=task, remind_at=remind_at, weekdays_only=False,
                remind_if_no_response=remind_if_no_response,
                cancel_on_event_type=cancel_on_event_type, mode="absolute_date",
                is_persistent=is_persistent, repeat_every_minutes=repeat_every_minutes,
                stop_at=_compute_stop_at(now, remind_at, stop_at_hm),
            )
        except ValueError:
            pass  # fecha inválida — continuar con otros patrones

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

        target_at = _compute_target_time(now, hour, minute, _force_pm)
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

        target_at = _compute_target_time(now, hour, minute, _force_pm)
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
        stop_at = _compute_stop_at(now, remind_at, stop_at_hm)

        return _build_response(
            task=task,
            remind_at=remind_at,
            weekdays_only=weekdays_only,
            remind_if_no_response=remind_if_no_response,
            cancel_on_event_type=cancel_on_event_type,
            mode="weekly_day",
            recurrence_type="weekly",
            recurrence_value=weekday_name,
            is_persistent=is_persistent,
            repeat_every_minutes=repeat_every_minutes,
            stop_at=stop_at,
        )

    # 6) recuérdame ... a las HH:MM
    m = re.match(r"^recu[eé]rdame(?:\s+(.+?))?\s+a las\s+(\d{1,2}):(\d{2})$", lower, re.IGNORECASE)
    if m and not weekdays_only:
        task = _clean_task((m.group(1) or "").strip())
        hour = int(m.group(2))
        minute = int(m.group(3))

        if not task:
            task = _inject_context or f"recordatorio de las {hour:02d}:{minute:02d}"
        elif _inject_context:
            # Si el task es un verbo genérico, el contexto es más descriptivo
            if task.lower() in _GENERIC_VERBS:
                task = _inject_context
            elif len(task) <= 6:
                task = f"{task} — {_inject_context}"

        remind_at = _compute_target_time(now, hour, minute, _force_pm)
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
        task = _clean_task((m.group(1) or "").strip())
        hour = int(m.group(2))
        minute = int(m.group(3))

        if not task:
            task = _inject_context or f"recordatorio de las {hour:02d}:{minute:02d}"

        remind_at = _compute_target_time(now, hour, minute, _force_pm)
        while remind_at.weekday() >= 5:
            remind_at = remind_at + timedelta(days=1)

        stop_at = _compute_stop_at(now, remind_at, stop_at_hm)

        return _build_response(
            task=task,
            remind_at=remind_at,
            weekdays_only=True,
            remind_if_no_response=remind_if_no_response,
            cancel_on_event_type=cancel_on_event_type,
            mode="weekdays",
            recurrence_type="weekdays",
            recurrence_value="mon-fri",
            is_persistent=is_persistent,
            repeat_every_minutes=repeat_every_minutes,
            stop_at=stop_at,
        )

    # 8) Fallback: resolución contextual
    # Si el mensaje actual no se entiende solo pero hay contexto previo,
    # intentamos completarlo con la tarea del último recordatorio creado.
    if context:
        prev_inbound = [c["text"] for c in context if c["direction"] == "inbound"]
        time_only = re.match(r'^(?:a las?\s+)?(\d{1,2}):(\d{2})$', lower)
        if time_only and len(prev_inbound) > 1:
            hour = int(time_only.group(1))
            minute = int(time_only.group(2))
            for prev in reversed(prev_inbound[:-1]):
                prev_parsed = parse_reminder(prev)
                if prev_parsed:
                    remind_at = _compute_target_time(now, hour, minute, _force_pm)
                    return _build_response(
                        task=prev_parsed["task_text"],
                        remind_at=remind_at,
                        weekdays_only=False,
                        remind_if_no_response=False,
                        cancel_on_event_type=None,
                        mode="today_or_tomorrow_at_time",
                    )

    return None