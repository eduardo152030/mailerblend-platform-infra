#!/usr/bin/env python3
"""PVE: TTFT con3000 tokens exactos en /completion, sin caché; un modelo a la vez."""
import pathlib,subprocess,json,time,urllib.request,sys,importlib.util,threading
root=pathlib.Path('/root/ia-local');sys.argv_backup=list(sys.argv);label=sys.argv[1];model=sys.argv[2] if len(sys.argv)>2 else 'gemma-4-26b'
sys.argv=['validate-api.py','library'];sp=importlib.util.spec_from_file_location('api',root/'validate-api.py');api=importlib.util.module_from_spec(sp);sp.loader.exec_module(api)
key=subprocess.check_output(['pct','exec','630','--','cat','/etc/llama/api.key'],text=True).strip();base='http://192.168.1.67:8080'
def call(path,data):
 req=urllib.request.Request(base+path,data=json.dumps({'model':model,**data}).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 return urllib.request.urlopen(req,timeout=1800)
with call('/tokenize',{'content':'dato '*4000}) as response:tokens=json.load(response)['tokens'][:3000]
assert len(tokens)==3000
start=time.monotonic();first=None;last={};samples=[];text='';stop=threading.Event();violations=[]
def watch():
 while not stop.is_set():
  m=api.memory();samples.append(m)
  if max(m['ct']['630']['resident_tasks'],sum(p['rss'] for p in m['processes']),sum(p.get('hwm',p['rss']) for p in m['processes']))>=.9*m['ct']['630']['max']:
   violations.append('RSS/resident>=90%');subprocess.run(['pct','exec','630','--','systemctl','stop','llama-server'],capture_output=True);return
  stop.wait(.5)
thread=threading.Thread(target=watch,daemon=True);thread.start()
error=None
try:
 with call('/completion',{'prompt':tokens,'n_predict':16,'stream':True,'cache_prompt':False,'temperature':0}) as response:
  for line in response:
   line=line.decode().strip()
   if not line.startswith('data: '):continue
   d=json.loads(line[6:]);content=d.get('content','')
   if content and first is None:first=time.monotonic()-start
   text+=content;last=d
except Exception as exc:error=type(exc).__name__
finally:stop.set();thread.join()
result={'label':label,'model':model,'prompt_tokens':3000,'ttft_s':first,'elapsed_s':time.monotonic()-start,'timings':last.get('timings'),'text':text,'memory':samples,'violations':violations,'error':error};path=root/'latency'/str(label+'.json');path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='memory'}))

assert not violations and error is None and first is not None,(violations,error)
