#!/usr/bin/env python3
"""
feed_data_crm.py - Datos de prueba para el CRM (POSTGRES CLONE 1:1)
================================================
CLON 1:1 del script original NocoDB, pero insertando en Postgres (schema CRM v2).

Crea datos de ejemplo para probar:
- Contactos
- Parametros UTM
- Formulario Web (campos dinámicos según servicio)

Características:
- Sin dependencias externas (solo stdlib). Usa ssh + docker exec + psql.
- Idempotente (no duplica si ya existe algo equivalente).
- Misma "forma" del script original: prints, delay, un contacto por servicio.

Requisitos:
- Acceso SSH a root@CRM_DB_HOST
- Contenedor Postgres (por defecto supabase-db)
 desde jainer@Jainer:~/work/mailerblend-platform-infra/terraform/proxmox$
python3 services/infra-composable-crm/database-schemas/03_feed_data_crm_as_user_journey.py
"""

import os
import sys
import time
import random
import subprocess
from datetime import datetime, timedelta

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
CRM_DB_HOST = os.getenv("CRM_DB_HOST", "192.168.1.118")
CRM_DB_CONTAINER = os.getenv("CRM_DB_CONTAINER", "supabase-db")

DELAY = float(os.getenv("DELAY", "0.5"))  # delay entre inserts

# Si no los defines, los autodetectamos con docker inspect (igual que tus runners)
CRM_DB_NAME = os.getenv("CRM_DB_NAME", "")
CRM_DB_USER = os.getenv("CRM_DB_USER", "")
CRM_DB_PASS = os.getenv("CRM_DB_PASS", "")

SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "LogLevel=ERROR",
]

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def sh(cmd: list[str], check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        check=check,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        text=True,
    )

def ssh_cmd(remote_cmd: str) -> list[str]:
    return ["ssh", *SSH_OPTS, f"root@{CRM_DB_HOST}", remote_cmd]

def autodetect_env():
    global CRM_DB_NAME, CRM_DB_USER, CRM_DB_PASS

    if CRM_DB_NAME and CRM_DB_USER and CRM_DB_PASS:
        return

    # extrae env vars del contenedor
    insp = sh(ssh_cmd(
        f"docker inspect {CRM_DB_CONTAINER} --format '{{{{range .Config.Env}}}}{{{{println .}}}}{{{{end}}}}'"
    ))
    lines = insp.stdout.strip().splitlines()
    env = {}
    for ln in lines:
        if "=" in ln:
            k, v = ln.split("=", 1)
            env[k.strip()] = v.strip()

    CRM_DB_NAME = CRM_DB_NAME or env.get("POSTGRES_DB", "postgres")
    CRM_DB_USER = CRM_DB_USER or env.get("POSTGRES_USER", "postgres")
    CRM_DB_PASS = CRM_DB_PASS or env.get("POSTGRES_PASSWORD", "")

    if not CRM_DB_PASS:
        print("❌ No se pudo autodetectar POSTGRES_PASSWORD. Define CRM_DB_PASS.", file=sys.stderr)
        sys.exit(1)

def psql_atc(sql: str) -> str:
    """
    Ejecuta SQL y devuelve stdout. -A -t (sin headers, sin alineación).
    FIXED: Usa -Atc en lugar de -c con json.dumps() para evitar problemas de escaping.
    """
    # Escapar comillas dobles para el shell (ya que usamos comillas dobles externas)
    sql_escaped = sql.replace('"', '\\"')
    
    remote = (
        f"docker exec -i {CRM_DB_CONTAINER} "
        f"env PGPASSWORD='{CRM_DB_PASS}' "
        f"psql -U '{CRM_DB_USER}' -d '{CRM_DB_NAME}' -Atc \"{sql_escaped}\""
    )
    cp = sh(ssh_cmd(remote))
    lines = (cp.stdout or '').splitlines()
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if s.startswith(('INSERT', 'UPDATE', 'DELETE', 'SELECT', 'CREATE', 'DROP', 'NOTICE')):
            continue
        return s
    return ''

def delay_short():
    time.sleep(DELAY)

def sql_quote(s: str | None) -> str:
    if s is None:
        return "NULL"
    # escapado básico seguro para literales
    return "'" + s.replace("'", "''") + "'"

def get_or_create_contact(contact: dict) -> str:
    """
    Idempotencia por email (no hay UNIQUE(email) en schema v2).
    Si existe email, devuelve id.
    Si no, inserta y devuelve id.
    """
    email = contact.get("email")
    if email:
        existing = psql_atc(
            f"SELECT id FROM contactos WHERE email = {sql_quote(email)} LIMIT 1;"
        )
        if existing:
            return existing

    # Inserta
    cols = [
        "nombre","email","telefono","company_name","tipo_empresa",
        "created_at","updated_at","gdpr_consent","gdpr_consent_date",
        "origen","estado"
    ]
    vals = [
        sql_quote(contact.get("nombre")),
        sql_quote(contact.get("email")),
        sql_quote(contact.get("telefono")),
        sql_quote(contact.get("company_name")),
        sql_quote(contact.get("tipo_empresa")),
        sql_quote(contact.get("created_at")),
        sql_quote(contact.get("created_at")),  # updated_at = created_at
        "true" if contact.get("gdpr_consent") else "false",
        sql_quote(contact.get("created_at")),
        sql_quote("FORMULARIO_WEB"),
        sql_quote("ACTIVO"),
    ]
    sql = (
        f"INSERT INTO contactos ({', '.join(cols)}) "
        f"VALUES ({', '.join(vals)}) "
        f"RETURNING id;"
    )
    return psql_atc(sql)

def insert_param_utm(row: dict) -> str | None:
    """
    Idempotencia: evita duplicar por contacto_id + (utm_source, utm_medium, utm_campaign, gclid, msclkid, li_fat_id).
    Nota: UNIQUE real es (contacto_id,gclid,msclkid,li_fat_id) pero NULLs permiten duplicados,
    así que usamos IS NOT DISTINCT FROM.
    """
    contacto_id = row["contacto_id"]
    utm_source = row.get("utm_source")
    utm_medium = row.get("utm_medium")
    utm_campaign = row.get("utm_campaign")
    gclid = row.get("gclid")
    msclkid = row.get("msclkid")
    li_fat_id = row.get("li_fat_id")

    exists_sql = f"""
    SELECT id
    FROM parametros_utm
    WHERE contacto_id = {sql_quote(contacto_id)}
      AND utm_source   IS NOT DISTINCT FROM {sql_quote(utm_source)}
      AND utm_medium   IS NOT DISTINCT FROM {sql_quote(utm_medium)}
      AND utm_campaign IS NOT DISTINCT FROM {sql_quote(utm_campaign)}
      AND gclid        IS NOT DISTINCT FROM {sql_quote(gclid)}
      AND msclkid      IS NOT DISTINCT FROM {sql_quote(msclkid)}
      AND li_fat_id    IS NOT DISTINCT FROM {sql_quote(li_fat_id)}
    LIMIT 1;
    """
    existing = psql_atc(exists_sql)
    if existing:
        return existing

    cols = [
        "contacto_id",
        "first_visit_at","created_at",
        "utm_source","utm_medium","utm_campaign","utm_content","utm_term",
        "adgroup","device","placement","keyword","creative",
        "gclid","msclkid","li_fat_id","fbclid",
        "ads_platform","landing_url","referrer_url",
    ]
    vals = [
        sql_quote(contacto_id),
        sql_quote(row.get("first_visit_at")),
        sql_quote(row.get("created_at")),
        sql_quote(row.get("utm_source")),
        sql_quote(row.get("utm_medium")),
        sql_quote(row.get("utm_campaign")),
        sql_quote(row.get("utm_content")),
        sql_quote(row.get("utm_term")),
        sql_quote(row.get("adgroup")),
        sql_quote(row.get("device")),
        sql_quote(row.get("placement")),
        sql_quote(row.get("keyword")),
        sql_quote(row.get("creative")),
        sql_quote(row.get("gclid")),
        sql_quote(row.get("msclkid")),
        sql_quote(row.get("li_fat_id")),
        sql_quote(row.get("fbclid")),
        sql_quote(row.get("ads_platform")),
        sql_quote(row.get("landing_url")),
        sql_quote(row.get("referrer_url")),
    ]
    sql = (
        f"INSERT INTO parametros_utm ({', '.join(cols)}) "
        f"VALUES ({', '.join(vals)}) RETURNING id;"
    )
    return psql_atc(sql)

def insert_formulario(row: dict) -> str | None:
    """
    Idempotencia: evita duplicar por contacto_id + servicio_relacionado + mensaje (prefijo).
    """
    contacto_id = row["contacto_id"]
    servicio = row["servicio_relacionado"]
    mensaje = row["mensaje"]

    existing = psql_atc(f"""
    SELECT id FROM formulario_web
    WHERE contacto_id = {sql_quote(contacto_id)}
      AND servicio_relacionado = {sql_quote(servicio)}
      AND mensaje = {sql_quote(mensaje)}
    LIMIT 1;
    """)
    if existing:
        return existing

    cols = [
        "contacto_id",
        "servicio_relacionado",
        "como_nos_conociste",
        "tipo_solucion",
        "situacion_infraestructura",
        "problema_fiabilidad",
        "parte_infraestructura",
        "herramientas_conectar",
        "tipo_soporte",
        "mensaje",
        "submitted_at",
        "origen",
    ]
    vals = [
        sql_quote(contacto_id),
        sql_quote(row.get("servicio_relacionado")),
        sql_quote(row.get("como_nos_conociste")),
        sql_quote(row.get("tipo_solucion")),
        sql_quote(row.get("situacion_infraestructura")),
        sql_quote(row.get("problema_fiabilidad")),
        sql_quote(row.get("parte_infraestructura")),
        sql_quote(row.get("herramientas_conectar")),
        sql_quote(row.get("tipo_soporte")),
        sql_quote(row.get("mensaje")),
        sql_quote(row.get("submitted_at")),
        sql_quote(row.get("origen") or "Formulario web"),
    ]

    sql = (
        f"INSERT INTO formulario_web ({', '.join(cols)}) "
        f"VALUES ({', '.join(vals)}) RETURNING id;"
    )
    return psql_atc(sql)

# ─══════════════════════════════════════════════════════════════════════════════
# DATOS DE PRUEBA (CLON 1:1)
# ─══════════════════════════════════════════════════════════════════════════════

def generar_contactos():
    """Genera contactos de ejemplo para cada tipo de servicio (clon 1:1)."""
    now = datetime.now().isoformat()
    return [
        {"nombre":"María García","email":"maria.garcia@pyme-tech.es","telefono":"+34 600 111 222","company_name":"PYME Tech Solutions","tipo_empresa":"Pyme","created_at":now,"gdpr_consent":True},
        {"nombre":"Carlos Martínez","email":"carlos@agenciadigital.com","telefono":"+34 600 222 333","company_name":"Agencia Digital Creativa","tipo_empresa":"Agencia","created_at":now,"gdpr_consent":True},
        {"nombre":"Laura Sánchez","email":"laura@startup-ai.io","telefono":"+34 600 333 444","company_name":"Startup AI Solutions","tipo_empresa":"Startup","created_at":now,"gdpr_consent":True},
        {"nombre":"Javier López","email":"javier@comercio-online.es","telefono":"+34 600 444 555","company_name":"Comercio Online SL","tipo_empresa":"Pyme","created_at":now,"gdpr_consent":True},
        {"nombre":"Ana Torres","email":"ana.torres@fintech-startup.com","telefono":"+34 600 555 666","company_name":"FinTech Innovación","tipo_empresa":"Startup","created_at":now,"gdpr_consent":True},
        {"nombre":"Roberto Fernández","email":"roberto@consultoria-it.es","telefono":"+34 600 666 777","company_name":"Consultoría IT Pro","tipo_empresa":"Pyme","created_at":now,"gdpr_consent":True},
        {"nombre":"Elena Ruiz","email":"elena@emprendedora.com","telefono":"+34 600 777 888","company_name":None,"tipo_empresa":"Emprendedor","created_at":now,"gdpr_consent":True},
    ]

def generar_parametros_utm(contacto_ids):
    """Genera parámetros UTM de ejemplo para cada contacto (clon 1:1)."""

    utm_configs = [
        {
            "utm_source":"google","utm_medium":"cpc","utm_campaign":"desarrollo-web-madrid","utm_content":"ad-group-desarrollo-web",
            "utm_term":"desarrollo web profesional","adgroup":"Desarrollo Web - Madrid","device":"mobile","placement":None,
            "keyword":"desarrollo web profesional","creative":"rsa-desarrollo-web-01","gclid":"EAIaIQobChMI1234567890",
            "msclkid":None,"li_fat_id":None,"ads_platform":"GOOGLE",
            "landing_url":"https://mailerblend.com/desarrollo-web","referrer_url":"https://www.google.com/search",
        },
        {
            "utm_source":"bing","utm_medium":"cpc","utm_campaign":"cloud-devops-2024","utm_content":"cloud-migration",
            "utm_term":"cloud devops","adgroup":"Cloud & DevOps","device":"desktop","placement":None,
            "keyword":"cloud devops","creative":"text-ad-cloud-01","gclid":None,"msclkid":"a1b2c3d4e5f6g7h8i9j0",
            "li_fat_id":None,"ads_platform":"BING",
            "landing_url":"https://mailerblend.com/cloud-devops","referrer_url":"https://www.bing.com/search",
        },
        {
            "utm_source":"linkedin","utm_medium":"cpc","utm_campaign":"sre-observabilidad-profesionales","utm_content":"sre-engineers",
            "utm_term":None,"adgroup":"SRE Professionals","device":"desktop","placement":"linkedin-feed",
            "keyword":None,"creative":"single-image-sre-01","gclid":None,"msclkid":None,"li_fat_id":"xyz123abc456def789",
            "ads_platform":"LINKEDIN",
            "landing_url":"https://mailerblend.com/sre-observabilidad","referrer_url":"https://www.linkedin.com",
        },
        {
            "utm_source":"google","utm_medium":"display","utm_campaign":"ecommerce-solutions","utm_content":"banner-ecommerce",
            "utm_term":None,"adgroup":"E-commerce Solutions","device":"tablet","placement":"techcrunch.com",
            "keyword":None,"creative":"banner-responsive-300x250","gclid":"EAIaIQobChMI9876543210",
            "msclkid":None,"li_fat_id":None,"ads_platform":"GOOGLE",
            "landing_url":"https://mailerblend.com/ecommerce","referrer_url":"https://techcrunch.com",
        },
        {
            "utm_source":"google","utm_medium":"cpc","utm_campaign":"infraestructura-gestionada","utm_content":"infraestructura-aws",
            "utm_term":"infraestructura gestionada aws","adgroup":"Infraestructura - AWS","device":"mobile","placement":None,
            "keyword":"infraestructura gestionada aws","creative":"rsa-infra-01","gclid":"EAIaIQobChMI1111111111",
            "msclkid":None,"li_fat_id":None,"ads_platform":"GOOGLE",
            "landing_url":"https://mailerblend.com/infraestructura-gestionada","referrer_url":"https://www.google.com/search",
        },
        {
            "utm_source":"bing","utm_medium":"cpc","utm_campaign":"integraciones-automatizacion","utm_content":"zapier-make",
            "utm_term":"automatización empresarial","adgroup":"Automatización","device":"desktop","placement":None,
            "keyword":"automatización empresarial","creative":"text-ad-automation-01","gclid":None,"msclkid":"z9y8x7w6v5u4t3s2r1",
            "li_fat_id":None,"ads_platform":"BING",
            "landing_url":"https://mailerblend.com/integraciones","referrer_url":"https://www.bing.com/search",
        },
        {
            "utm_source":"google","utm_medium":"organic","utm_campaign":None,"utm_content":None,"utm_term":None,
            "adgroup":None,"device":"mobile","placement":None,"keyword":None,"creative":None,
            "gclid":None,"msclkid":None,"li_fat_id":None,"ads_platform":None,
            "landing_url":"https://mailerblend.com/outsourcing-it","referrer_url":"https://www.google.com/search",
        },
    ]

    parametros = []
    for i, contacto_id in enumerate(contacto_ids):
        cfg = utm_configs[i % len(utm_configs)]
        param = {
            "contacto_id": contacto_id,
            "first_visit_at": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "created_at": datetime.now().isoformat(),
            **cfg
        }
        parametros.append(param)
    return parametros

def generar_formularios_web(contacto_ids):
    """Genera formularios web con campos dinámicos según el servicio (clon 1:1)."""
    now = datetime.now().isoformat()
    return [
        {
            "contacto_id": contacto_ids[0],
            "servicio_relacionado": "Desarrollo web y software a medida",
            "como_nos_conociste": "Google / Buscador",
            "tipo_solucion": "Web profesional / landing",
            "mensaje": "Necesitamos una web profesional para nuestra empresa de tecnología. Queremos algo moderno, rápido y que refleje nuestra identidad de marca. Buscamos un partner técnico para largo plazo.",
            "submitted_at": now,
            "origen": "Formulario web",
        },
        {
            "contacto_id": contacto_ids[1],
            "servicio_relacionado": "Cloud & DevOps",
            "como_nos_conociste": "LinkedIn",
            "situacion_infraestructura": "AWS",
            "mensaje": "Tenemos nuestra infraestructura en AWS pero está mal configurada. Los costes son muy altos y no tenemos monitorización adecuada. Necesitamos ayuda para optimizar y automatizar despliegues.",
            "submitted_at": now,
            "origen": "Formulario web",
        },
        {
            "contacto_id": contacto_ids[2],
            "servicio_relacionado": "SRE / Observabilidad",
            "como_nos_conociste": "Recomendación",
            "problema_fiabilidad": "Caídas frecuentes sin saber por qué",
            "mensaje": "Nuestra aplicación se cae frecuentemente y no sabemos por qué. Cuando ocurre un incidente, tardamos horas en identificar el problema. Necesitamos implementar observabilidad y definir SLOs.",
            "submitted_at": now,
            "origen": "Formulario web",
        },
        {
            "contacto_id": contacto_ids[3],
            "servicio_relacionado": "Desarrollo web y software a medida",
            "como_nos_conociste": "Google / Buscador",
            "tipo_solucion": "E-commerce / tienda online",
            "mensaje": "Queremos lanzar una tienda online para vender nuestros productos. Necesitamos integración con pasarela de pago, gestión de inventario y envíos. El proyecto es urgente, queremos lanzar en 2 meses.",
            "submitted_at": now,
            "origen": "Formulario web",
        },
        {
            "contacto_id": contacto_ids[4],
            "servicio_relacionado": "Infraestructura gestionada",
            "como_nos_conociste": "Redes sociales",
            "parte_infraestructura": "Todo lo anterior",
            "mensaje": "Somos una startup sin equipo técnico interno. Necesitamos que alguien se encargue de todo: hosting, dominios, SSL, backups, seguridad... Todo lo relacionado con infraestructura.",
            "submitted_at": now,
            "origen": "Formulario web",
        },
        {
            "contacto_id": contacto_ids[5],
            "servicio_relacionado": "Integraciones / Automatización",
            "como_nos_conociste": "Cliente existente",
            "herramientas_conectar": "Necesitamos conectar Salesforce con HubSpot, sincronizar datos de clientes, automatizar envío de emails según comportamiento, e integrar con nuestro ERP SAP. También queremos automatizar la generación de informes.",
            "mensaje": "Tenemos muchas herramientas que no hablan entre sí. Perdemos mucho tiempo copiando datos manualmente. Queremos automatizar workflows y tener todo integrado.",
            "submitted_at": now,
            "origen": "Formulario web",
        },
        {
            "contacto_id": contacto_ids[6],
            "servicio_relacionado": "Outsourcing IT / CAU",
            "como_nos_conociste": "Evento / Conferencia",
            "tipo_soporte": "Externalización completa IT",
            "mensaje": "Somos una empresa de 50 empleados y no tenemos departamento IT. Necesitamos externalizar todo: soporte a usuarios, mantenimiento de equipos, gestión de licencias, ciberseguridad, etc.",
            "submitted_at": now,
            "origen": "Formulario web",
        },
    ]

# ─══════════════════════════════════════════════════════════════════════════════
# MAIN
# ─══════════════════════════════════════════════════════════════════════════════
def main():
    autodetect_env()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  📊 Generando datos de prueba para el CRM (Postgres)")
    print("  🎯 Un ejemplo por cada tipo de servicio")
    print(f"  🧩 Target: {CRM_DB_HOST}:{CRM_DB_CONTAINER} db={CRM_DB_NAME} user={CRM_DB_USER}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    contacto_ids: list[str] = []

    # ─── INSERTAR CONTACTOS ────────────────────────────────────────────────────
    print("👤 Insertando Contactos...\n")
    contactos = generar_contactos()
    for i, c in enumerate(contactos, 1):
        label = c["company_name"] or "Emprendedor"
        print(f"  {i}. {c['nombre']} ({label})...", end=" ")
        cid = get_or_create_contact(c)
        contacto_ids.append(cid)
        print(f"✅ ID: {cid}")
        delay_short()

    print()

    # ─── INSERTAR PARÁMETROS UTM ───────────────────────────────────────────────
    print("🔗 Insertando Parámetros UTM...\n")
    parametros = generar_parametros_utm(contacto_ids)
    utm_ids: list[str] = []
    for i, p in enumerate(parametros, 1):
        platform = p.get("ads_platform") or "Orgánico"
        medium = p.get("utm_medium") or "N/A"
        print(f"  {i}. {platform} - {medium}...", end=" ")
        pid = insert_param_utm(p)
        if pid:
            utm_ids.append(pid)
            print(f"✅ ID: {pid}")
        else:
            print("❌ Error")
        delay_short()

    print()

    # ─── INSERTAR FORMULARIOS WEB ──────────────────────────────────────────────
    print("📝 Insertando Formularios Web (campos dinámicos)...\n")
    formularios = generar_formularios_web(contacto_ids)
    form_ids: list[str] = []

    servicios_emoji = {
        "Desarrollo web y software a medida": "💻",
        "Cloud & DevOps": "☁️",
        "SRE / Observabilidad": "📊",
        "Infraestructura gestionada": "🏗️",
        "Integraciones / Automatización": "🔄",
        "Outsourcing IT / CAU": "🛠️",
    }

    for i, f in enumerate(formularios, 1):
        servicio = f["servicio_relacionado"]
        emoji = servicios_emoji.get(servicio, "📋")
        print(f"  {i}. {emoji} {servicio}")

        if f.get("tipo_solucion"):
            print(f"     └─ Tipo de solución: {f['tipo_solucion']}")
        if f.get("situacion_infraestructura"):
            print(f"     └─ Infraestructura actual: {f['situacion_infraestructura']}")
        if f.get("problema_fiabilidad"):
            print(f"     └─ Problema: {f['problema_fiabilidad']}")
        if f.get("parte_infraestructura"):
            print(f"     └─ Gestionar: {f['parte_infraestructura']}")
        if f.get("herramientas_conectar"):
            print(f"     └─ Herramientas: {f['herramientas_conectar'][:50]}...")
        if f.get("tipo_soporte"):
            print(f"     └─ Soporte: {f['tipo_soporte']}")

        print(f"     └─ Mensaje: {f['mensaje'][:60]}...")

        fid = insert_formulario(f)
        if fid:
            form_ids.append(fid)
            print(f"     ✅ ID: {fid}\n")
        else:
            print("     ❌ Error\n")
        delay_short()

    # ─── RESUMEN ───────────────────────────────────────────────────────────────
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ✅ Datos de prueba insertados correctamente")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    print("  📊 Resumen:")
    print(f"    • {len(contacto_ids)} Contactos")
    print(f"    • {len(utm_ids)} Parámetros UTM")
    print(f"    • {len(form_ids)} Formularios Web")
    print()
    print("  💡 Ahora puedes ver en tu CRM:")
    print("    • Cómo cada contacto tiene su tracking UTM")
    print("    • Cómo los formularios muestran campos dinámicos diferentes")
    print("    • Cómo se relacionan Contactos → Parámetros UTM")
    print("    • Cómo se relacionan Contactos → Formulario Web")
    print()
    print("  🎯 Servicios probados:")
    print("    1️⃣  Desarrollo web - Landing page")
    print("    2️⃣  Cloud & DevOps - AWS")
    print("    3️⃣  SRE - Caídas frecuentes")
    print("    4️⃣  Desarrollo web - E-commerce")
    print("    5️⃣  Infraestructura gestionada - Todo")
    print("    6️⃣  Integraciones - Salesforce + HubSpot + SAP")
    print("    7️⃣  Outsourcing IT - Externalización completa")
    print()

if __name__ == "__main__":
    main()