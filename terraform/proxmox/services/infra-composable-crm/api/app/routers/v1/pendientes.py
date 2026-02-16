from __future__ import annotations

from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import date, datetime, time  # 📅 Para manejo de fechas

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/pendientes", tags=["pendientes"])  # ✅ CORREGIDO: era /v1/oportunidades


def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 200:
        return 200
    return limit


# -------------------------
# 📋 Valores permitidos (basados en DB constraints)
# -------------------------
ALLOWED_STATUS = {"TODO", "IN_PROGRESS", "DONE", "CANCELLED"}
ALLOWED_PRIORITY = {"HIGH", "MEDIUM", "LOW"}  # ✅ Corregido: la DB NO tiene URGENT


def _normalize_status(value: Optional[str]) -> str:
    """Normaliza y valida el valor de status."""
    if not value:
        return "TODO"
    
    normalized = value.strip().upper()
    
    # Mapeo de aliases comunes
    aliases = {
        "PENDING": "TODO",
        "WORKING": "IN_PROGRESS",
        "IN PROGRESS": "IN_PROGRESS",
        "INPROGRESS": "IN_PROGRESS",
        "COMPLETED": "DONE",
        "FINISHED": "DONE",
        "CANCELED": "CANCELLED",
    }
    
    normalized = aliases.get(normalized, normalized)
    
    if normalized not in ALLOWED_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status: '{value}'. Allowed values: {', '.join(sorted(ALLOWED_STATUS))}"
        )
    
    return normalized


def _normalize_priority(value: Optional[str]) -> str:
    """Normaliza y valida el valor de priority."""
    if not value:
        return "MEDIUM"
    
    normalized = value.strip().upper()
    
    if normalized not in ALLOWED_PRIORITY:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid priority: '{value}'. Allowed values: {', '.join(sorted(ALLOWED_PRIORITY))}"
        )
    
    return normalized


# -------------------------
# 📅 Date/Time conversion helpers
# -------------------------
def _parse_date_field(value: Any) -> Optional[date]:
    """Convierte strings de fecha a objetos date (YYYY-MM-DD)."""
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.strip()).date()
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format: '{value}'. Expected format: YYYY-MM-DD"
            )
    raise HTTPException(
        status_code=400,
        detail=f"Invalid date type: {type(value)}. Expected string in format YYYY-MM-DD"
    )


def _parse_time_field(value: Any) -> Optional[time]:
    """Convierte strings de tiempo a objetos time (HH:MM o HH:MM:SS)."""
    if value is None or value == "":
        return None
    if isinstance(value, time):
        return value
    if isinstance(value, str):
        try:
            # Intenta parsear HH:MM:SS o HH:MM
            return datetime.strptime(value.strip(), "%H:%M:%S").time()
        except ValueError:
            try:
                return datetime.strptime(value.strip(), "%H:%M").time()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid time format: '{value}'. Expected format: HH:MM or HH:MM:SS"
                )
    raise HTTPException(
        status_code=400,
        detail=f"Invalid time type: {type(value)}. Expected string in format HH:MM"
    )


def _parse_datetime_field(value: Any) -> Optional[datetime]:
    """Convierte strings de datetime a objetos datetime."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.strip())
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid datetime format: '{value}'. Expected ISO format"
            )
    raise HTTPException(
        status_code=400,
        detail=f"Invalid datetime type: {type(value)}"
    )


# -------------------------
# Endpoints
# -------------------------


@router.get("/metadata/allowed-values")
async def get_allowed_values() -> Dict[str, Any]:
    """
    Retorna los valores permitidos para los campos con constraints.
    Útil para construir dropdowns en la UI.
    """
    return {
        "status": sorted(ALLOWED_STATUS),
        "priority": sorted(ALLOWED_PRIORITY),
    }


@router.get("")
async def list_pendientes(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),

    # search
    q: Optional[str] = Query(None, min_length=1, max_length=200),

    # filtros exactos
    status: Optional[str] = Query(None, min_length=1, max_length=50),
    priority: Optional[str] = Query(None, min_length=1, max_length=50),
    assigned_to: Optional[str] = Query(None, min_length=1, max_length=200),
    oportunidad_id: Optional[UUID] = Query(None),
    contacto_id: Optional[UUID] = Query(None),

    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Lista pendientes/tareas con filtros y paginación.
    """
    limit = _clamp_limit(limit)

    where: List[str] = []
    args: List[Any] = []
    i = 1

    if status:
        where.append(f"status = ${i}")
        args.append(status)
        i += 1
    if priority:
        where.append(f"priority = ${i}")
        args.append(priority)
        i += 1
    if assigned_to:
        where.append(f"assigned_to ILIKE ${i}")
        args.append(f"%{assigned_to}%")
        i += 1
    if oportunidad_id:
        where.append(f"oportunidad_id = ${i}")
        args.append(oportunidad_id)
        i += 1
    if contacto_id:
        where.append(f"contacto_id = ${i}")
        args.append(contacto_id)
        i += 1

    if q:
        q_like = f"%{q}%"
        where.append(f"(title ILIKE ${i} OR COALESCE(description,'') ILIKE ${i} OR COALESCE(assigned_to,'') ILIKE ${i})")
        args.append(q_like)
        i += 1

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = await conn.fetch(
        f"""
        SELECT
          id,
          contacto_id,
          oportunidad_id,
          linkedin_lead_id,
          title,
          description,
          status,
          priority,
          assigned_to,
          due_date,
          due_time,
          reminder_enabled,
          reminder_datetime,
          completed_at,
          created_at,
          updated_at,
          created_by,
          contacto_nombre
        FROM pendientes
        {where_sql}
        ORDER BY
          CASE WHEN status = 'DONE' THEN 1 ELSE 0 END,
          due_date ASC NULLS LAST,
          created_at DESC NULLS LAST,
          id DESC
        LIMIT ${i} OFFSET ${i+1}
        """,
        *args,
        limit,
        offset,
    )

    total = await conn.fetchval(
        f"SELECT count(*)::int FROM pendientes {where_sql}",
        *args,
    )

    items = [dict(r) for r in rows]
    return {"items": items, "limit": limit, "offset": offset, "count": len(items), "total": int(total or 0)}


@router.get("/{pendiente_id}")
async def get_pendiente(
    pendiente_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    row = await conn.fetchrow("SELECT * FROM pendientes WHERE id = $1", pendiente_id)
    if not row:
        raise HTTPException(status_code=404, detail="Pendiente not found")
    return dict(row)


# -------------------------
# 🆕 POST - Crear pendiente
# -------------------------
@router.post("")
async def create_pendiente(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Crea un nuevo pendiente/tarea asociado a una oportunidad o contacto.
    
    Payload esperado:
    {
        "title": "Llamar al cliente",
        "oportunidad_id": "uuid",
        "due_date": "2026-02-20",
        "due_time": "14:30",
        "priority": "HIGH",
        "description": "Seguimiento de propuesta",
        "assigned_to": "Juan Perez"
    }
    """
    # Validar título (requerido)
    title = payload.get("title", "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="'title' is required")
    
    # IDs opcionales
    oportunidad_id = payload.get("oportunidad_id")
    contacto_id = payload.get("contacto_id")
    linkedin_lead_id = payload.get("linkedin_lead_id")
    
    # Convertir strings a UUID si es necesario
    if oportunidad_id and isinstance(oportunidad_id, str):
        oportunidad_id = UUID(oportunidad_id)
    if contacto_id and isinstance(contacto_id, str):
        contacto_id = UUID(contacto_id)
    
    # Si hay oportunidad, obtener contacto_id y contacto_nombre
    contacto_nombre = None
    if oportunidad_id:
        op = await conn.fetchrow(
            "SELECT contacto_id, contacto_nombre FROM oportunidades WHERE id = $1",
            oportunidad_id
        )
        if op:
            if not contacto_id:
                contacto_id = op.get("contacto_id")
            contacto_nombre = op.get("contacto_nombre")
    
    # Si hay contacto pero no nombre, buscarlo
    if contacto_id and not contacto_nombre:
        c = await conn.fetchrow(
            "SELECT nombre FROM contactos WHERE id = $1",
            contacto_id
        )
        if c:
            contacto_nombre = c.get("nombre")
    
    # Campos opcionales con defaults
    description = payload.get("description", "").strip() or None
    status = _normalize_status(payload.get("status", "TODO"))
    priority = _normalize_priority(payload.get("priority", "MEDIUM"))
    assigned_to = payload.get("assigned_to", "").strip() or None
    created_by = payload.get("created_by", "api").strip()
    
    # Convertir campos de fecha/tiempo
    due_date = _parse_date_field(payload.get("due_date"))
    due_time = _parse_time_field(payload.get("due_time"))
    reminder_enabled = payload.get("reminder_enabled", False)
    reminder_datetime = _parse_datetime_field(payload.get("reminder_datetime")) if reminder_enabled else None
    
    # Insertar
    row = await conn.fetchrow(
        """
        INSERT INTO pendientes (
            id,
            contacto_id,
            oportunidad_id,
            linkedin_lead_id,
            title,
            description,
            status,
            priority,
            assigned_to,
            due_date,
            due_time,
            reminder_enabled,
            reminder_datetime,
            created_by,
            contacto_nombre,
            created_at,
            updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NOW(), NOW()
        )
        RETURNING *
        """,
        uuid4(),
        contacto_id,
        oportunidad_id,
        linkedin_lead_id,
        title,
        description,
        status,
        priority,
        assigned_to,
        due_date,
        due_time,
        reminder_enabled,
        reminder_datetime,
        created_by,
        contacto_nombre,
    )
    
    return dict(row)


# -------------------------
# 🔄 PATCH - Actualizar pendiente
# -------------------------
@router.patch("/{pendiente_id}")
async def patch_pendiente(
    pendiente_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Actualiza un pendiente existente.
    """
    before = await conn.fetchrow("SELECT * FROM pendientes WHERE id = $1", pendiente_id)
    if not before:
        raise HTTPException(status_code=404, detail="Pendiente not found")

    # Campos editables
    editable = {
        "title",
        "description",
        "status",
        "priority",
        "assigned_to",
        "due_date",
        "due_time",
        "reminder_enabled",
        "reminder_datetime",
        "completed_at",
    }

    updates = {k: v for k, v in payload.items() if k in editable}
    if not updates:
        return dict(before)

    # Normalizar y validar status y priority
    if "status" in updates:
        updates["status"] = _normalize_status(updates["status"])
    if "priority" in updates:
        updates["priority"] = _normalize_priority(updates["priority"])

    # Convertir campos de fecha/tiempo
    if "due_date" in updates:
        updates["due_date"] = _parse_date_field(updates["due_date"])
    if "due_time" in updates:
        updates["due_time"] = _parse_time_field(updates["due_time"])
    if "reminder_datetime" in updates:
        updates["reminder_datetime"] = _parse_datetime_field(updates["reminder_datetime"])
    if "completed_at" in updates:
        updates["completed_at"] = _parse_datetime_field(updates["completed_at"])

    # Si se marca como DONE y no hay completed_at, agregarlo automáticamente
    if updates.get("status") == "DONE" and "completed_at" not in updates:
        updates["completed_at"] = datetime.now()

    set_parts: List[str] = []
    args: List[Any] = []
    idx = 1
    for k, v in updates.items():
        set_parts.append(f"{k} = ${idx}")
        args.append(v)
        idx += 1

    set_parts.append("updated_at = NOW()")
    sql = f"UPDATE pendientes SET {', '.join(set_parts)} WHERE id = ${idx} RETURNING *"
    args.append(pendiente_id)

    after = await conn.fetchrow(sql, *args)
    return dict(after)


# -------------------------
# 🗑️ DELETE - Eliminar pendiente
# -------------------------
@router.delete("/{pendiente_id}")
async def delete_pendiente(
    pendiente_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Elimina un pendiente.
    """
    row = await conn.fetchrow("DELETE FROM pendientes WHERE id = $1 RETURNING *", pendiente_id)
    if not row:
        raise HTTPException(status_code=404, detail="Pendiente not found")
    return {"deleted": True, "pendiente": dict(row)}