#!/usr/bin/env python3
"""PVE:300s sin inferencia ni llamadas al modelo; prueba PID/pesos residentes."""
import sys,importlib.util,pathlib,json,time,datetime,subprocess
sys.argv=['validate-api.py','library'];sp=importlib.util.spec_from_file_location('api','/root/ia-local/validate-api.py');api=importlib.util.module_from_spec(sp);sp.loader.exec_module(api)
wall_start=int(time.time());start=time.monotonic();samples=[];identity=None
for i in range(6):
 while time.monotonic()<start+i*60:time.sleep(min(1,start+i*60-time.monotonic()))
 m=api.memory();model_procs=[p for p in m['processes'] if p['model_files']];assert len(model_procs)==1 and model_procs[0]['model_files']==['gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf'],'Gemma not resident'
 if identity is None:identity=model_procs[0]['pid']
 assert model_procs[0]['pid']==identity,'Model PID changed during idle';assert max(m['ct']['630']['resident_tasks'],sum(p['rss'] for p in m['processes']),sum(p.get('hwm',p['rss']) for p in m['processes']))<.9*m['ct']['630']['max']
 samples.append({'elapsed_s':time.monotonic()-start,**m});print('idle',i*60,'s Gemma PID',identity,'RSSGiB',round(model_procs[0]['rss']/1024**3,3),flush=True)
wall_end=int(time.time());logs=subprocess.check_output(['pct','exec','630','--','journalctl','-u','llama-server','--since','@'+str(wall_start),'--until','@'+str(wall_end),'--no-pager','-o','cat'],text=True);requests=logs.count('processing task,');assert requests==0,'Idle window contains inference requests'
d={'inference_requests_in_journal':requests,'result':'PASS','duration_s':time.monotonic()-start,'same_model_pid':True,'no_model_requests_during_interval':True,'samples':samples};path=pathlib.Path('/root/ia-local/latency/idle-residency.json');path.write_text(json.dumps(d,indent=2)+'\n')
