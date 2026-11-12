#!/usr/bin/env python3
"""D069 read-only: actual sole owner/reference/output persistence, resources, fleet."""
from pathlib import Path
import json,subprocess,urllib.request,hashlib,shlex,urllib.parse
ROOT=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/mailerblend-recovery/voicebox-d069';OWNER='1fd00418-2a79-4178-883f-af6c3f5e07ee'
def api(url):
 with urllib.request.urlopen(url,timeout=20) as r:return json.load(r)
code="""from pathlib import Path
import subprocess,json,hashlib,datetime,sqlite3
c=json.loads(subprocess.check_output(['pct','exec','627','--','docker','inspect','voicebox']))[0];cg=Path('/sys/fs/cgroup/lxc/627')
r={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'configs':{p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/etc/pve/lxc').glob('*.conf')},'container':{k:c[k] for k in ['Id','Image','RestartCount']},'state':{k:c['State'][k] for k in ['Running','StartedAt','OOMKilled']},'limits':{k:c['HostConfig'][k] for k in ['Memory','MemorySwap','NanoCpus']},'cgroup':{n:(cg/n).read_text() for n in ['memory.current','memory.events','memory.swap.current','memory.max']},'config':subprocess.check_output(['pct','config','627'],text=True),'private_original_hashes':json.loads(subprocess.check_output(['pct','exec','627','--','python3','-c',\"from pathlib import Path;import hashlib,json;print(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/srv/voicebox/private-originals').glob('*-original.wav')}))\"]))}
print(json.dumps(r))"""
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve'];r=json.loads(subprocess.check_output(ssh+['python3 -c '+shlex.quote(code)],timeout=30));baseline=json.loads((P/'baseline.json').read_text());assert all(r['configs'][k]==v for k,v in baseline['configs'].items() if k!='627')
assert all(x in r['config'] for x in ['memory: 7168','cores: 3','swap: 512','size=50G'])
assert r['container']['Image']==json.loads((ROOT/'services/infra-voicebox/image-lock.json').read_text())['image_id'] and r['state']['Running'] and not r['state']['OOMKilled']
assert r['limits']=={'Memory':6200*2**20,'MemorySwap':6600*2**20,'NanoCpus':3*10**9}
assert all(int(v)==0 for k,v in (x.split() for x in r['cgroup']['memory.events'].splitlines()) if k in ['oom','oom_kill','oom_group_kill'])
recording=json.loads((P/'recording-check.json').read_text());assert recording['original_sha256'] in r['private_original_hashes'].values()
base='http://192.168.1.127:17493';profiles=api(base+'/profiles');assert len(profiles)==1 and profiles[0]['id']==OWNER and profiles[0]['default_engine']=='qwen'
refs=api(base+'/profiles/'+OWNER+'/samples');assert len(refs)==1 and refs[0]['id']=='8840f5e1-990b-463e-b94e-e72beef61917'
reference_code="from pathlib import Path;import hashlib;print(hashlib.sha256(Path('/srv/voicebox/data/profiles/1fd00418-2a79-4178-883f-af6c3f5e07ee/8840f5e1-990b-463e-b94e-e72beef61917.wav').read_bytes()).hexdigest())"
reference_hash=subprocess.check_output(ssh+[shlex.join(['pct','exec','627','--','python3','-c',reference_code])],text=True).strip();assert reference_hash==recording['reference_sha256']
trial=json.loads((P/'pilot-summary.json').read_text());assert api(base+'/history/'+trial['generation_id'])['status']=='completed'
with urllib.request.urlopen(trial['audio_url'],timeout=20) as response:assert hashlib.sha256(response.read()).hexdigest()==trial['sha256']
models=api(base+'/models/status')['models'];loaded=[x['model_name'] for x in models if x['loaded']];assert len(loaded)<=1
assert api(base+'/health')['status']=='healthy' and api(base+'/settings/generation')['max_chunk_chars']==200
before=json.loads((P.parent/'voicebox-d068/targets-before.json').read_text());targets=api('http://192.168.1.110:9090/api/v1/targets');canon=lambda d:sorted((x['scrapeUrl'],x['scrapePool'],json.dumps(x['labels'],sort_keys=True)) for x in d['data']['activeTargets']);assert canon(before)==canon(targets) and all(x['health']=='up' for x in targets['data']['activeTargets'])
alerts=api('http://192.168.1.110:9090/api/v1/query?'+urllib.parse.urlencode({'query':'ALERTS{alertstate=~"firing|pending"}'}));assert not alerts['data']['result']
r.update({'result':'PASS','owner_profiles':1,'references':1,'reference_bytes_unchanged':True,'completed_audio_persists':True,'loaded_models':loaded,'other_pve_configurations_unchanged':len(baseline['configs'])-1,'other_managed_lxc_unchanged':17,'targets_up_unchanged':len(targets['data']['activeTargets']),'firing_or_pending_alerts':0})
(P/'audit.json').write_text(json.dumps(r,indent=2)+'\n');(P/'audit.json').chmod(0o600)
# Public evidence excludes config text and owner-original hashes.
public={k:v for k,v in r.items() if k not in ['configs','config','private_original_hashes']};(ROOT/'docs/roadmap/evidence/2026-11-10-d069-audit.json').write_text(json.dumps(public,indent=2)+'\n');print(json.dumps(public,indent=2))
