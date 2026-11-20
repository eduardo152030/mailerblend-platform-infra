"""Release CRM notification containers on CT618 using privately staged inputs."""
from argparse import ArgumentParser
from ipaddress import IPv4Address
import re
import json, os, pathlib, shutil, subprocess, tempfile
from urllib.parse import urlsplit, unquote
os.umask(0o077)
parser = ArgumentParser(description=__doc__)
parser.add_argument("--stage", type=pathlib.Path, required=True)
parser.add_argument("--image-tag", required=True)
parser.add_argument("--relay-ip", type=IPv4Address, required=True)
options = parser.parse_args()
if pathlib.Path("/etc/hostname").read_text().strip() != "infra-composable-crm":
    parser.error("Expected the CRM container")
if not re.fullmatch(r"[0-9a-f]{8,40}", options.image_tag):
    parser.error("Expected a reviewed Git SHA tag")
stage = options.stage.resolve()
if not stage.is_dir() or stage.stat().st_mode & 0o077:
    parser.error("Expected a private staging directory")
api=pathlib.Path('/opt/healthcheck-d051/crm-api/compose.private.json')
ui=pathlib.Path('/opt/crm-ui-release/.env')
auth=pathlib.Path('/opt/crm-auth/docker-compose.yml')
auth_env=auth.parent/'.env'
worker=stage/'compose/crm-notifications'
worker_env=worker/'.env'
ca=stage/'ca-bundle.crt'
backup=pathlib.Path(tempfile.mkdtemp(prefix='before-68.',dir='/opt'))
files={api:'crm-api.json',ui:'crm-ui.env',auth:'crm-auth.yml',auth_env:'crm-auth.env'}
for path,name in files.items():
    if path.exists(): shutil.copy2(path,backup/name)
print(f'Configuration backup {backup}',flush=True)
def run(args,**kwargs):
    subprocess.run(args,check=True,**kwargs)
def compose(file,*args,project=None):
    cmd=['docker','compose','--project-directory',str(file.parent),'-f',str(file)]
    if project: cmd.extend(['-p',project])
    run(cmd+list(args),stdout=subprocess.DEVNULL)
def env_append(path,keyvals):
    current=path.read_text().splitlines() if path.exists() else []
    lines=[line for line in current if line.split('=',1)[0] not in keyvals]
    for name,value in keyvals.items():
        if any(c in value for c in ("'","\n","\r")): raise ValueError('Unexpected env value syntax')
        lines.append(f"{name}='{value}'")
    path.write_text('\n'.join(lines)+'\n')
    path.chmod(0o600)
old_ui_image = subprocess.check_output(
    ['docker', 'inspect', '--format', '{{.Config.Image}}', 'crm-ui-release-crm-ui-1'],
    text=True,
).strip()
config=json.loads(api.read_text())
service=config['services']['crm-api']
dsn=service['environment']['CRM_DB_DSN']
assert isinstance(dsn,str) and dsn.startswith('postgres')
role=unquote(urlsplit(dsn).username or '')
assert role
quoted_role='"'+role.replace('"','""')+'"'
migration=(stage/'database-schemas/14_contact_notifications.sql').read_bytes()
sql=migration+f'\nGRANT USAGE ON SCHEMA crm_notifications TO {quoted_role};\nGRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA crm_notifications TO {quoted_role};\n'.encode()
run(['docker','exec','-i','supabase-db','psql','-X','-U','postgres','-d','postgres','-v','ON_ERROR_STOP=1'],input=sql,stdout=subprocess.DEVNULL)
print('PostgreSQL migration and CRM role grants applied',flush=True)
ca.write_bytes(pathlib.Path('/etc/ssl/certs/ca-certificates.crt').read_bytes()+b'\n'+(stage/'ca.crt').read_bytes())
ca.chmod(0o644)
common=dict(CRM_SMTP_HOST=str(options.relay_ip),CRM_SMTP_PORT='587',CRM_SMTP_FROM='team@nucleotecnologico.es',CRM_SMTP_CA_BUNDLE=str(ca))
try:
    service['image']=f'infra-composable-crm/crm-api:{options.image_tag}'
    api.write_text(json.dumps(config)+'\n')
    compose(api,'up','-d','--no-deps','--no-build','crm-api',project='d051-crm-api')
    env_append(ui,dict(CRM_UI_IMAGE=f'infra-composable-crm/crm-ui:{options.image_tag}'))
    compose(ui.parent/'docker-compose.yml','up','-d','--no-deps','--no-build','crm-ui')
    env_append(auth_env,dict(common,CRM_SMTP_USER='gotrue',CRM_SMTP_PASSWORD=(stage/'gotrue.password').read_text().strip()))
    shutil.copyfile(stage/'compose/crm-auth/docker-compose.yml',auth)
    compose(auth,'up','-d','--no-deps','--no-build','auth')
    env_append(worker_env,dict(common,CRM_DB_DSN=dsn,CRM_API_IMAGE=service['image'],CRM_SMTP_USER='crm',CRM_SMTP_PASSWORD=(stage/'crm.password').read_text().strip()))
    compose(worker/'docker-compose.yml','up','-d','--no-deps','--no-build')
except Exception:
    for path,name in files.items():
        previous=backup/name
        if previous.exists(): shutil.copy2(previous,path)
        elif path==ui: env_append(ui,dict(CRM_UI_IMAGE=old_ui_image))
    if worker_env.exists():
        compose(worker/'docker-compose.yml','stop')
    compose(api,'up','-d','--no-deps','--no-build','crm-api',project='d051-crm-api')
    compose(ui.parent/'docker-compose.yml','up','-d','--no-deps','--no-build','crm-ui')
    compose(auth,'up','-d','--no-deps','--no-build','auth')
    raise
print('CRMAPI, UI, GoTrue and notifications worker started',flush=True)
