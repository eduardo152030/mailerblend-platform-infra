#!/usr/bin/env python3
import os, subprocess, json, uuid, datetime, textwrap

CRM_DB_HOST = os.getenv("CRM_DB_HOST", "192.168.1.118")
CRM_DB_CONTAINER = os.getenv("CRM_DB_CONTAINER", "supabase-db")
CRM_DB_USER = os.getenv("CRM_DB_USER", "pgadmin2026f")
CRM_DB_PASS = os.getenv("CRM_DB_PASS", "l1W3YyXJUyqfSrkhdJMe")
CRM_DB_NAME = os.getenv("CRM_DB_NAME", "postgres")

SSH_OPTS = ["-o","StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-o","LogLevel=ERROR"]

def sh(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)

def psql(sql: str) -> str:
    remote = (
        f"docker exec -i {CRM_DB_CONTAINER} env PGPASSWORD='{CRM_DB_PASS}' "
        f"psql -X -q -At -v ON_ERROR_STOP=1 -U '{CRM_DB_USER}' -d '{CRM_DB_NAME}' "
        f"-c {json.dumps(sql)}"
    )
    cp = sh(["ssh", *SSH_OPTS, f"root@{CRM_DB_HOST}", remote])
    return (cp.stdout or "").strip()

def insert_contacto(c: dict) -> str:
    # IMPORTANTE: no seteamos id, Postgres lo genera (uuid_generate_v4()).
    # También metemos campos requeridos por checks: origen, estado, pack_asignado.
    sql = f"""
    INSERT INTO contactos (
      nombre,email,telefono,company_name,cargo,tipo_empresa,ciudad,pais,
      origen,estado,pack_asignado,gdpr_consent,marketing_consent,created_by,notas
    ) VALUES (
      {q(c['nombre'])},{q(c['email'])},{q(c['telefono'])},{q(c['company_name'])},{q(c.get('cargo'))},
      {q(c.get('tipo_empresa'))},{q(c.get('ciudad'))},{q(c.get('pais','ES'))},
      {q(c.get('origen','FORMULARIO_WEB'))},{q(c.get('estado','ACTIVO'))},{q(c.get('pack_asignado','NO_ASIGNADO'))},
      {bool_sql(c.get('gdpr_consent', True))},{bool_sql(c.get('marketing_consent', False))},
      'seed',
      {q(c.get('notas'))}
    )
    ON CONFLICT (email) DO UPDATE SET
      nombre=EXCLUDED.nombre,
      telefono=EXCLUDED.telefono,
      company_name=EXCLUDED.company_name,
      updated_at=NOW()
    RETURNING id;
    """
    return psql(sql)

def insert_parametros_utm(r: dict) -> str:
    # Dedup simple: mismo contacto + misma combinación UTM/click ids.
    exists = f"""
    SELECT id FROM parametros_utm
    WHERE contacto_id = {q(r['contacto_id'])}
      AND COALESCE(utm_source,'') = COALESCE({q(r.get('utm_source'))},'')
      AND COALESCE(utm_medium,'') = COALESCE({q(r.get('utm_medium'))},'')
      AND COALESCE(utm_campaign,'') = COALESCE({q(r.get('utm_campaign'))},'')
      AND COALESCE(gclid,'') = COALESCE({q(r.get('gclid'))},'')
      AND COALESCE(msclkid,'') = COALESCE({q(r.get('msclkid'))},'')
      AND COALESCE(li_fat_id,'') = COALESCE({q(r.get('li_fat_id'))},'')
    LIMIT 1;
    """
    existing = psql(exists)
    if existing:
        return existing

    sql = f"""
    INSERT INTO parametros_utm (
      contacto_id,utm_source,utm_medium,utm_campaign,utm_content,utm_term,
      gclid,msclkid,li_fat_id,ads_platform,landing_url,first_visit_at,created_at
    ) VALUES (
      {q(r['contacto_id'])},{q(r.get('utm_source'))},{q(r.get('utm_medium'))},{q(r.get('utm_campaign'))},{q(r.get('utm_content'))},{q(r.get('utm_term'))},
      {q(r.get('gclid'))},{q(r.get('msclkid'))},{q(r.get('li_fat_id'))},{q(r.get('ads_platform'))},{q(r.get('landing_url'))},
      NOW() - INTERVAL '5 minutes', NOW()
    )
    RETURNING id;
    """
    return psql(sql)

def insert_formulario_web(f: dict) -> str:
    # Columnas NOT NULL: contacto_id, mensaje, servicio_relacionado (y checks)
    sql = f"""
    INSERT INTO formulario_web (
      contacto_id, servicio_relacionado, como_nos_conociste,
      tipo_solucion, situacion_infraestructura, problema_fiabilidad,
      parte_infraestructura, herramientas_conectar, tipo_soporte,
      mensaje, submitted_at
    ) VALUES (
      {q(f['contacto_id'])},
      {q(f['servicio_relacionado'])},
      {q(f.get('como_nos_conociste','Google / Buscador'))},
      {q(f.get('tipo_solucion'))},
      {q(f.get('situacion_infraestructura'))},
      {q(f.get('problema_fiabilidad'))},
      {q(f.get('parte_infraestructura'))},
      {q(f.get('herramientas_conectar'))},
      {q(f.get('tipo_soporte'))},
      {q(f['mensaje'])},
      NOW()
    )
    RETURNING id;
    """
    return psql(sql)

def q(v):
    if v is None:
        return "NULL"
    s = str(v).replace("'", "''")
    return f"'{s}'"

def bool_sql(v: bool) -> str:
    return "TRUE" if v else "FALSE"

def main():
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  📊 Seed CRM (PostgreSQL) — Formulario web dinámico")
    print(f"  🎯 Target: {CRM_DB_HOST}:{CRM_DB_CONTAINER} db={CRM_DB_NAME} user={CRM_DB_USER}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # Mapping 1:1 basado en tu JSON del formulario (servicio -> campo dinámico). :contentReference[oaicite:2]{index=2}
    cases = [
        ("Desarrollo web y software a medida", {"tipo_solucion": "Web profesional / landing"}),
        ("Cloud & DevOps", {"situacion_infraestructura": "AWS"}),
        ("SRE / Observabilidad", {"problema_fiabilidad": "Caídas frecuentes sin saber por qué"}),
        ("Infraestructura gestionada", {"parte_infraestructura": "Todo lo anterior"}),
        ("Integraciones / Automatización", {"herramientas_conectar": "HubSpot + Holded + Slack + Google Sheets"}),
        ("Outsourcing IT / CAU", {"tipo_soporte": "Externalización completa IT"}),
    ]

    base_contact = {
        "telefono": "+34 600 111 222",
        "ciudad": "Barcelona",
        "pais": "ES",
        "origen": "FORMULARIO_WEB",   # check contactos_origen_check
        "estado": "ACTIVO",           # check contactos_estado_check
        "pack_asignado": "NO_ASIGNADO",
        "gdpr_consent": True,
        "marketing_consent": False,
    }

    for i, (servicio, extra) in enumerate(cases, 1):
        email = f"seed.{i}.{uuid.uuid4().hex[:6]}@example.com"
        nombre = f"Seed Lead {i} ({servicio[:18]})"
        company = f"Empresa Seed {i}"

        cid = insert_contacto({
            **base_contact,
            "nombre": nombre,
            "email": email,
            "company_name": company,
            "tipo_empresa": "Pyme",
            "cargo": "Operations Manager",
            "notas": f"seed formulario dinámico: {servicio}",
        })
        print(f"👤 Contacto {i}: {email} ✅ {cid}")

        _ = insert_parametros_utm({
            "contacto_id": cid,
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": f"seed-{i}-{servicio[:12].lower().replace(' ','-')}",
            "gclid": f"TEST-GCLID-{i}",
            "ads_platform": "GOOGLE",
            "landing_url": "https://www.nucleotecnologico.es/contacto",
        })
        print(f"🔗 UTM {i}: contacto_id={cid} ✅")

        msg = textwrap.dedent(f"""
        Hola, soy un lead de prueba #{i}.
        Servicio: {servicio}
        Extra: {json.dumps(extra, ensure_ascii=False)}
        """).strip()

        fid = insert_formulario_web({
            "contacto_id": cid,
            "servicio_relacionado": servicio,
            "como_nos_conociste": "Google / Buscador",
            "mensaje": msg,
            **extra
        })
        print(f"📝 Formulario {i}: ✅ {fid}\n")

    print("✅ Seed completado.")
    print("💡 Verifica en API: /_svc/v1/contacts?q=seed&limit=50 y /snapshot con un UUID real.")

if __name__ == "__main__":
    main()
