#!/usr/bin/env python3
"""Read-only recovery evidence; no model load or inference."""
import json,subprocess,shlex,urllib.request,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=Path.home()/'.local/share/mailerblend-recovery/voicebox-d070';OUT.mkdir(mode=0o700,exist_ok=True)
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
code="""import subprocess,json,os,time,hashlib,datetime
from pathlib import Path
cg=Path('/sys/fs/cgroup/lxc/627');c=json.loads(subprocess.check_output(['pct','exec','627','--','docker','inspect','voicebox']))[0];init=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();proc=Path('/proc')/init/'root/proc'/str(c['State']['Pid'])
def sample():
 st=(proc/'stat').read_text().split(') ',1)[1].split();return {'cpu_ticks':int(st[11])+int(st[12]),'memory':{x.split(':')[0]:x.split(':',1)[1].strip() for x in (proc/'status').read_text().splitlines() if x.startswith(('VmRSS:','VmHWM:','VmSwap:'))},'cgroup':{n:(cg/n).read_text() for n in ['memory.current','memory.swap.current','memory.events','cpu.stat']}}
windows=[]
for _ in range(3):
 a=sample();start=time.monotonic();time.sleep(5);b=sample();elapsed=time.monotonic()-start;b['elapsed_seconds']=elapsed;b['process_cpu_cores']=(b['cpu_ticks']-a['cpu_ticks'])/os.sysconf('SC_CLK_TCK')/elapsed;parse=lambda s:dict(x.split() for x in s.splitlines());b['cgroup_cpu_cores']=(int(parse(b['cgroup']['cpu.stat'])['usage_usec'])-int(parse(a['cgroup']['cpu.stat'])['usage_usec']))/1e6/elapsed;windows.append(b)
ref='/srv/voicebox/data/profiles/1fd00418-2a79-4178-883f-af6c3f5e07ee/8840f5e1-990b-463e-b94e-e72beef61917.wav'
check=\"from pathlib import Path;import hashlib,json;print(json.dumps({'reference':hashlib.sha256(Path(\"+repr(ref)+\").read_bytes()).hexdigest(),'originals':sorted(hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/srv/voicebox/private-originals').glob('*-original.wav'))}))\"
r={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'container':{'id':c['Id'],'image':c['Image'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'oom_killed':c['State']['OOMKilled']},'ct_uptime_seconds':float(subprocess.check_output(['pct','exec','627','--','cat','/proc/uptime'],text=True).split()[0]),'config_hashes':{p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/etc/pve/lxc').glob('*.conf')},'data_hashes':json.loads(subprocess.check_output(['pct','exec','627','--','python3','-c',check])),'windows':windows};print(json.dumps(r))
"""
r=json.loads(subprocess.check_output(ssh+['python3 -c '+shlex.quote(code)],timeout=40));before=json.loads((OUT.parent/'voicebox-d069/audit.json').read_text());configs=before['configs'];assert r['config_hashes']==configs,'PVE configuration changed since D069'
assert r['container']['id']=='68ecf2b01961696f7db2f452a7450ae0a74abe27fd0658de8a4e170df03da8b4' and r['container']['image']==json.loads((ROOT/'services/infra-voicebox/image-lock.json').read_text())['image_id'];assert not r['container']['oom_killed'];assert r['ct_uptime_seconds']>26062.98
assert max(x['process_cpu_cores'] for x in r['windows'])<.15,'Persistent busy inference'
assert all(int(v)==0 for k,v in (x.split() for x in r['windows'][-1]['cgroup']['memory.events'].splitlines()) if k in ['oom','oom_kill','oom_group_kill'])
owner=json.loads((OUT.parent/'voicebox-d069/recording-check.json').read_text());assert r['data_hashes']['reference']==owner['reference_sha256'] and owner['original_sha256'] in r['data_hashes']['originals']
def api(path):
 with urllib.request.urlopen('http://192.168.1.127:17493'+path,timeout=10) as response:return json.load(response)
profiles=api('/profiles');assert len(profiles)==1 and profiles[0]['id']=='1fd00418-2a79-4178-883f-af6c3f5e07ee';assert len(api('/profiles/'+profiles[0]['id']+'/samples'))==1
job=api('/history/d7ce3d31-fa43-4cd8-bd44-0b990ac53da2');assert job['status']=='failed' and job['error']=='Generation cancelled';assert api('/health')['status']=='healthy'
h=api('/history?limit=100');rows=h if isinstance(h,list) else h.get('items',h.get('generations',[]));assert not any(x['status'] in ['generating','loading_model','queued','pending'] for x in rows)
r.update({'result':'PASS','cancelled_generation':job['id'],'generation_status':job['status'],'generation_error':job['error'],'active_generations':0,'ct_restart':False,'profiles':1,'references':1,'reference_and_original_bytes_preserved':True,'other_pve_configs_unchanged':26,'pve_resources_changed':False})
(OUT/'audit.json').write_text(json.dumps(r,indent=2));(OUT/'audit.json').chmod(0o600)
public={k:v for k,v in r.items() if k not in ['config_hashes','data_hashes']};(ROOT/'docs/roadmap/evidence/2026-11-11-d070-recovery.json').write_text(json.dumps(public,indent=2)+'\n');print(json.dumps(public,indent=2))
