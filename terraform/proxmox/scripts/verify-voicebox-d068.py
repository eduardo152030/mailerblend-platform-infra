#!/usr/bin/env python3
"""Read-only D068 audit: actual PVE resources, image, preserved profiles and monitoring."""
import json,hashlib,shlex,subprocess,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/mailerblend-recovery/voicebox-d068';SSH=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
code="""from pathlib import Path
import subprocess,json,hashlib,re,datetime
configs={p.stem:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/etc/pve/lxc').glob('*.conf')}
cfg=subprocess.check_output(['pct','config','627'],text=True);r={k:re.search('^'+k+': (.*)$',cfg,re.M)[1] for k in ['memory','swap','cores','rootfs']}
c=json.loads(subprocess.check_output(['pct','exec','627','--','docker','inspect','voicebox']))[0]
logs=subprocess.check_output(['journalctl','-k','--since','2026-11-10 14:31:19 UTC','--no-pager','-o','cat'],text=True);oom=[l for l in logs.splitlines() if re.search(r'oom-kill|Out of memory|Killed process',l,re.I)]
p=Path('/sys/fs/cgroup/lxc/627');cg={n:(p/n).read_text() for n in ['memory.current','memory.peak','memory.swap.current','memory.events','memory.max']}
uptime=subprocess.check_output(['pct','exec','627','--','cat','/proc/uptime'],text=True).split()[0]
print(json.dumps({'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'resources':r,'config_hashes':configs,'kernel_oom_records':oom,'cgroup':cg,'uptime_seconds':int(float(uptime)),'container':{'id':c['Id'],'image':c['Image'],'running':c['State']['Running'],'oom_killed':c['State']['OOMKilled'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'memory_limit':c['HostConfig']['Memory'],'memory_swap_limit':c['HostConfig']['MemorySwap'],'nano_cpus':c['HostConfig']['NanoCpus']},'host_pressure':Path('/proc/pressure/memory').read_text()}))"""
d=json.loads(subprocess.check_output(SSH+['python3 -'],input=code.encode(),timeout=60));before=json.loads((P/'before.json').read_text());lock=json.loads((ROOT/'services/infra-voicebox/image-lock.json').read_text())
assert d['resources']=={'memory':'7168','swap':'512','cores':'3','rootfs':'local-lvm:vm-627-disk-0,size=50G'}
assert all(d['config_hashes'][k]==v for k,v in before['config_hashes'].items() if k!='627')
assert d['container']['image']==lock['image_id'] and d['container']['running'] and not d['container']['oom_killed']
assert d['container']['memory_limit']==6200*2**20 and d['container']['memory_swap_limit']==6600*2**20 and d['container']['nano_cpus']==3*10**9
assert not d['kernel_oom_records'] and all(int(v)==0 for k,v in (x.split() for x in d['cgroup']['memory.events'].splitlines()) if k in ['oom','oom_kill','oom_group_kill'])
def get(url):
 with urllib.request.urlopen(url,timeout=20) as r:return json.load(r)
profiles=get('http://192.168.1.127:17493/profiles');original=json.loads((P/'profiles-before.json').read_text());fields=['id','name','description','language','voice_type','preset_engine','preset_voice_id','default_engine','created_at','updated_at']
for old in original:
 now=next(x for x in profiles if x['id']==old['id']);assert all(now.get(k)==old.get(k) for k in fields),'Preexisting profile modified'
assert len(profiles)==8 and not any(x['name']=='Eduardo — Personal Voice' for x in profiles)
loaded=[x['model_name'] for x in get('http://192.168.1.127:17493/models/status')['models'] if x['loaded']];assert loaded==['kokoro']
# User-protected old sample remains retrievable and byte-identical.
with urllib.request.urlopen('http://192.168.1.127:17493/audio/597aaabb-5688-4df1-bd1c-18d9c6144afd',timeout=20) as response:old_audio=response.read()
assert hashlib.sha256(old_audio).hexdigest()=='29b727abe8f8929c5c5dee528110ef72b932d5917a736078cc1660ce352f051f'
targets=get('http://192.168.1.110:9090/api/v1/targets');canon=lambda x:sorted((t['scrapeUrl'],t['scrapePool'],json.dumps(t['labels'],sort_keys=True)) for t in x['data']['activeTargets'])
assert canon(targets)==canon(json.loads((P/'targets-before.json').read_text())) and all(t['health']=='up' for t in targets['data']['activeTargets'])
alerts=get('http://192.168.1.110:9090/api/v1/query?'+urllib.parse.urlencode({'query':'ALERTS{alertstate=~"firing|pending"}'}));assert not alerts['data']['result']
d.update({'result':'PASS','other_pve_config_hashes_unchanged':len(before['config_hashes'])-1,'other_managed_lxc_unchanged':17,'monitoring_targets_identical_and_up':len(targets['data']['activeTargets']),'preexisting_profiles_preserved':len(original),'profiles_total':len(profiles),'personal_profile_created':False,'alex_old_sample_preserved':True,'loaded_models':loaded,'firing_or_pending_alerts':0})
(P/'audit.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items() if k!='config_hashes'},indent=2))
