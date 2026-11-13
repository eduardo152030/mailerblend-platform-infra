"""PVE read-only D084 checks. Never load models, submit jobs or restart services."""
from pathlib import Path
import json,subprocess,hashlib,time,datetime
APP='sha256:09774c5b7c535185c901557ddb6c69a4f8bb38ceff2c6998e19bab403b8e94ea'
WORKER='sha256:bcc5c14f88064ffa76f813d788d183918b208deba45075d8118a2b07c60c248b'
def call(*args):return subprocess.check_output(args,text=True,timeout=30)
assert call('pct','status','627').strip()=='status: running'
cfg=dict(x.split(': ',1) for x in call('pct','config','627').splitlines() if ': ' in x)
assert cfg['memory']=='15360' and cfg['cores']=='3' and cfg['swap']=='2048' and cfg['rootfs'] in ['local-lvm:vm-627-disk-0,size=50G','local-lvm:vm-627-disk-0,size=100G']
assert call('systemctl','is-active','voicebox-qwen-627.service').strip()=='active'
c=json.loads(call('pct','exec','627','--','docker','inspect','voicebox'))[0];assert c['Image']==APP and c['State']['Health']['Status']=='healthy'
assert c['HostConfig']['Memory']==6200*2**20 and c['HostConfig']['MemorySwap']==6600*2**20 and c['HostConfig']['NanoCpus']==3*10**9
assert json.loads(call('pct','exec','627','--','docker','image','inspect',WORKER))[0]['Id']==WORKER
pid=call('lxc-info','-n','627','-pH').strip();root=Path('/proc',pid,'root');jobs=root/'srv/voicebox/qwen-worker/jobs'
assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in jobs.glob('*/state.json'))
checks={}
for ident in ['7f348e9777214f4e827dcf7e1458c045','baa61a95c7b445248229aa697b941710']:
 p=jobs/ident/'checkpoint';m=json.loads((p/'manifest.json').read_text());commit=json.loads((p/'COMMITTED.json').read_text());assert hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest()==commit['manifest_sha256'];assert hashlib.sha256((p/'codes.npy').read_bytes()).hexdigest()==m['codes']['sha256'];assert m['generation']['eos_emitted'];checks[ident]={'integrity':True,'shape':m['codes']['shape'],'eos':True}
h=json.loads((jobs/'agent-heartbeat.json').read_text());assert time.time()-h['timestamp']<8
src=root/'srv/voicebox/qwen-worker/src';hashes={n:hashlib.sha256((src/n).read_bytes()).hexdigest() for n in ['worker.py','runtime.py','checkpoint.py']}
controller={n:hashlib.sha256((Path('/opt/voicebox-qwen-627')/n).read_bytes()).hexdigest() for n in ['agent.py','supervise.py','guards.py']}
model=root/'srv/voicebox/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base/snapshots/5d83992436eae1d760afd27aff78a71d676296fc'
assert (model/'config.json').is_file() and (model/'model.safetensors').stat().st_size>10**9 and (model/'speech_tokenizer/model.safetensors').stat().st_size>10**8
print(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ct_running':True,'resources':{k:cfg[k] for k in ['memory','cores','swap','rootfs']},'app_image':APP,'worker_image':WORKER,'app_id':c['Id'],'started_at':c['State']['StartedAt'],'restart_count':c['RestartCount'],'healthy':True,'agent_active':True,'no_active_inference':True,'checkpoints':checks,'worker_source_hashes':hashes,'controller_hashes':controller,'model_available':True,'no_mutations':True}))
