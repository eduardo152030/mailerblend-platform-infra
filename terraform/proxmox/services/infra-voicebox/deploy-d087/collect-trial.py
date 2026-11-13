"""PVE read-only checkpoint/WAV/resource evidence for exactly one D087 trial."""
from pathlib import Path
import argparse,hashlib,json,subprocess,datetime
p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--trial',choices=['A','B','C'],required=True);a=p.parse_args()
import uuid
ident=uuid.UUID(a.id).hex
pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');job=root/'srv/voicebox/qwen-worker/jobs'/ident
state=json.loads((job/'state.json').read_text());result={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'trial':a.trial,'id':a.id,'state':state,'success':state['status']=='completed','stages':{}}
for name in ['talker','decoder','chatterbox']:
 f=job/(name+'-supervisor.json')
 if f.is_file():
  r=json.loads(f.read_text());measurements=r.get('measurements',[]);summary={'success':r.get('success'),'error':r.get('error'),'elapsed_total':r.get('elapsed_total'),'worker_result':r.get('worker_result'),'processes_released':r.get('processes_released') or (r.get('worker_cgroup_empty') and r.get('container_state',{}).get('Pid')==0)}
  if measurements and any('worker_current' in m for m in measurements):
   peak=max((m for m in measurements if 'worker_current' in m),key=lambda m:m['worker_current'])
   summary['worker_peak_sample']={k:peak[k] for k in ['at_utc','worker_current','rss_bytes','ct_current','worker_stat','worker_events'] if k in peak}
  for key in ['ct_current','ct_swap','host_available','worker_current','rss_bytes','ct_psi_full_avg10','host_psi_full_avg10']:
   values=[m[key] for m in measurements if key in m]
   if values:summary[key+('_min' if key=='host_available' else '_max')]=(min(values) if key=='host_available' else max(values))
  for group,keys in [('ct_stat',['anon','file','kernel']),('worker_stat',['anon','file','kernel']),('worker_cpu',['usage_usec','user_usec','system_usec']),('ct_events',['oom','oom_kill']),('worker_events',['oom','oom_kill'])]:
   for key in keys:
    values=[m[group][key] for m in measurements if key in m.get(group,{})]
    if values:summary[group+'_'+key+'_max']=max(values)
  if measurements:
   first,last=measurements[0],measurements[-1]
   summary['ct_cpu_delta_usec']=last['ct_cpu']['usage_usec']-first['ct_cpu']['usage_usec']
   summary['ct_swap_growth_bytes']=max(m['ct_swap'] for m in measurements)-r.get('baseline',first)['ct_swap']
   summary['ct_events_delta']={k:last['ct_events'][k]-r.get('baseline',first)['ct_events'][k] for k in ['oom','oom_kill']}
   summary['host_oom_delta']=last['host_oom']-r.get('baseline',first)['host_oom']
  result['stages'][name]=summary
cp=job/'checkpoint'
if (cp/'COMMITTED.json').exists():
 manifest=(cp/'manifest.json').read_bytes();meta=json.loads(manifest);commit=json.loads((cp/'COMMITTED.json').read_text());assert hashlib.sha256(manifest).hexdigest()==commit['manifest_sha256']
 assert hashlib.sha256((cp/'codes.npy').read_bytes()).hexdigest()==meta['codes']['sha256']
 result['checkpoint']={'integrity':True,'shape':meta['codes']['shape'],'eos':meta['generation']['eos_emitted'],'language':meta['generation'].get('language'),'generation':meta['generation']}
else:result['checkpoint']={'exists':False}
if (job/'events.jsonl').exists():result['events']=[json.loads(line) for line in (job/'events.jsonl').read_text().splitlines()]
names=subprocess.check_output(['pct','exec','627','--','docker','ps','--format','{{.Names}}'],text=True).splitlines();result['no_active_inference']=not any(n.startswith(('qwen-','chatterbox-')) for n in names)
print(json.dumps(result))
