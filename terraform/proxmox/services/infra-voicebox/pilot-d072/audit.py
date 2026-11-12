"""PVE read-only post-pilot evidence, never prints private text or recording."""
from pathlib import Path
import json,hashlib,subprocess,time,datetime
CG=Path('/sys/fs/cgroup/lxc/627')
def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=15)
def usage():return int(dict(x.split() for x in (CG/'cpu.stat').read_text().splitlines())['usage_usec'])
a=usage();t=time.monotonic();time.sleep(5);cores=(usage()-a)/1e6/(time.monotonic()-t)
prod=json.loads(ct('docker','inspect','voicebox'))[0];pilot=json.loads(ct('docker','inspect','qwen-d072-short-int8'))[0]
check="""from pathlib import Path
import hashlib,json
p=Path('/srv/voicebox/data/profiles/1fd00418-2a79-4178-883f-af6c3f5e07ee/8840f5e1-990b-463e-b94e-e72beef61917.wav')
print(json.dumps({'reference':hashlib.sha256(p.read_bytes()).hexdigest(),'originals':sorted(hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/srv/voicebox/private-originals').glob('*-original.wav')),'piper_bytes':Path('/srv/voicebox/data/models/piper/es_ES-sharvard-medium.onnx').stat().st_size}))"""
r={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'production':{'id':prod['Id'],'image':prod['Image'],'started_at':prod['State']['StartedAt'],'health':prod['State'].get('Health',{}).get('Status'),'restarts':prod['RestartCount']},'pilot':{'running':pilot['State']['Running'],'pid':pilot['State']['Pid'],'oom_killed':pilot['State']['OOMKilled'],'exit_code':pilot['State']['ExitCode']},'ct_cpu_cores_5s':cores,'ct_memory':int((CG/'memory.current').read_text()),'ct_swap':int((CG/'memory.swap.current').read_text()),'ct_events':dict(x.split() for x in (CG/'memory.events').read_text().splitlines()),'host_pressure':Path('/proc/pressure/memory').read_text(),'host_memory_available':int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024,'config_hashes':{p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/etc/pve/lxc').glob('*.conf')},'data':json.loads(ct('python3','-c',check)),'resources':[x for x in ct('cat','/etc/hostname').splitlines()]}
print(json.dumps(r))
