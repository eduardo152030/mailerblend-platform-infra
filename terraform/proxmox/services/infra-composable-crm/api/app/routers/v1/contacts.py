from typing import Optional, Dict, Any
from uuid import UUID
import json

from fastapi import APIRouter, Depends, Query, HTTPException
from asyncpg import Connection
from pydantic import BaseModel, EmailStr, Field

from app.db import get_db

router = APIRouter(prefix="/v1/contacts", tags=["contacts"])


# ─── LOGGING ──────────────────────────────────────────────────────────────────

async def log_event(
    conn: Connection,
    contacto_id: UUID,
    event_key: str,
    payload: Dict[str, Any],
    created_by: str = "system",
) -> None:
    """
    Registra un evento en la tabla historial.
    
    Args:
        conn: Conexión a la base de datos
        contacto_id: ID del contacto relacionado
        event_key: Clave del evento (ej: CONTACT_CREATED, CONTACT_UPDATED)
        payload: Datos adicionales del evento
        created_by: Usuario/sistema que generó el evento
    """
    # Mapear event_key a los tipos válidos de historial
    event_type_map = {
        "CONTACT_CREATED": "NOTE",
        "CONTACT_UPDATED": "NOTE",
    }
    
    event_subject_map = {
        "CONTACT_CREATED": "Contacto creado vía API",
        "CONTACT_UPDATED": "Contacto actualizado vía API",
    }
    
    await conn.execute(
        """
        INSERT INTO historial (
            contacto_id,
            type,
            subject,
            notes,
            created_by,
            activity_date,
            created_at
        ) VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
        """,
        contacto_id,
        event_type_map.get(event_key, "NOTE"),
        event_subject_map.get(event_key, f"Evento: {event_key}"),
        json.dumps(payload),
        created_by,
    )


# ─── MODELS ───────────────────────────────────────────────────────────────────

class ContactCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=200)
    cargo: Optional[str] = Field(None, max_length=100)
    ciudad: Optional[str] = Field(None, max_length=100)
    pais: Optional[str] = Field("ES", max_length=2)
    tipo_empresa: Optional[str] = Field(None, max_length=50)

    # opcionales "crm"
    origen: str = Field("MANUAL", max_length=50)  # debe cumplir contactos_origen_check
    estado: str = Field("ACTIVO", max_length=50)  # debe cumplir contactos_estado_check
    pack_asignado: str = Field("NO_ASIGNADO", max_length=50)
    
    # GDPR compliance
    gdpr_consent: bool = Field(False, description="Consentimiento GDPR obligatorio")
    marketing_consent: bool = Field(False, description="Consentimiento marketing opcional")


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _clamp_limit(limit: int) -> int:
    """Limita el rango de resultados entre 1 y 200"""
    if limit < 1:
        return 1
    if limit > 200:
        return 200
    return limit


# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@router.get("")
async def list_contacts(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    q: Optional[str] = Query(None, min_length=1, max_length=200),
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Lista contactos con paginación y búsqueda opcional.
    
    Query params:
    - limit: Número máximo de resultados (1-200, default 50)
    - offset: Offset para paginación (default 0)
    - q: Búsqueda por nombre, email, teléfono o empresa
    """
    limit = _clamp_limit(limit)

    # Campos consistentes con get_contact (sin datos sensibles)
    select_fields = """
        id,
        nombre,
        email,
        telefono,
        company_name,
        cargo,
        ciudad,
        pais,
        tipo_empresa,
        estado,
        origen,
        lead_score,
        pack_asignado,
        created_at,
        updated_at
    """

    if q:
        q_like = f"%{q}%"
        rows = await conn.fetch(
            f"""
            SELECT {select_fields}
            FROM contactos
            WHERE
              nombre ILIKE $3 OR
              email ILIKE $3 OR
              telefono ILIKE $3 OR
              company_name ILIKE $3
            ORDER BY created_at DESC NULLS LAST, id DESC
            LIMIT $1 OFFSET $2
            """,
            limit,
            offset,
            q_like,
        )
        total = await conn.fetchval(
            """
            SELECT count(*)::int
            FROM contactos
            WHERE
              nombre ILIKE $1 OR
              email ILIKE $1 OR
              telefono ILIKE $1 OR
              company_name ILIKE $1
            """,
            q_like,
        )
    else:
        rows = await conn.fetch(
            f"""
            SELECT {select_fields}
            FROM contactos
            ORDER BY created_at DESC NULLS LAST, id DESC
            LIMIT $1 OFFSET $2
            """,
            limit,
            offset,
        )
        total = await conn.fetchval("SELECT count(*)::int FROM contactos")

    items = [dict(r) for r in rows]
    return {
        "items": items,
        "limit": limit,
        "offset": offset,
        "count": len(items),
        "total": int(total or 0),
    }


@router.get("/{contact_id}")
async def get_contact(
    contact_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Obtiene un contacto por ID.
    
    Retorna todos los campos del contacto excepto datos internos sensibles.
    """
    row = await conn.fetchrow(
        """
        SELECT
            id,
            nombre,
            email,
            telefono,
            company_name,
            cargo,
            ciudad,
            pais,
            tipo_empresa,
            estado,
            origen,
            lead_score,
            pack_asignado,
            gdpr_consent,
            gdpr_consent_date,
            marketing_consent,
            created_at,
            updated_at,
            created_by,
            notas
        FROM contactos
        WHERE id = $1
        """,
        contact_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Contact not found")
    return dict(row)


@router.get("/{contact_id}/snapshot")
async def contact_snapshot(
    contact_id: UUID,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Snapshot 360º del contacto: contacto + todas sus relaciones.

    Incluye:
    - Datos del contacto
    - Parámetros UTM (tracking de visitas)
    - Formularios web enviados
    - Oportunidades
    - Historial de actividades
    - Tareas pendientes
    - Presupuestos
    - Facturas

    Orden cronológico real por tabla:
      - parametros_utm: created_at DESC
      - formulario_web: submitted_at DESC
      - historial: COALESCE(activity_date, created_at) DESC
      - oportunidades: created_at DESC
      - pendientes: created_at DESC
      - presupuestos: created_at DESC
      - facturas: created_at DESC
    """
    contact = await conn.fetchrow(
        "SELECT * FROM contactos WHERE id = $1",
        contact_id,
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Parámetros UTM (incluye contacto_nombre si existe)
    utm = await conn.fetch(
        """
        SELECT *
        FROM parametros_utm
        WHERE contacto_id = $1
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT 50
        """,
        contact_id,
    )

    # Formularios web (incluye contacto_nombre si existe)
    submissions = await conn.fetch(
        """
        SELECT 
            id, contacto_id, servicio_relacionado, como_nos_conociste,
            tipo_solucion, situacion_infraestructura, problema_fiabilidad,
            parte_infraestructura, herramientas_conectar, tipo_soporte,
            mensaje, submitted_at, origen,
            host(ip_address) as ip_address,
            user_agent, contacto_nombre
        FROM formulario_web
        WHERE contacto_id = $1
        ORDER BY submitted_at DESC NULLS LAST, id DESC
        LIMIT 50
        """,
        contact_id,
    )

    # Oportunidades (incluye contacto_nombre si existe)
    oportunidades = await conn.fetch(
        """
        SELECT *
        FROM oportunidades
        WHERE contacto_id = $1
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT 100
        """,
        contact_id,
    )

    # Historial de actividades (incluye contacto_nombre si existe)
    historial = await conn.fetch(
        """
        SELECT *
        FROM historial
        WHERE contacto_id = $1
        ORDER BY COALESCE(activity_date, created_at) DESC NULLS LAST, id DESC
        LIMIT 200
        """,
        contact_id,
    )

    # Tareas pendientes (incluye contacto_nombre si existe)
    pendientes = await conn.fetch(
        """
        SELECT *
        FROM pendientes
        WHERE contacto_id = $1
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT 200
        """,
        contact_id,
    )

    # Presupuestos (incluye contacto_nombre si existe)
    presupuestos = await conn.fetch(
        """
        SELECT *
        FROM presupuestos
        WHERE contacto_id = $1
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT 100
        """,
        contact_id,
    )

    # Facturas (incluye contacto_nombre si existe)
    facturas = await conn.fetch(
        """
        SELECT *
        FROM facturas
        WHERE contacto_id = $1
        ORDER BY created_at DESC NULLS LAST, id DESC
        LIMIT 100
        """,
        contact_id,
    )

    return {
        "contact": dict(contact),
        "related": {
            "parametros_utm": [dict(r) for r in utm],
            "formulario_web": [dict(r) for r in submissions],
            "oportunidades": [dict(r) for r in oportunidades],
            "historial": [dict(r) for r in historial],
            "pendientes": [dict(r) for r in pendientes],
            "presupuestos": [dict(r) for r in presupuestos],
            "facturas": [dict(r) for r in facturas],
        },
    }


@router.post("")
async def create_contact(
    payload: ContactCreate,
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Crea o actualiza un contacto.
    
    Comportamiento idempotente por email:
    - Si el email ya existe: actualiza campos básicos + updated_at
    - Si no existe: crea nuevo contacto
    
    IMPORTANTE: Para cumplir GDPR, gdpr_consent debe ser True.
    """
    # Verificar si existe contacto con ese email
    row = await conn.fetchrow(
        "SELECT id FROM contactos WHERE email = $1",
        str(payload.email),
    )

    if row:
        # UPDATE: contacto existente
        contacto_id = row["id"]
        updated = await conn.fetchrow(
            """
            UPDATE contactos
            SET
              nombre = $2,
              telefono = COALESCE($3, telefono),
              company_name = COALESCE($4, company_name),
              cargo = COALESCE($5, cargo),
              ciudad = COALESCE($6, ciudad),
              pais = COALESCE($7, pais),
              tipo_empresa = COALESCE($8, tipo_empresa),
              origen = $9,
              estado = $10,
              pack_asignado = $11,
              gdpr_consent = $12,
              marketing_consent = $13,
              updated_at = NOW()
            WHERE id = $1
            RETURNING *
            """,
            contacto_id,
            payload.nombre,
            payload.telefono,
            payload.company_name,
            payload.cargo,
            payload.ciudad,
            payload.pais,
            payload.tipo_empresa,
            payload.origen,
            payload.estado,
            payload.pack_asignado,
            payload.gdpr_consent,
            payload.marketing_consent,
        )
        
        # Log evento de actualización
        await log_event(
            conn,
            contacto_id=contacto_id,
            event_key="CONTACT_UPDATED",
            payload={
                "email": str(payload.email),
                "source": "api",
            },
            created_by="api",
        )
        
        return dict(updated)

    # INSERT: nuevo contacto
    created = await conn.fetchrow(
        """
        INSERT INTO contactos (
          nombre, email, telefono, company_name, cargo, ciudad, pais, tipo_empresa,
          origen, estado, pack_asignado,
          gdpr_consent, gdpr_consent_date, marketing_consent,
          created_by, created_at, updated_at
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8,
          $9, $10, $11,
          $12, CASE WHEN $12 THEN NOW() ELSE NULL END, $13,
          'api', NOW(), NOW()
        )
        RETURNING *
        """,
        payload.nombre,
        str(payload.email),
        payload.telefono,
        payload.company_name,
        payload.cargo,
        payload.ciudad,
        payload.pais,
        payload.tipo_empresa,
        payload.origen,
        payload.estado,
        payload.pack_asignado,
        payload.gdpr_consent,
        payload.marketing_consent,
    )
    
    # Log evento de creación
    await log_event(
        conn,
        contacto_id=created["id"],
        event_key="CONTACT_CREATED",
        payload={
            "email": str(payload.email),
            "source": "api",
        },
        created_by="api",
    )
    
    return dict(created)