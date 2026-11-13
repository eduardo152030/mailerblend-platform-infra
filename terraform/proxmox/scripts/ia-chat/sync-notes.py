#!/usr/bin/env python3
"""Sincroniza únicamente Notes de630/631 desde las fuentes canónicas.
SSH estricto, backup privado, digest PVE y comprobación sin cambios de runtime.
Por defecto solo verifica; --apply permite cambiar exclusivamente description.
"""
import argparse,hashlib,json,os,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REMOTE=r'''
import sys,json,subprocess,hashlib,pathlib,datetime
payload=json.load(sys.stdin)
def run(*args):return subprocess.check_output(args,text=True).strip()
def config(ct):return json.loads(run('pvesh','get',f'/nodes/pve/lxc/{ct}/config','--output-format','json'))
def identities():
 return {'630':run('pct','exec','630','--','systemctl','show','llama-server','-p','MainPID','-p','NRestarts','-p','ExecMainStartTimestampMonotonic'),'631':run('pct','exec','631','--','docker','inspect','--format','{{.Id}}|{{.State.StartedAt}}|{{.RestartCount}}','ia-chat-open-webui-1','ia-chat-searxng-1','cadvisor')}
def protected():return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in pathlib.Path('/etc/pve/lxc').glob('*.conf') if p.stem not in ['630','631']}
old=protected();ids=identities();rows=[]
for item in payload['notes']:
 ct=item['ct'];assert ct in [630,631] and item['hostname']=={630:'infra-llm',631:'infra-webui'}[ct]
 before=config(ct);assert before['hostname']==item['hostname'];desired=item['description'];changed=before.get('description','')!=desired
 if changed and payload['apply']:
  p=pathlib.Path('/root/ia-local/notes-backups');p.mkdir(mode=0o700,exist_ok=True)
  data=json.dumps(before,sort_keys=True).encode();backup=p/(str(ct)+'-'+hashlib.sha256(data).hexdigest()+'.json')
  if not backup.exists():backup.write_bytes(data);backup.chmod(0o600)
  subprocess.run(['pvesh','set',f'/nodes/pve/lxc/{ct}/config','--description',desired,'--digest',before['digest']],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 after=config(ct);assert {k:v for k,v in before.items() if k not in ['description','digest']}=={k:v for k,v in after.items() if k not in ['description','digest']},'Unexpected non-Notes change'
 assert after.get('description','')==desired,'Runtime Notes differ; run with --apply if authorized'
 rows.append({'ct_id':ct,'hostname':after['hostname'],'notes_equal':True,'configuration_writes':int(changed and payload['apply']),'allowed_field':'description','sha256':hashlib.sha256(desired.encode()).hexdigest()})
assert protected()==old,'Other CT configurations changed';assert identities()==ids,'Service identity/restart changed'
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'result':'PASS','cts':rows,'other_ct_configs_unchanged':True,'runtime_identity_unchanged':True,'restarts':0,'redeploys':0,'terraform_apply':False}))
'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');p.add_argument('--ct',type=int,choices=[630,631],action='append',help='Limita las escrituras de Notes a los CT seleccionados');p.add_argument('--evidence-dir',type=Path,default=ROOT/'docs/roadmap/evidence/ia-chat-2026-11-13');a=p.parse_args()
 generated=json.loads((ROOT/'inventory/generated/lxc-notes.json').read_text());items=[]
 for ct,name in [(630,'infra-llm'),(631,'infra-webui')]:
  if a.ct and ct not in a.ct:continue
  d=generated[name];body='# '+d['title']+'\n\n'+'\n\n'.join(d['sections'])+'\n';assert body==(ROOT/'services'/name/'NOTES.md').read_text(),'Generated Notes stale'
  items.append({'ct':ct,'hostname':name,'description':body})
 args=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve',shlex.join(['python3','-c',REMOTE])]
 r=subprocess.run(args,input=json.dumps({'apply':a.apply,'notes':items}).encode(),capture_output=True,timeout=120)
 assert r.returncode==0,'Notes sync failed; no sensitive remote output printed'
 result=json.loads(r.stdout);dest=a.evidence_dir/('notes-sync-applied.json' if a.apply else 'notes-sync-verified.json');dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
