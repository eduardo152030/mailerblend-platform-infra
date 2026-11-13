#!/usr/bin/env python3
"""PVE: cadena RAG real+STT concurrentes, guarda host y observación de ambosCT."""
import pathlib,subprocess,sys,importlib.util,json,time,datetime
sys.argv=['validate-api.py','library'];spec=importlib.util.spec_from_file_location('ia_api','/root/ia-local/validate-api.py');api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
api.unload();api.guard('RAG-Gemma-con-STT')
root=pathlib.Path('/root/ia-local');logs={};procs={}
for name,args in {'rag':['pct','exec','631','--','python3','/root/webui-check.py','rag-chat'],'stt':['pct','exec','631','--','env','IA_RESULT_PATH=/root/ia-webui-stt-final.json','python3','/root/webui-check.py','stt']}.items():
 logs[name]=(root/('concurrent-'+name+'.log')).open('w');procs[name]=subprocess.Popen(args,stdout=logs[name],stderr=subprocess.STDOUT)
samples=[];anomalies=[]
while True:
 m=api.memory();samples.append(m)
 if len({f for p in m['processes'] for f in p['model_files']})>1:anomalies.append('dosmodelos')
 if max(m['ct']['630']['resident_tasks'],sum(p['rss'] for p in m['processes']))>0.9*m['ct']['630']['max']:anomalies.append('630>90%')
 if anomalies:
  subprocess.run(['pct','exec','630','--','systemctl','stop','llama-server'],capture_output=True)
  for p in procs.values():p.terminate()
  break
 if all(p.poll() is not None for p in procs.values()):break
 time.sleep(1)
for name,p in procs.items():p.wait();logs[name].close()
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncodes':{k:p.returncode for k,p in procs.items()},'anomalies':anomalies,'samples':samples}
(root/'rag-stt-concurrent.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'returncodes':result['returncodes'],'anomalies':anomalies,'ct631_peak_working_gib':max(s['ct']['631']['working_set'] for s in samples)/1024**3,'ct631_peak_resident_gib':max(s['ct']['631']['resident_tasks'] for s in samples)/1024**3}),flush=True)
for name in procs:print(name,(root/('concurrent-'+name+'.log')).read_text()[-1500:],flush=True)
if anomalies or any(p.returncode for p in procs.values()):raise SystemExit(1)
