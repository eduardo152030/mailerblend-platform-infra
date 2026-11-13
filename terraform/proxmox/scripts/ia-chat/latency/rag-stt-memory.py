#!/usr/bin/env python3
"""PVE: RAG+STT concurrentes de fixture; mide eventos por diferencia, RAM6314096."""
import pathlib,subprocess,sys,importlib.util,time,json
sys.argv=['validate-api.py','library'];sp=importlib.util.spec_from_file_location('api','/root/ia-local/validate-api.py');api=importlib.util.module_from_spec(sp);sp.loader.exec_module(api)
root=pathlib.Path('/root/ia-local/latency');cg=pathlib.Path('/sys/fs/cgroup/lxc/631');assert int((cg/'memory.max').read_text())==4096*1024**2
before=dict((k,int(v)) for k,v in (l.split() for l in (cg/'memory.events').read_text().splitlines()));api.unload();api.guard('latency-RAG-STT4096');processes={};files={}
for name in ['rag','stt']:
 args=['pct','exec','631','--','env','IA_RESULT_PATH=/root/ia-latency-'+name+'.json','python3','/root/webui-check.py','rag-chat' if name=='rag' else 'stt'];files[name]=(root/('memory-'+name+'.log')).open('w');processes[name]=subprocess.Popen(args,stdout=files[name],stderr=subprocess.STDOUT)
samples=[];violations=[]
while any(p.poll() is None for p in processes.values()):
 m=api.memory();samples.append(m)
 if max(m['ct']['630']['resident_tasks'],sum(p['rss'] for p in m['processes']),sum(p.get('hwm',p['rss']) for p in m['processes']))>=.9*m['ct']['630']['max']:
  violations.append('630>=90%');subprocess.run(['pct','exec','630','--','systemctl','stop','llama-server'],capture_output=True)
  for p in processes.values():p.terminate()
  break
 time.sleep(.5)
for n,p in processes.items():p.wait();files[n].close()
after=dict((k,int(v)) for k,v in (l.split() for l in (cg/'memory.events').read_text().splitlines()));delta={k:after[k]-v for k,v in before.items()};d={'before':before,'after':after,'delta':delta,'returncodes':{n:p.returncode for n,p in processes.items()},'violations':violations,'samples':samples};(root/'rag-stt-memory.json').write_text(json.dumps(d,indent=2)+'\n')
assert not violations and delta['oom']==0 and delta['oom_kill']==0,'HALT memory guard'
print(json.dumps({'events_delta':delta,'returncodes':d['returncodes'],'peak_resident631_gib':max(s['ct']['631']['resident_tasks'] for s in samples)/1024**3,'peak_working631_gib':max(s['ct']['631']['working_set'] for s in samples)/1024**3}))
