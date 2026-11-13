#!/usr/bin/env python3
"""PVE: reaplicación sin cambios de630/631; verificaPID,contenedores,configs yjobs."""
import pathlib,subprocess,json,hashlib,datetime
root=pathlib.Path('/root/ia-local')
def run(*a):return subprocess.run(a,text=True,capture_output=True,check=True).stdout.strip()
def snapshot():
 return {'protected':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*pathlib.Path('/etc/pve/lxc').glob('*.conf'),pathlib.Path('/etc/pve/storage.cfg'),pathlib.Path('/etc/network/interfaces')]},'llama':run('pct','exec','630','--','systemctl','show','llama-server','-p','MainPID','-p','ExecMainStartTimestampMonotonic','-p','NRestarts'),'containers':{name:run('pct','exec','631','--','docker','inspect','--format','{{.Id}}|{{.Image}}|{{.State.StartedAt}}|{{.RestartCount}}|{{.HostConfig.Runtime}}',name) for name in ['ia-chat-open-webui-1','ia-chat-searxng-1','cadvisor']},'artifacts':{'llama':run('pct','exec','630','--','sha256sum','/etc/llama/models.ini','/etc/systemd/system/llama-server.service'),'webui':run('pct','exec','631','--','sha256sum','/opt/ia-chat/docker-compose.yml','/opt/ia-chat/custom.css')}}
before=snapshot();outputs={}
outputs['provision']='Terraform authoritative; checked separately with scoped no-op plan'
outputs['llama']=run('python3',str(root/'install-llama.py'))
assert json.loads(outputs['llama'].splitlines()[-1])=={'changed_template':False,'changed_ini':False,'changed_unit':False,'service_restarted':False,'active':'active'}
run('pct','exec','631','--','sh','-c','cd /opt/ia-chat && docker compose config --quiet')
outputs['compose']=run('pct','exec','631','--','sh','-c','cd /opt/ia-chat && docker compose up -d')
outputs['jobs']=json.loads(run('python3',str(root/'create-backups.py')));assert outputs['jobs']['created']==[]
after=snapshot();assert before==after,'Cambio inesperado en reaplicación'
original=json.loads((root/'protected-before.json').read_text());assert all(after['protected'].get(p)==sha for p,sha in original.items())
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pass':True,'no_recreation_reload_restart':True,'original_protected_configs_unchanged':True,'before':before,'after':after,'outputs':outputs};(root/'idempotence.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pass':True,'no_recreation_reload_restart':True,'original_protected_configs_unchanged':True,'protected_configs':len(original)}))
