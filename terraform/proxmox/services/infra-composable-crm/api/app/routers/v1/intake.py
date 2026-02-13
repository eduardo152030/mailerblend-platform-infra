from __future__ import annotations

import os
import secrets
from typing import Any, Dict, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from asyncpg import Connection

from app.db import get_db

router = APIRouter(prefix="/v1/intake", tags=["intake"])


# ----------------------------
# Security: Ingest Secret
# ----------------------------
def get_ingest_secret(
    x_ingest_secret: Optional[str] = Header(default=None, alias="X-Ingest-Secret"),
) -> bool:
    """
    Protege el endpoint con un shared secret:
      - .env: CRM_INGEST_SECRET=...
      - Header: X-Ingest-Secret: ...
    """
    expected = os.getenv("CRM_INGEST_SECRET")

    # Si no está definido en el servidor, fallamos "cerrado" (secure by default)
    if not expected:
        raise HTTPException(status_code=500, detail="CRM_INGEST_SECRET not configured")

    if not x_ingest_secret:
        raise HTTPException(status_code=401, detail="Missing ingest secret")

    # Constant-time compare
    if not secrets.compare_digest(x_ingest_secret, expected):
        raise HTTPException(status_code=401, detail="Invalid ingest secret")

    return True


# ----------------------------
# Payload (contrato MVP)
# ----------------------------
class UTM(BaseModel):
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None
    utm_term: Optional[str] = None
    adgroup: Optional[str] = None
    device: Optional[str] = None
    placement: Optional[str] = None
    keyword: Optional[str] = None
    creative: Optional[str] = None
    gclid: Optional[str] = None
    msclkid: Optional[str] = None
    li_fat_id: Optional[str] = None
    fbclid: Optional[str] = None
    ads_platform: Optional[str] = None
    landing_url: Optional[str] = None
    referrer_url: Optional[str] = None
    first_visit_at: Optional[str] = None  # ISO string; DB castea
    # created_at lo deja el server


class WebForm(BaseModel):
    servicio_relacionado: str
    como_nos_conociste: Optional[str] = None
    mensaje: str

    # Campos dinámicos (opcionales)
    tipo_solucion: Optional[str] = None
    situacion_infraestructura: Optional[str] = None
    problema_fiabilidad: Optional[str] = None
    parte_infraestructura: Optional[str] = None
    herramientas_conectar: Optional[str] = None
    tipo_soporte: Optional[str] = None

    # meta opcional
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    origen: Optional[str] = "Formulario web"


class LeadIntakeRequest(BaseModel):
    # Identidad
    nombre: str
    email: str
    telefono: Optional[str] = None
    company_name: Optional[str] = None
    company_size: Optional[str] = None
    cargo: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    tipo_empresa: Optional[str] = None

    # Consentimientos
    gdpr_consent: bool = False
    marketing_consent: bool = False

    # Tracking + Form
    utm: Optional[UTM] = None
    form: WebForm

    # para auditoría
    source: str = Field(default="lambda", description="quien envía el intake: lambda/api/etc")


# ----------------------------
# Triage (MVP, portable)
# ----------------------------
def compute_triage(payload: LeadIntakeRequest) -> Dict[str, Any]:
    """
    Devuelve:
      lead_tag: Cold/Warm/Hot/Qualified/Unqualified
      prioridad: Alta/Media/Baja
      next_action: SEND_EMAIL/CALL/BOOK_MEETING/SEND_PROPOSAL/FOLLOW_UP/NO_ACTION
      probabilidad: 0..100
      score: int
      breakdown: dict
    """
    score = 0
    breakdown: Dict[str, Any] = {}

    # Señales básicas (MVP)
    if payload.gdpr_consent:
        score += 5
        breakdown["gdpr_consent"] = 5

    if payload.company_name:
        score += 5
        breakdown["company_name"] = 5

    if payload.cargo and payload.cargo.lower() in ("owner", "ceo", "founder", "director", "cto"):
        score += 15
        breakdown["decision_maker"] = 15

    # Por servicio (intención)
    srv = (payload.form.servicio_relacionado or "").lower()
    if "cloud" in srv or "devops" in srv or "sre" in srv:
        score += 20
        breakdown["service_intent_high"] = 20
    elif "infraestructura" in srv:
        score += 15
        breakdown["service_intent_mid"] = 15
    elif "automatización" in srv or "integraciones" in srv:
        score += 15
        breakdown["service_intent_mid"] = 15
    elif "outsourcing" in srv or "cau" in srv:
        score += 15
        breakdown["service_intent_mid"] = 15
    elif "desarrollo" in srv:
        score += 10
        breakdown["service_intent_low"] = 10

    # Longitud del mensaje como proxy de dolor
    msg_len = len(payload.form.mensaje or "")
    if msg_len >= 200:
        score += 20
        breakdown["message_detail"] = 20
    elif msg_len >= 80:
        score += 10
        breakdown["message_detail"] = 10

    # Tracking fuerte (click id)
    utm = payload.utm
    has_click_id = False
    if utm and (utm.gclid or utm.msclkid or utm.li_fat_id or utm.fbclid):
        score += 10
        breakdown["click_id_present"] = 10
        has_click_id = True

    # Clasificación simple
    if score >= 55:
        lead_tag = "Hot"
        prioridad = "Alta"
        next_action = "BOOK_MEETING"
        probabilidad = 70
    elif score >= 35:
        lead_tag = "Warm"
        prioridad = "Media"
        next_action = "FOLLOW_UP"
        probabilidad = 45
    elif score >= 20:
        lead_tag = "Cold"
        prioridad = "Media"
        next_action = "FOLLOW_UP"
        probabilidad = 20
    else:
        lead_tag = "Unqualified"
        prioridad = "Baja"
        next_action = "NO_ACTION"
        probabilidad = 5

    # "Qualified" (regla MVP): Warm/Hot + click_id o mucho detalle
    if lead_tag in ("Warm", "Hot") and (has_click_id or msg_len >= 250):
        lead_tag = "Qualified"
        prioridad = "Alta"
        next_action = "BOOK_MEETING"
        probabilidad = max(probabilidad, 75)

    return {
        "lead_tag": lead_tag,
        "prioridad": prioridad,
        "next_action": next_action,
        "probabilidad": probabilidad,
        "score": score,
        "breakdown": breakdown,
    }


# ----------------------------
# Endpoint
# ----------------------------
@router.post("/webform")
async def intake_webform(
    req: LeadIntakeRequest,
    _: bool = Depends(get_ingest_secret),  # ✅ auth gate (secret)
    conn: Connection = Depends(get_db),
) -> Dict[str, Any]:
    """
    Inserta/Upsert:
      - contactos (dedupe email) - SIN ON CONFLICT
      - parametros_utm (si viene)
      - formulario_web
      - oportunidades (si lead_tag in Cold/Warm/Hot/Qualified)
      - historial (EVENT::LEAD_CREATED + EVENT::LEAD_QUALIFIED)
    """
    triage = compute_triage(req)

    async with conn.transaction():
        # 1) contacto (upsert MANUAL por email - sin ON CONFLICT)
        existing_contact = await conn.fetchrow(
            "SELECT id FROM contactos WHERE email = $1",
            req.email,
        )

        if existing_contact:
            # UPDATE contacto existente
            contact = await conn.fetchrow(
                """
                UPDATE contactos SET
                  nombre = $2,
                  telefono = $3,
                  company_name = $4,
                  company_size = $5, 
                  cargo = $6,
                  ciudad = $7,
                  pais = $8,
                  tipo_empresa = $9,
                  gdpr_consent = $10,
                  gdpr_consent_date = CASE
                    WHEN $10 AND gdpr_consent_date IS NULL THEN now()
                    ELSE gdpr_consent_date
                  END,
                  marketing_consent = $11,
                  updated_at = now(),
                  created_by = COALESCE(created_by, $12)
                WHERE id = $1
                RETURNING *
                """,
                existing_contact["id"],
                req.nombre,
                req.telefono,
                req.company_name,
                req.company_size,  
                req.cargo,
                req.ciudad,
                req.pais,
                req.tipo_empresa,
                req.gdpr_consent,
                req.marketing_consent,
                req.source,
            )
        else:
            # INSERT nuevo contacto
            contact = await conn.fetchrow(
                """
                INSERT INTO contactos (
                  nombre, email, telefono, company_name, company_size, cargo, ciudad, pais, tipo_empresa,
                  origen, estado, pack_asignado, gdpr_consent, gdpr_consent_date,
                  marketing_consent, created_by
                )
                VALUES (
                  $1,$2,$3,$4,$5,$6,$7,$8,$9,
                  'FORMULARIO_WEB','ACTIVO','NO_ASIGNADO',$10, CASE WHEN $10 THEN now() ELSE NULL END,
                  $11, $12
                )
                RETURNING *
                """,
                req.nombre,
                req.email,
                req.telefono,
                req.company_name,
                req.company_size, 
                req.cargo,
                req.ciudad,
                req.pais,
                req.tipo_empresa,
                req.gdpr_consent,
                req.marketing_consent,
                req.source,
            )

        if not contact:
            raise HTTPException(status_code=500, detail="Failed to upsert contact")

        contacto_id = UUID(str(contact["id"]))

        # 2) utm
        utm_id = None
        if req.utm:
            if req.utm.gclid or req.utm.msclkid or req.utm.li_fat_id:
                existing_utm = await conn.fetchrow(
                    """
                    SELECT id FROM parametros_utm
                    WHERE contacto_id = $1
                      AND gclid IS NOT DISTINCT FROM $2
                      AND msclkid IS NOT DISTINCT FROM $3
                      AND li_fat_id IS NOT DISTINCT FROM $4
                    LIMIT 1
                    """,
                    contacto_id,
                    req.utm.gclid,
                    req.utm.msclkid,
                    req.utm.li_fat_id,
                )

                if existing_utm:
                    row = await conn.fetchrow(
                        """
                        UPDATE parametros_utm SET
                          utm_source = $2,
                          utm_medium = $3,
                          utm_campaign = $4,
                          utm_content = $5,
                          utm_term = $6,
                          adgroup = $7,
                          device = $8,
                          placement = $9,
                          keyword = $10,
                          creative = $11,
                          fbclid = $12,
                          ads_platform = $13,
                          landing_url = $14,
                          referrer_url = $15,
                          first_visit_at = COALESCE(first_visit_at, $16::timestamptz)
                        WHERE id = $1
                        RETURNING id
                        """,
                        existing_utm["id"],
                        req.utm.utm_source,
                        req.utm.utm_medium,
                        req.utm.utm_campaign,
                        req.utm.utm_content,
                        req.utm.utm_term,
                        req.utm.adgroup,
                        req.utm.device,
                        req.utm.placement,
                        req.utm.keyword,
                        req.utm.creative,
                        req.utm.fbclid,
                        req.utm.ads_platform,
                        req.utm.landing_url,
                        req.utm.referrer_url,
                        datetime.fromisoformat(req.utm.first_visit_at.replace("Z", "+00:00")) if req.utm.first_visit_at else None,
                    )
                    utm_id = str(row["id"]) if row else None
                else:
                    row = await conn.fetchrow(
                        """
                        INSERT INTO parametros_utm (
                          contacto_id,
                          utm_source, utm_medium, utm_campaign, utm_content, utm_term,
                          adgroup, device, placement, keyword, creative,
                          gclid, msclkid, li_fat_id, fbclid, ads_platform,
                          landing_url, referrer_url,
                          first_visit_at, created_at
                        )
                        VALUES (
                          $1,
                          $2,$3,$4,$5,$6,
                          $7,$8,$9,$10,$11,
                          $12,$13,$14,$15,$16,
                          $17,$18,
                          $19::timestamptz,
                          now()
                        )
                        RETURNING id
                        """,
                        contacto_id,
                        req.utm.utm_source,
                        req.utm.utm_medium,
                        req.utm.utm_campaign,
                        req.utm.utm_content,
                        req.utm.utm_term,
                        req.utm.adgroup,
                        req.utm.device,
                        req.utm.placement,
                        req.utm.keyword,
                        req.utm.creative,
                        req.utm.gclid,
                        req.utm.msclkid,
                        req.utm.li_fat_id,
                        req.utm.fbclid,
                        req.utm.ads_platform,
                        req.utm.landing_url,
                        req.utm.referrer_url,
                        datetime.fromisoformat(req.utm.first_visit_at.replace("Z", "+00:00")) if req.utm.first_visit_at else None,
                    )
                    utm_id = str(row["id"]) if row else None
            else:
                row = await conn.fetchrow(
                    """
                    INSERT INTO parametros_utm (
                      contacto_id,
                      utm_source, utm_medium, utm_campaign, utm_content, utm_term,
                      adgroup, device, placement, keyword, creative,
                      gclid, msclkid, li_fat_id, fbclid, ads_platform,
                      landing_url, referrer_url, first_visit_at, created_at
                    )
                    VALUES (
                      $1,
                      $2,$3,$4,$5,$6,
                      $7,$8,$9,$10,$11,
                      NULL,NULL,NULL,$12,$13,
                      $14,$15,
                      $16::timestamptz,
                      now()
                    )
                    RETURNING id
                    """,
                    contacto_id,
                    req.utm.utm_source,
                    req.utm.utm_medium,
                    req.utm.utm_campaign,
                    req.utm.utm_content,
                    req.utm.utm_term,
                    req.utm.adgroup,
                    req.utm.device,
                    req.utm.placement,
                    req.utm.keyword,
                    req.utm.creative,
                    req.utm.fbclid,
                    req.utm.ads_platform,
                    req.utm.landing_url,
                    req.utm.referrer_url,
                    datetime.fromisoformat(req.utm.first_visit_at.replace("Z", "+00:00")) if req.utm.first_visit_at else None,
                )
                utm_id = str(row["id"]) if row else None

        # 3) formulario_web
        form = req.form
        formulario = await conn.fetchrow(
            """
            INSERT INTO formulario_web (
              contacto_id,
              servicio_relacionado,
              como_nos_conociste,
              tipo_solucion,
              situacion_infraestructura,
              problema_fiabilidad,
              parte_infraestructura,
              herramientas_conectar,
              tipo_soporte,
              mensaje,
              submitted_at,
              origen,
              ip_address,
              user_agent
            )
            VALUES (
              $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,
              now(), $11, $12, $13
            )
            RETURNING *
            """,
            contacto_id,
            form.servicio_relacionado,
            form.como_nos_conociste,
            form.tipo_solucion,
            form.situacion_infraestructura,
            form.problema_fiabilidad,
            form.parte_infraestructura,
            form.herramientas_conectar,
            form.tipo_soporte,
            form.mensaje,
            form.origen or "Formulario web",
            form.ip_address,
            form.user_agent,
        )

        formulario_id = UUID(str(formulario["id"])) if formulario else None

        # 4) oportunidad (si aplica)
        oportunidad_id = None
        if triage["lead_tag"] in ("Cold", "Warm", "Hot", "Qualified"):
            deal_name = f"{form.servicio_relacionado} - {req.company_name or req.nombre}"
            oportunidad = await conn.fetchrow(
                """
                INSERT INTO oportunidades (
                  contacto_id,
                  formulario_id,
                  deal_name,
                  estado,
                  lead_tag,
                  prioridad,
                  next_action,
                  probabilidad,
                  pack,
                  created_at,
                  updated_at
                )
                VALUES (
                  $1,$2,$3,
                  'Nuevo',
                  $4,$5,$6,$7,
                  'NO_ASIGNADO',
                  now(), now()
                )
                RETURNING id
                """,
                contacto_id,
                formulario_id,
                deal_name,
                triage["lead_tag"],
                triage["prioridad"],
                triage["next_action"],
                triage["probabilidad"],
            )
            oportunidad_id = UUID(str(oportunidad["id"])) if oportunidad else None

        # 5) historial: eventos
        await conn.execute(
            """
            INSERT INTO historial (
              contacto_id, oportunidad_id, type, subject, notes,
              activity_date, created_by, created_at
            )
            VALUES ($1,$2,'NOTE','EVENT::LEAD_CREATED',$3, now(), $4, now())
            """,
            contacto_id,
            oportunidad_id,
            f'{{"source":"{req.source}"}}',
            req.source,
        )

        await conn.execute(
            """
            INSERT INTO historial (
              contacto_id, oportunidad_id, type, subject, notes,
              activity_date, created_by, created_at
            )
            VALUES ($1,$2,'NOTE','EVENT::LEAD_QUALIFIED',$3, now(), $4, now())
            """,
            contacto_id,
            oportunidad_id,
            (
                "{"
                f"\"lead_tag\":\"{triage['lead_tag']}\","
                f"\"priority\":\"{triage['prioridad']}\","
                f"\"next_action_key\":\"{triage['next_action']}\","
                f"\"score\":{triage['score']},"
                f"\"utm_id\":{('\"'+utm_id+'\"') if utm_id else 'null'},"
                f"\"formulario_id\":{('\"'+str(formulario_id)+'\"') if formulario_id else 'null'}"
                "}"
            ),
            req.source,
        )

    return {
        "contact_id": str(contacto_id),
        "formulario_id": str(formulario_id) if formulario_id else None,
        "utm_id": utm_id,
        "oportunidad_id": str(oportunidad_id) if oportunidad_id else None,
        "triage": triage,
    }