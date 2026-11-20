"""Prepare the dedicated auth schema and launch GoTrue on CT618."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
PSQL = ["docker", "exec", "-i", "supabase-db", "psql", "-U", "postgres", "-d", "postgres",
        "--set", "ON_ERROR_STOP=1", "-At"]


def db(sql):
    return subprocess.check_output(PSQL, input=sql, text=True).strip()


def main():
    settings = json.load(sys.stdin)
    password = settings["CRM_AUTH_DB_PASSWORD"]
    jwt_key = settings["CRM_AUTH_JWT_SECRET"]
    if not re.fullmatch(r"[0-9a-f]{48}", password) or not re.fullmatch(r"[0-9a-f]{64}", jwt_key):
        raise SystemExit("Unexpected CRM secret format")
    state = db("""
        SELECT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname='auth'),
               EXISTS (SELECT 1 FROM pg_roles WHERE rolname='crm_auth');
    """)
    if state == "f|f":
        bootstrap = (HERE / "initialize.sql").read_text()
        db("\\set auth_password " + password + "\n" + bootstrap)
    elif state != "t|t" or not (HERE / ".env").exists():
        raise SystemExit("Existing auth schema or role requires reconciliation")

    if db("""
        SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
        WHERE n.nspname='public' AND c.relkind IN ('r','p','v','m')
          AND (has_table_privilege('crm_auth', c.oid, 'SELECT') OR
               has_table_privilege('crm_auth', c.oid, 'INSERT') OR
               has_table_privilege('crm_auth', c.oid, 'UPDATE') OR
               has_table_privilege('crm_auth', c.oid, 'DELETE'));
    """) != "0":
        raise SystemExit("Auth role inherits business table privileges")
    private_config = f"CRM_AUTH_DB_PASSWORD={password}\nCRM_AUTH_JWT_SECRET={jwt_key}\n"
    env_file = HERE / ".env"
    if not env_file.exists():
        fd = os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as handle:
            handle.write(private_config)
    elif env_file.read_text() != private_config:
        raise SystemExit("Auth environment differs from the supplied credentials")
    subprocess.run(["docker", "compose", "-p", "crm-auth", "up", "-d"], cwd=HERE, check=True)
    for _ in range(20):
        try:
            with urllib.request.urlopen("http://192.168.1.118:18090/health", timeout=2) as res:
                if res.status == 200:
                    print("GoTrue healthy with an isolated auth schema and dedicated role.")
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(2)
    raise SystemExit("GoTrue readiness timed out")


if __name__ == "__main__":
    main()
