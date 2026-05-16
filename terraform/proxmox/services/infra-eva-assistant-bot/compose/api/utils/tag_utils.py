"""
utils/tag_utils.py
==================
Tag extraction, normalization, and Focalboard property building.

Rules:
  - Pure functions — no DB, no HTTP, no side effects.
  - Preserves ALL existing Focalboard property IDs — do not change them.
  - Does NOT merge tags into notes — keeps them separate.

To debug:
  - Tag not extracted           → inspect extract_tags()
  - Wrong Focalboard prop ID    → check core/config.py constants
  - Tags and notes mixed        → inspect build_text_prop()

UI compatibility note:
  The Lovable UI reads 'a6bxuk4rgxp7wn6bashiadwaiiy' (TEXT_PROP_ID) as "Notes".
  Tags in this property appear as plain text in the notes field.
  Tags are ALSO stored separately in reminder.tags (DB column).
  The UI tag badges come from reminder.tags via the EVA REST API — NOT from Focalboard.
  Therefore: storing tags in TEXT_PROP alongside notes is cosmetic only.
  Keeping them separate from notes reduces visual noise in the UI.
"""
import re
from typing import Optional


# Known project tags → Focalboard option IDs (from core/config.py)
# Duplicated here to keep tag_utils self-contained. Keep in sync with config.py.
PROYECTO_MAP = {
    "#mailerblend": "copt_mailerblend",
    "#nt":          "copt_nt",
    "#personal":    "copt_personal",
    "#tradeintuit": "copt_tradeintuit",
    "#sage":        None,  # not a content board project, no option ID
}

FORMATO_MAP = {
    "youtube":  "copt_youtube",
    "short":    "copt_shortreel",
    "reel":     "copt_shortreel",
    "linkedin": "copt_linkedin",
}


def extract_tags(text: str) -> list[str]:
    """
    Extract all hashtags from text. Returns list with # prefix.
    Case-preserving.

    Example: "idea #contenido #NT" → ["#contenido", "#NT"]
    """
    return re.findall(r'#[a-zA-Z]\w*', text)


def tags_str(tags: list[str]) -> Optional[str]:
    """Join list of tags into space-separated string, or None if empty."""
    return " ".join(tags) if tags else None


def remove_tags(text: str) -> str:
    """Remove all hashtags from text. Strips resulting extra whitespace."""
    return re.sub(r'\s*#[a-zA-Z]\w*', '', text).strip()


def is_content_tag(tags: list[str]) -> bool:
    """Return True if #contenido is in the tag list."""
    return any(t.lower() == "#contenido" for t in tags)


def filter_content_tag(tags: list[str]) -> list[str]:
    """Return tags list without #contenido."""
    return [t for t in tags if t.lower() != "#contenido"]


def detect_proyecto(tags: list[str]) -> Optional[str]:
    """
    Return Focalboard option ID for the first matching project tag.
    Returns None if no project tag found or tag has no option ID.
    """
    for tag in tags:
        opt_id = PROYECTO_MAP.get(tag.lower())
        if opt_id:
            return opt_id
    return None


def detect_formato(text: str, tags: list[str]) -> Optional[str]:
    """
    Return Focalboard option ID for the first matching format keyword
    found in text or tags.
    """
    combined = f"{text.lower()} {' '.join(t.lower() for t in tags)}"
    for keyword, opt_id in FORMATO_MAP.items():
        if keyword in combined:
            return opt_id
    return None


def build_text_prop(notes: Optional[str], tags: list[str]) -> Optional[str]:
    """
    Build the value for TEXT_PROP_ID ('a6bxuk4rgxp7wn6bashiadwaiiy').

    UI reads this as "Notes". Strategy:
    - If notes exist: use notes only (tags are visible via UI tag badges separately)
    - If no notes but tags exist: store tags as text so the field isn't empty
    - If neither: return None (field stays empty)

    This preserves notes without mixing tag strings into them.
    """
    if notes:
        return notes
    non_content_tags = filter_content_tag(tags)
    if non_content_tags:
        return " ".join(non_content_tags)
    return None


# ── Tag update message parsing ────────────────────────────────────────────

def is_tags_only_message(text: str) -> bool:
    """
    Return True if the message contains only hashtags (no other content).
    Examples:
      "#personal"          → True
      "#personal #NT"      → True
      "algo #personal"     → False
      "#personal text"     → False
    """
    return bool(extract_tags(text)) and not remove_tags(text).strip()


def merge_tags(existing: str | None, incoming: list[str]) -> str | None:
    """
    Merge incoming tags into existing tags string.
    - Deduplicates (case-insensitive comparison)
    - Preserves order: existing first, new appended
    - Returns None if result is empty

    Example:
      existing="#personal", incoming=["#NT", "#personal"] → "#personal #NT"
    """
    existing_list = extract_tags(existing or "")
    existing_lower = {t.lower() for t in existing_list}
    new_only = [t for t in incoming if t.lower() not in existing_lower]
    merged = existing_list + new_only
    return " ".join(merged) if merged else None


def parse_tag_update_message(text: str) -> dict | None:
    """
    Parse a message that is a tag update command.
    Returns dict with keys: task_id (int|None), tags (list[str])
    Returns None if message is not a tag update.

    Supported formats:
      "#personal"                     → {task_id: None, tags: ["#personal"]}
      "#personal #NT"                 → {task_id: None, tags: ["#personal", "#NT"]}
      "196 #personal"                 → {task_id: 196,  tags: ["#personal"]}
      "196 añade #personal"           → {task_id: 196,  tags: ["#personal"]}
      "196 tags #personal #NT"        → {task_id: 196,  tags: ["#personal", "#NT"]}
      "añade #personal a la 196"      → {task_id: 196,  tags: ["#personal"]}
      "algo sin tags"                 → None
      "tengo que revisar"             → None  (no tags)
    """
    import re as _re
    tags = extract_tags(text)
    if not tags:
        return None

    # Must have at least one valid project/content tag to be treated as tag update
    # (avoid false positives from reminder messages that happen to contain a hashtag)
    KNOWN_TAGS = {
        "#personal", "#contenido", "#nt", "#mailerblend",
        "#tradeintuit", "#sage",
    }
    has_known = any(t.lower() in KNOWN_TAGS for t in tags)
    if not has_known:
        return None

    # Extract explicit task ID if present
    task_id = None
    # Patterns: "196 #personal", "196 tags #personal", "añade #personal a la 196"
    id_match = _re.search(r'\b(\d{1,6})\b', text)
    if id_match:
        task_id = int(id_match.group(1))

    # Content after removing tags and ID — if there's substantial content it's not a tag update
    clean = remove_tags(text).strip()
    clean = _re.sub(r'\b\d{1,6}\b', '', clean).strip()
    # Allow short connector words: "añade", "tags", "a la", "para"
    connector_words = {"añade", "añadir", "agrega", "agregar", "tags", "tag", "a", "la", "el", "para"}
    remaining_words = [w for w in clean.split() if w.lower() not in connector_words]
    if remaining_words:
        # Real content remains → not a pure tag update
        return None

    return {"task_id": task_id, "tags": tags}


def extract_explicit_task_id(text: str) -> int | None:
    """
    Extract explicit task ID from a tag update message.
    "196 #personal" → 196
    "#personal"     → None
    """
    import re as _re
    result = parse_tag_update_message(text)
    if result:
        return result.get("task_id")
    return None