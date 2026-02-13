#!/usr/bin/env python3
"""
cleanup_seed_contacts.py - Limpia los contactos de prueba del CRM
=================================================================
Elimina los contactos seed y todas sus dependencias de forma segura.

Características:
- Sin dependencias externas (solo stdlib). Usa ssh + docker exec + psql.
- Elimina en cascada todas las relaciones.
- Muestra estadísticas de eliminación.

Requisitos:
- Acceso SSH a root@CRM_DB_HOST
- Contenedor Postgres (por defecto supabase-db)

# Con pipe (automatizado)
echo "y" | python3 services/infra-composable-crm/database-schemas/cleanup_seed_contacts.py

# O modo interactivo (te preguntará) Funciona. 
python3 services/infra-composable-crm/database-schemas/03.1_cleanup_data_crm_as_user_journey.py

"""

import os
import sys
import subprocess

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
CRM_DB_HOST = os.getenv("CRM_DB_HOST", "192.168.1.118")
CRM_DB_CONTAINER = os.getenv("CRM_DB_CONTAINER", "supabase-db")

# Si no los defines, los autodetectamos con docker inspect
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

def psql_exec(sql: str) -> str:
    """
    Ejecuta SQL y devuelve stdout completo.
    """
    # Escapar comillas dobles para el shell
    sql_escaped = sql.replace('"', '\\"')
    
    remote = (
        f"docker exec -i {CRM_DB_CONTAINER} "
        f"env PGPASSWORD='{CRM_DB_PASS}' "
        f"psql -U '{CRM_DB_USER}' -d '{CRM_DB_NAME}' -Atc \"{sql_escaped}\""
    )
    cp = sh(ssh_cmd(remote))
    return cp.stdout.strip()

# ─── SQL DE LIMPIEZA ──────────────────────────────────────────────────────────
CLEANUP_SQL = """
WITH seed_emails(email) AS (
  VALUES
    ('maria.garcia@pyme-tech.es'),
    ('carlos@agenciadigital.com'),
    ('laura@startup-ai.io'),
    ('javier@comercio-online.es'),
    ('ana.torres@fintech-startup.com'),
    ('roberto@consultoria-it.es'),
    ('elena@emprendedora.com')
),
seed_ids AS (
  SELECT c.id
  FROM contactos c
  JOIN seed_emails e ON e.email = c.email
),
del_utm AS (
  DELETE FROM parametros_utm
  WHERE contacto_id IN (SELECT id FROM seed_ids)
  RETURNING 1
),
del_form AS (
  DELETE FROM formulario_web
  WHERE contacto_id IN (SELECT id FROM seed_ids)
  RETURNING 1
),
del_fact AS (
  DELETE FROM facturas
  WHERE contacto_id IN (SELECT id FROM seed_ids)
  RETURNING 1
),
del_pres AS (
  DELETE FROM presupuestos
  WHERE contacto_id IN (SELECT id FROM seed_ids)
  RETURNING 1
),
del_pend AS (
  DELETE FROM pendientes
  WHERE contacto_id IN (SELECT id FROM seed_ids)
  RETURNING 1
),
del_hist AS (
  DELETE FROM historial
  WHERE contacto_id IN (SELECT id FROM seed_ids)
  RETURNING 1
),
del_opp AS (
  DELETE FROM oportunidades
  WHERE contacto_id IN (SELECT id FROM seed_ids)
  RETURNING 1
),
del_contacts AS (
  DELETE FROM contactos
  WHERE id IN (SELECT id FROM seed_ids)
  RETURNING email
)
SELECT
  (SELECT count(*) FROM del_contacts) AS deleted_contacts,
  (SELECT count(*) FROM del_utm) AS deleted_utm_rows,
  (SELECT count(*) FROM del_form) AS deleted_form_rows,
  (SELECT count(*) FROM del_fact) AS deleted_fact_rows,
  (SELECT count(*) FROM del_pres) AS deleted_pres_rows,
  (SELECT count(*) FROM del_pend) AS deleted_pend_rows,
  (SELECT count(*) FROM del_hist) AS deleted_hist_rows,
  (SELECT count(*) FROM del_opp) AS deleted_opp_rows;
"""

# ─══════════════════════════════════════════════════════════════════════════════
# MAIN
# ─══════════════════════════════════════════════════════════════════════════════
def main():
    autodetect_env()

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🧹 Limpiando contactos seed del CRM (Postgres)")
    print(f"  🧩 Target: {CRM_DB_HOST}:{CRM_DB_CONTAINER} db={CRM_DB_NAME} user={CRM_DB_USER}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    print("📧 Contactos a eliminar:")
    print("   • maria.garcia@pyme-tech.es")
    print("   • carlos@agenciadigital.com")
    print("   • laura@startup-ai.io")
    print("   • javier@comercio-online.es")
    print("   • ana.torres@fintech-startup.com")
    print("   • roberto@consultoria-it.es")
    print("   • elena@emprendedora.com")
    print()

    # Confirmación (soporta tanto modo interactivo como pipe)
    try:
        if sys.stdin.isatty():
            # Modo interactivo
            response = input("⚠️  ¿Estás seguro de eliminar estos contactos y todas sus dependencias? [y/N]: ")
        else:
            # Modo pipe/script
            print("⚠️  ¿Estás seguro de eliminar estos contactos y todas sus dependencias? [y/N]: ", end='', flush=True)
            response = sys.stdin.readline().strip()
            print(response)  # echo la respuesta para que se vea en el log
        
        if response.lower() not in ['y', 'yes', 's', 'si', 'sí']:
            print("\n❌ Operación cancelada.")
            sys.exit(0)
    except (EOFError, KeyboardInterrupt):
        print("\n\n❌ Operación cancelada.")
        sys.exit(0)

    print("\n🗑️  Ejecutando limpieza...\n")

    try:
        result = psql_exec(CLEANUP_SQL)
        
        # Parsear resultado (formato: deleted_contacts|deleted_utm|deleted_form|...)
        if result:
            parts = result.split('|')
            if len(parts) == 8:
                print("✅ Limpieza completada exitosamente\n")
                print("📊 Registros eliminados:")
                print(f"   • Contactos:           {parts[0]}")
                print(f"   • Parámetros UTM:      {parts[1]}")
                print(f"   • Formularios Web:     {parts[2]}")
                print(f"   • Facturas:            {parts[3]}")
                print(f"   • Presupuestos:        {parts[4]}")
                print(f"   • Pendientes:          {parts[5]}")
                print(f"   • Historial:           {parts[6]}")
                print(f"   • Oportunidades:       {parts[7]}")
                print()
                
                total_deps = sum(int(x) for x in parts[1:])
                print(f"   📌 Total dependencias: {total_deps}")
                print(f"   📌 Total general:      {int(parts[0]) + total_deps}")
            else:
                print("✅ Limpieza completada")
                print(f"Resultado: {result}")
        else:
            print("⚠️  No se encontraron contactos para eliminar.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al ejecutar la limpieza:")
        print(f"   {e}")
        if e.stderr:
            print(f"\n   Detalles: {e.stderr}")
        sys.exit(1)

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  ✅ Base de datos limpia")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

if __name__ == "__main__":
    main()