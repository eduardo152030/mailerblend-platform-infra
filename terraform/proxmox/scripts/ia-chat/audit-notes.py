#!/usr/bin/env python3
"""Auditoría filtrada de630/631 y comparación con el inventario; solo lectura remota."""
import importlib.util,json,subprocess,shlex,datetime,os,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sp=importlib.util.spec_from_file_location('stage',ROOT/'scripts/phase6-stage-a.py');t=importlib.util.module_from_spec(sp);sp.loader.exec_module(t)
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
def pve(code):return subprocess.check_output(ssh+[shlex.join(['python3','-c',code])])
active=json.loads(pve("import subprocess,json;d=json.loads(subprocess.check_output(['pvesh','get','/nodes/pve/lxc','--output-format','json']));print(json.dumps([{'vmid':r['vmid'],'name':r.get('name'),'status':r['status']} for r in d]))"))
declared={yaml.safe_load(p.read_text())['service']['vmid']:p.stem for p in (ROOT/'inventory/services').glob('*.yml')}
print('Activos fuera del inventario:',[r for r in active if r['status']=='running' and r['vmid'] not in declared]);print('CT nuevos de esta tarea:',[r|{'service':declared.get(r['vmid'])} for r in active if r['vmid'] in [630,631]])
private=Path.home()/'.local/share/mailerblend-recovery/ia-chat/notes-20261113';private.mkdir(parents=True,exist_ok=True,mode=0o700)
result={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'identified':[r|{'service':declared.get(r['vmid'])} for r in active if r['vmid'] in [630,631]],'unmanaged_active':[r for r in active if r['status']=='running' and r['vmid'] not in declared],'cts':{}}
for ct in [630,631]:
 code=f"import subprocess,json;d=json.loads(subprocess.check_output(['pvesh','get','/nodes/pve/lxc/{ct}/config','--output-format','json']));print(json.dumps(d))"
 cfg=json.loads(pve(code));backup=private/(str(ct)+'-'+__import__('hashlib').sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()+'.json');backup.write_text(json.dumps(cfg));backup.chmod(0o600)
 keep=['hostname','cores','memory','swap','rootfs','mp0','net0','unprivileged','features','onboot','timezone','ostype','nameserver','searchdomain','tags']
 data={'config':{k:cfg[k] for k in keep if k in cfg}}
 data['runtime']=json.loads(t.py(ct,"import subprocess,json,pathlib; print(json.dumps({'os':dict(l.split('=',1) for l in pathlib.Path('/etc/os-release').read_text().splitlines() if '=' in l).get('PRETTY_NAME'),'ip':json.loads(subprocess.check_output(['ip','-j','-4','addr','show','dev','eth0'])),'mounts':subprocess.check_output(['findmnt','-J','-o','TARGET,SOURCE,FSTYPE,OPTIONS'],text=True),'listeners':subprocess.check_output(['ss','-ltn'],text=True),'services':{n:subprocess.run(['systemctl','is-active',n],capture_output=True,text=True).stdout.strip() for n in ['llama-server','node-exporter','lxc-cpu.timer','docker']}}))"))
 if ct==631:
  data['containers']=json.loads(t.py(ct,"import subprocess,json;ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();cs=json.loads(subprocess.check_output(['docker','inspect']+ids));print(json.dumps([{'name':c['Name'],'id':c['Id'],'image':c['Config']['Image'],'started':c['State']['StartedAt'],'status':c['State']['Status'],'health':c['State'].get('Health',{}).get('Status'),'has_healthcheck':bool(c['Config'].get('Healthcheck')),'ports':c['NetworkSettings']['Ports'],'mounts':[{'source':m['Source'],'destination':m['Destination'],'rw':m['RW']} for m in c['Mounts']],'restart_policy':c['HostConfig']['RestartPolicy']['Name']} for c in cs]))"))
 result['cts'][str(ct)]=data
result['jobs']=json.loads(pve("import subprocess,json;d=json.loads(subprocess.check_output(['pvesh','get','/cluster/backup','--output-format','json']));print(json.dumps([r for r in d if r.get('id') in ['ia-chat-webui-631','ia-chat-llm-630']]))"))
result['monitoring']={k:t.query(q) for k,q in {'targets':'up{service=~"infra-llm|infra-webui"}','probes':'probe_success{service=~"infra-llm|infra-webui"}','cpu':'lxc:cpu_usage:percent{ct_id=~"630|631"}','ram':'node_memory_MemTotal_bytes{service=~"infra-llm|infra-webui",job="node_exporter"}','alerts':'ALERTS{service=~"infra-llm|infra-webui",alertstate="firing"}'}.items()}
(ROOT/'docs/roadmap/evidence/ia-chat-2026-11-13/notes-live-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('Auditoría guardada; contenedores631:',[(r['name'],r['health'],r['has_healthcheck']) for r in result['cts']['631']['containers']])
