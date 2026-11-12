#!/usr/bin/env python3
"""Finish owner-only cloning validation when real references exist; no substitute or third-party voice.
Prepare a scoped monitored model trial before invoking. Does not download models.
"""
import argparse,array,hashlib,io,json,time,urllib.request,wave,subprocess
from pathlib import Path
import yaml
p=argparse.ArgumentParser();p.add_argument('--owner-reference-confirmed',action='store_true',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
root=Path(__file__).resolve().parents[1];catalog=root/'services/infra-voicebox/voice-identities.yml';data=yaml.safe_load(catalog.read_text());entry=data['identities']['personal']
assert entry.get('profile_id') and entry['status']=='OWNER_REFERENCE_STORED_AWAITING_CONTROLLED_SYNTHESIS','Owner recordings and stored real profile required; no fictitious identity'
BASE='http://192.168.1.127:17493'
def api(path,value=None):
 with urllib.request.urlopen(urllib.request.Request(BASE+path,data=None if value is None else json.dumps(value).encode(),headers={'Content-Type':'application/json'}),timeout=30) as r:return json.load(r)
profile=api('/profiles/'+entry['profile_id']);assert profile['voice_type']=='cloned' and profile.get('default_engine') in (None,'qwen')
assert api('/profiles/'+entry['profile_id']+'/samples'),'No actual owner samples'
# This requires a reviewed CPU Base candidate and its one-time pinned download before invocation.
for m in api('/models/status')['models']:
 if m['loaded'] and m['model_name']!='qwen-tts-0.6B':api('/models/'+m['model_name']+'/unload',{})
assert not any(m['loaded'] and m['model_name']!='qwen-tts-0.6B' for m in api('/models/status')['models'])
ssh_pre=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
check="import json,subprocess;from pathlib import Path;p=Path('/sys/fs/cgroup/lxc/627');assert int((p/'memory.max').read_text())==7*2**30;c=json.loads(subprocess.check_output(['pct','exec','627','--','docker','inspect','voicebox']))[0];assert c['HostConfig']['Memory']>=4*2**30;print('PASS cloning resource preflight')"
subprocess.run(ssh_pre+['python3 -c '+__import__('shlex').quote(check)],check=True,timeout=15)
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
def memory():
 code="from pathlib import Path;import json;p=Path('/sys/fs/cgroup/lxc/627');d={n:(p/n).read_text() for n in ['memory.current','memory.swap.current','memory.events','cpu.stat']};d['host_pressure']=Path('/proc/pressure/memory').read_text();d['host_available']=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024;import subprocess,os;c=json.loads(subprocess.check_output(['pct','exec','627','--','docker','inspect','voicebox']))[0];init=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();st=(Path('/proc')/init/'root/proc'/str(c['State']['Pid'])/'stat').read_text().split(') ',1)[1].split();d['main_cpu_usec']=(int(st[11])+int(st[12]))*1000000//os.sysconf('SC_CLK_TCK');status=(Path('/proc')/init/'root/proc'/str(c['State']['Pid'])/'status').read_text();d['process_memory']={line.split(':')[0]:line.split(':',1)[1].strip() for line in status.splitlines() if line.startswith(('VmRSS:','VmHWM:','VmSwap:'))};print(json.dumps(d))"
 return json.loads(subprocess.check_output(ssh+['python3 -c '+__import__('shlex').quote(code)],timeout=15))
baseline=memory();assert baseline['host_available']>=int(1.5*2**30) and float(baseline['host_pressure'].splitlines()[1].split()[1].split('=')[1])<2,'Host safety preflight';initial_events=dict(x.split() for x in baseline['memory.events'].splitlines());initial_swap=int(baseline['memory.swap.current']);start=time.monotonic();last_cpu=baseline['main_cpu_usec'];last_progress=start
text='Ningún trader opera sin perder, ni siquiera los mejores. La diferencia no está en evitar las pérdidas, sino en cómo las gestionas.'
g=api('/generate',{'profile_id':profile['id'],'engine':'qwen','model_size':'0.6B','language':'es','text':text,'seed':42,'personality':False,'max_chunk_chars':200});ident=g['id']
private=Path.home()/'.local/share/mailerblend-recovery/voicebox-personal';private.mkdir(parents=True,mode=0o700,exist_ok=True);receipt=private/(ident+'-validation.json');record={'profile_id':profile['id'],'generation_id':ident,'status':'IN_PROGRESS','measurements':[]};receipt.write_text(json.dumps(record)+'\n');receipt.chmod(0o600)
while time.monotonic()-start<180:
 observed=memory();record['measurements'].append({'elapsed_seconds':time.monotonic()-start,**observed});receipt.write_text(json.dumps(record,indent=2)+'\n');events=dict(x.split() for x in observed['memory.events'].splitlines());cpu=observed['main_cpu_usec']
 if cpu-last_cpu>1000000:last_progress=time.monotonic();last_cpu=cpu
 if observed['host_available']<int(1.5*2**30) or float(observed['host_pressure'].splitlines()[1].split()[1].split('=')[1])>=2 or int(observed['memory.current'])>=int(6.5*2**30) or int(observed['memory.swap.current'])-initial_swap>64*2**20 or any(int(events[k])>int(initial_events[k]) for k in ['oom','oom_kill','oom_group_kill']) or time.monotonic()-last_progress>45:
  # Stop only this service to release the owner Base job; keep all samples/data.
  subprocess.run(ssh+['pct exec 627 -- docker restart voicebox'],check=True,timeout=90)
  for _ in range(40):
   try:
    if api('/health')['status']=='healthy':api('/models/load',{'model_name':'kokoro'});break
   except Exception:pass
   time.sleep(2)
  record.update({'status':'SAFETY_STOP','elapsed_seconds':time.monotonic()-start});receipt.write_text(json.dumps(record,indent=2)+'\n')
  raise RuntimeError('Owner Base safety stop; data preserved, reconcile recorded ID before another attempt')

 g=api('/history/'+ident)
 if g['status'] in ['completed','failed','cancelled']:break
 time.sleep(2)
if g['status']!='completed':
 subprocess.run(ssh+['pct exec 627 -- docker restart voicebox'],check=True,timeout=90)
 for _ in range(40):
  try:
   if api('/health')['status']=='healthy':api('/models/load',{'model_name':'kokoro'});break
  except Exception:pass
  time.sleep(2)
 record.update({'status':'FAILED_OR_TIMEOUT','generation_status':g['status'],'error':g.get('error'),'elapsed_seconds':time.monotonic()-start});receipt.write_text(json.dumps(record,indent=2)+'\n')
 raise RuntimeError('Owner Base trial did not complete; stable service restarted, reconcile recorded ID')
with urllib.request.urlopen(BASE+'/audio/'+ident,timeout=30) as r:audio=r.read()
with wave.open(io.BytesIO(audio)) as w:
 assert w.getnchannels()==1 and w.getsampwidth()==2;seconds=w.getnframes()/w.getframerate();samples=array.array('h',w.readframes(w.getnframes()));assert seconds>2 and max(abs(x) for x in samples)>100
with a.output.open('xb') as f:f.write(audio)
a.output.chmod(0o600);record.update({'status':'TECHNICAL_AUDIO_PASS_PENDING_OWNER_LISTENING','audio_seconds':seconds,'sha256':hashlib.sha256(audio).hexdigest()});receipt.write_text(json.dumps(record,indent=2)+'\n')
api('/models/load',{'model_name':'kokoro'})
entry['status']='TECHNICAL_SAMPLE_PASS';entry['auditory_acceptance']='PENDING_OWNER_LISTENING';entry['sample_generation_id']=ident;catalog.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True))
import shlex
sync_code="from pathlib import Path;import sys;p=Path('/srv/voicebox/data/voice-identities.yml');p.write_bytes(sys.stdin.buffer.read());p.chmod(0o600)"
subprocess.run(ssh+[shlex.join(['pct','exec','627','--','python3','-c',sync_code])],input=catalog.read_bytes(),check=True,timeout=30)
print(json.dumps(record))
