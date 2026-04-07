"""
Router: LinkedIn Invite Templates
Gestión de mensajes de invitación con A/B testing
"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from typing import Optional, Dict, Any, List
from uuid import UUID
from asyncpg import Connection
import json

from app.db import get_db


router = APIRouter(
    prefix="/v1/linkedin-sourcing/invite-templates",
    tags=["LinkedIn Invite Templates"]
)


@router.get("")
async def list_templates(
    is_active: Optional[bool] = Query(None),
    target_pack: Optional[str] = Query(None),
    template_type: Optional[str] = Query(None),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Listar todos los templates de invitación.
    
    Filtros:
    - is_active: true/false
    - target_pack: GUARDIAN, MOTOR, FORTALEZA, ALL
    - template_type: PROFESSIONAL_NEUTRAL, MICRO_CONTEXTUAL, CUSTOM
    """
    where = []
    args = []
    i = 1
    
    if is_active is not None:
        where.append(f"is_active = ${i}")
        args.append(is_active)
        i += 1
    
    if target_pack:
        where.append(f"(target_pack = ${i} OR target_pack = 'ALL')")
        args.append(target_pack)
        i += 1
    
    if template_type:
        where.append(f"template_type = ${i}")
        args.append(template_type)
        i += 1
    
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    
    rows = await conn.fetch(
        f"""
        SELECT 
            id,
            template_name,
            template_type,
            display_name,
            template_text,
            required_variables,
            target_pack,
            is_active,
            is_default,
            weight,
            times_sent,
            times_accepted,
            acceptance_rate,
            description,
            notes,
            created_at,
            updated_at
        FROM linkedin_invite_templates
        {where_sql}
        ORDER BY 
            is_default DESC,
            acceptance_rate DESC NULLS LAST,
            template_type,
            created_at DESC
        """,
        *args
    )
    
    return {
        "templates": [dict(r) for r in rows],
        "count": len(rows)
    }


@router.get("/{template_id}")
async def get_template(
    template_id: UUID,
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """Obtener un template específico."""
    row = await conn.fetchrow(
        "SELECT * FROM linkedin_invite_templates WHERE id = $1",
        template_id
    )
    
    if not row:
        raise HTTPException(404, "Template not found")
    
    return dict(row)


@router.post("")
async def create_template(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Crear un nuevo template.
    
    Body:
    {
        "template_name": "custom_pack_guardian_v1",
        "template_type": "CUSTOM",
        "display_name": "Custom para GUARDIAN",
        "template_text": "Hola {{nombre}}, ...",
        "required_variables": ["nombre", "empresa"],
        "target_pack": "GUARDIAN",
        "weight": 30,
        "description": "Template personalizado"
    }
    """
    required = ["template_name", "template_type", "display_name", "template_text"]
    if not all(k in payload for k in required):
        raise HTTPException(400, f"Required: {', '.join(required)}")
    
    # Validar que template_name sea único
    exists = await conn.fetchval(
        "SELECT EXISTS(SELECT 1 FROM linkedin_invite_templates WHERE template_name = $1)",
        payload["template_name"]
    )
    if exists:
        raise HTTPException(400, f"Template name '{payload['template_name']}' already exists")
    
    template_id = await conn.fetchval(
        """
        INSERT INTO linkedin_invite_templates (
            template_name,
            template_type,
            display_name,
            template_text,
            required_variables,
            target_pack,
            weight,
            description,
            notes,
            created_by
        ) VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7, $8, $9, $10)
        RETURNING id
        """,
        payload["template_name"],
        payload["template_type"],
        payload["display_name"],
        payload["template_text"],
        json.dumps(payload.get("required_variables", [])),
        payload.get("target_pack", "ALL"),
        payload.get("weight", 50),
        payload.get("description"),
        payload.get("notes"),
        payload.get("created_by", "system")
    )
    
    return {
        "id": str(template_id),
        "template_name": payload["template_name"],
        "created": True
    }


@router.patch("/{template_id}")
async def update_template(
    template_id: UUID,
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Actualizar un template.
    
    Campos editables:
    - display_name
    - template_text
    - required_variables
    - weight
    - is_active
    - is_default
    - description
    - notes
    """
    exists = await conn.fetchval(
        "SELECT id FROM linkedin_invite_templates WHERE id = $1",
        template_id
    )
    if not exists:
        raise HTTPException(404, "Template not found")
    
    updates = []
    args = []
    i = 1
    
    editable_fields = [
        "display_name", "template_text", "target_pack",
        "weight", "is_active", "is_default", 
        "description", "notes"
    ]
    
    for field in editable_fields:
        if field in payload:
            updates.append(f"{field} = ${i}")
            args.append(payload[field])
            i += 1
    
    if "required_variables" in payload:
        updates.append(f"required_variables = ${i}::jsonb")
        args.append(json.dumps(payload["required_variables"]))
        i += 1
    
    if not updates:
        raise HTTPException(400, "No fields to update")
    
    updates.append("updated_at = NOW()")
    args.append(template_id)
    
    await conn.execute(
        f"UPDATE linkedin_invite_templates SET {', '.join(updates)} WHERE id = ${i}",
        *args
    )
    
    return {"id": str(template_id), "updated": True}


@router.delete("/{template_id}")
async def delete_template(
    template_id: UUID,
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Desactivar un template (soft delete).
    No se eliminan físicamente para mantener métricas históricas.
    """
    exists = await conn.fetchval(
        "SELECT id FROM linkedin_invite_templates WHERE id = $1",
        template_id
    )
    if not exists:
        raise HTTPException(404, "Template not found")
    
    await conn.execute(
        "UPDATE linkedin_invite_templates SET is_active = FALSE, updated_at = NOW() WHERE id = $1",
        template_id
    )
    
    return {"id": str(template_id), "deactivated": True}


@router.get("/select/for-lead")
async def select_template_for_lead(
    pack: str = Query("ALL"),
    lead_id: Optional[UUID] = Query(None),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Selecciona un template usando A/B testing (weighted random).
    
    Params:
    - pack: GUARDIAN, MOTOR, FORTALEZA, ALL
    - lead_id: (opcional) para logging
    
    Retorna el template seleccionado según los pesos configurados.
    """
    row = await conn.fetchrow(
        "SELECT * FROM get_template_for_lead($1)",
        pack
    )
    
    if not row:
        raise HTTPException(404, f"No active templates found for pack '{pack}'")
    
    return {
        "template_id": str(row["template_id"]),
        "template_name": row["template_name"],
        "template_text": row["template_text"],
        "required_variables": row["required_variables"],
        "pack": pack,
        "lead_id": str(lead_id) if lead_id else None
    }


@router.post("/{template_id}/stats/increment")
async def increment_template_stats(
    template_id: UUID,
    stat_type: str = Body(..., embed=True),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Incrementar estadísticas de un template.
    
    stat_type: "sent" o "accepted"
    
    Llamar cuando:
    - "sent": Se envía una invitación con este template
    - "accepted": Un lead acepta una invitación de este template
    """
    if stat_type not in ["sent", "accepted"]:
        raise HTTPException(400, "stat_type must be 'sent' or 'accepted'")
    
    exists = await conn.fetchval(
        "SELECT id FROM linkedin_invite_templates WHERE id = $1",
        template_id
    )
    if not exists:
        raise HTTPException(404, "Template not found")
    
    await conn.execute(
        "SELECT increment_template_stats($1, $2)",
        template_id,
        stat_type
    )
    
    # Obtener stats actualizadas
    stats = await conn.fetchrow(
        """
        SELECT times_sent, times_accepted, acceptance_rate
        FROM linkedin_invite_templates
        WHERE id = $1
        """,
        template_id
    )
    
    return {
        "template_id": str(template_id),
        "stat_type": stat_type,
        "times_sent": stats["times_sent"],
        "times_accepted": stats["times_accepted"],
        "acceptance_rate": float(stats["acceptance_rate"])
    }


@router.get("/stats/comparison")
async def compare_template_stats(
    target_pack: Optional[str] = Query(None),
    min_samples: int = Query(10),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Comparar performance de templates (A/B test results).
    
    Params:
    - target_pack: Filtrar por pack
    - min_samples: Mínimo de envíos para incluir en comparación
    
    Retorna ranking de templates por acceptance_rate.
    """
    where = ["times_sent >= $1"]
    args = [min_samples]
    i = 2
    
    if target_pack:
        where.append(f"(target_pack = ${i} OR target_pack = 'ALL')")
        args.append(target_pack)
        i += 1
    
    where_sql = "WHERE " + " AND ".join(where)
    
    rows = await conn.fetch(
        f"""
        SELECT 
            template_name,
            display_name,
            template_type,
            target_pack,
            times_sent,
            times_accepted,
            acceptance_rate,
            is_active,
            weight
        FROM linkedin_invite_templates
        {where_sql}
        ORDER BY acceptance_rate DESC NULLS LAST, times_sent DESC
        """,
        *args
    )
    
    return {
        "templates": [dict(r) for r in rows],
        "count": len(rows),
        "filters": {
            "target_pack": target_pack,
            "min_samples": min_samples
        }
    }


@router.post("/render")
async def render_template(
    payload: Dict[str, Any] = Body(...),
    conn: Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Renderizar un template con variables reales.
    
    Body:
    {
        "template_id": "uuid",
        "variables": {
            "nombre": "María",
            "empresa": "Clínica Dental López",
            "rol": "Directora",
            "ciudad": "Madrid"
        }
    }
    
    Retorna el mensaje renderizado listo para enviar.
    """
    template_id = payload.get("template_id")
    variables = payload.get("variables", {})
    
    if not template_id:
        raise HTTPException(400, "template_id is required")
    
    # Obtener template
    template = await conn.fetchrow(
        "SELECT template_text, required_variables FROM linkedin_invite_templates WHERE id = $1",
        UUID(template_id)
    )
    
    if not template:
        raise HTTPException(404, "Template not found")
    
    text = template["template_text"]
    required_vars = template["required_variables"]
    
    # Verificar que tenemos todas las variables requeridas
    missing = [v for v in required_vars if v not in variables]
    if missing:
        raise HTTPException(
            400,
            f"Missing required variables: {', '.join(missing)}"
        )
    
    # Renderizar
    rendered = text
    for key, value in variables.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
    
    return {
        "template_id": template_id,
        "rendered_message": rendered,
        "character_count": len(rendered),
        "variables_used": list(variables.keys())
    }