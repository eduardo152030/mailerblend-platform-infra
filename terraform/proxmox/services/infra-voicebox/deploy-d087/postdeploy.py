"""PVE read-only deployment gate. No generation, profile edit or model loading."""
from pathlib import Path
import json,subprocess,urllib.request,urllib.error,time,hashlib
APP='sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386'
def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=30)
def get(path):return json.load(urllib.request.urlopen('http://192.168.1.127:17493'+path,timeout=15))
c=json.loads(ct('docker','inspect','voicebox'))[0];assert c['Image']==APP and c['State']['Health']['Status']=='healthy'
assert c['Config']['User']=='999:999' and not c['HostConfig']['Privileged'] and not c['HostConfig']['CapAdd']
s=dict(l.split(':',1) for l in ct('docker','exec','voicebox','cat','/proc/1/status').splitlines() if ':' in l)
assert s['Uid'].split()==['999']*4 and s['Gid'].split()==['999']*4 and int(s['CapEff'],16)==0 and int(s['CapPrm'],16)==0
assert get('/health')['status']=='healthy' and not get('/health')['model_loaded']
caps=get('/tts-capabilities')
for e,n in [('qwen',1200),('chatterbox',240)]:assert caps[e]['ready'] and caps[e]['languages']==['es','en'] and caps[e]['max_chars']==n
history=get('/history');assert 'baa61a95-c7b4-4524-8229-aa697b941710' in json.dumps(history)
presets=get('/effects/presets');assert {'Robotic','Radio','Echo Chamber','Deep Voice'}<={p['name'] for p in presets}
# Nonexistent ID exercises cancellation routing without changing a real job.
request=urllib.request.Request('http://192.168.1.127:17493/generate/00000000-0000-0000-0000-000000000000/cancel',data=b'',method='POST')
try:urllib.request.urlopen(request,timeout=10);raise AssertionError('Expected404 for unknown generation')
except urllib.error.HTTPError as exc:assert exc.code==404
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');jobs=root/'srv/voicebox/qwen-worker/jobs'
assert not any(json.loads(p.read_text()).get('status') in ['queued','running'] for p in jobs.glob('*/state.json'))
assert not any(n.startswith(('qwen-','chatterbox-')) for n in ct('docker','ps','--format','{{.Names}}').splitlines())
heartbeat=json.loads((jobs/'agent-heartbeat.json').read_text());assert heartbeat['status']=='healthy' and time.time()-heartbeat['timestamp']<8 and heartbeat['chatterbox']['ready']
cg=Path('/sys/fs/cgroup/lxc/627');assert int((cg/'memory.max').read_text())==20*2**30 and int((cg/'memory.swap.max').read_text())==2*2**30
print(json.dumps({'result':'PASS','image':APP,'uid':999,'gid':999,'cap_eff':s['CapEff'].strip(),'cap_prm':s['CapPrm'].strip(),'healthy':True,'models_loaded_in_app':False,'capabilities':caps,'history_accessible':True,'effects_available_without_applying':sorted(p['name'] for p in presets if p['name'] in ['Robotic','Radio','Echo Chamber','Deep Voice']),'cancel_route_unknown_id':404,'agent_healthy':True,'no_active_inference':True,'resources_unchanged':True}))
