#!/usr/bin/env python3
"""Actualiza solo los defaults de rendimiento WebUI631 y reconcilia Compose sin pull.
No toca datos/secretos, SearXNG ni cAdvisor. Segunda aplicación conserva identidades.
"""
import subprocess,shlex,json,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
code=r'''
import pathlib,json,sys,subprocess,time,urllib.request
payload=json.load(sys.stdin)
def run(*a):return subprocess.check_output(a,text=True).strip()
def ids():return {n:run('docker','inspect','--format','{{.Id}}|{{.State.StartedAt}}|{{.RestartCount}}',n) for n in ['ia-chat-open-webui-1','ia-chat-searxng-1','cadvisor']}
base=pathlib.Path('/opt/ia-chat');old=(base/'docker-compose.yml').read_text();assert old==payload['baseline'],'Compose drift';before=ids();changed=old!=payload['compose']
# Compare normalized Compose through Docker itself; never print expanded environment.
if changed:
 backup=base/'.runtime/latency/compose-before.yml'
 if not backup.exists():backup.write_text(old);backup.chmod(0o600)
 (base/'docker-compose.yml').write_text(payload['compose'])
profile=base/'chat-performance.json'
if not profile.exists() or profile.read_text()!=payload['profile']:profile.write_text(payload['profile']);profile.chmod(0o600)
subprocess.run(['docker','compose','-f',str(base/'docker-compose.yml'),'config','--quiet'],check=True)
subprocess.run(['docker','compose','-f',str(base/'docker-compose.yml'),'up','-d','--no-deps','--pull','never','open-webui'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
for _ in range(120):
 try:
  with urllib.request.urlopen('http://127.0.0.1:3000/health',timeout=3) as r:assert r.status==200
  break
 except Exception:time.sleep(2)
else:raise AssertionError('WebUI not ready')
after=ids();assert before['ia-chat-searxng-1']==after['ia-chat-searxng-1'] and before['cadvisor']==after['cadvisor']
if not changed:assert before==after,'Unexpected restart on identical Compose'
print(json.dumps({'configuration_changed':changed,'webui_recreated':before['ia-chat-open-webui-1']!=after['ia-chat-open-webui-1'],'other_containers_unchanged':True,'health':200,'image_pull':False}))
'''
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve'];payload={'compose':(ROOT/'services/infra-webui/compose/docker-compose.yml').read_text(),'profile':(ROOT/'services/infra-webui/config/chat-performance.json').read_text()}
baseline=subprocess.check_output(ssh+[shlex.join(['pct','exec','631','--','cat','/opt/ia-chat/docker-compose.yml'])]).decode();previous=yaml.safe_load(baseline);desired=yaml.safe_load(payload['compose'])
allowed=['DEFAULT_MODEL_PARAMS','DEFAULT_MODEL_METADATA','ENABLE_TITLE_GENERATION','ENABLE_SEARCH_QUERY_GENERATION','ENABLE_TAGS_GENERATION','ENABLE_FOLLOW_UP_GENERATION','ENABLE_AUTOCOMPLETE_GENERATION','ENABLE_RETRIEVAL_QUERY_GENERATION']
for key in allowed:previous['services']['open-webui']['environment'][key]=desired['services']['open-webui']['environment'][key]
assert previous==desired,'Unrelated Compose changes: stop before overwriting'
payload['baseline']=baseline
p=subprocess.run(ssh+[shlex.join(['pct','exec','631','--','python3','-c',code])],input=json.dumps(payload).encode(),capture_output=True,timeout=360);assert p.returncode==0,'WebUI reconciliation failed; sensitive output withheld';d=json.loads(p.stdout);dest=ROOT/'docs/roadmap/evidence/ia-chat-latency-2026-11-13'/('webui-compose-applied.json' if d['configuration_changed'] else 'webui-compose-idempotent.json');dest.write_bytes(p.stdout);print(json.dumps(d))
